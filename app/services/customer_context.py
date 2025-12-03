"""
Customer context retrieval service for hyper-personalized chatbot responses.
Provides customer data, location context, and environmental factors.
"""
import asyncio
import math
from datetime import datetime, time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_get, cache_set
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.models import Customer, Store, Interaction

logger = get_logger(__name__)

@dataclass
class CustomerContext:
    """Customer context data structure."""
    customer_id: str
    basic_info: Dict[str, Any]
    preferences: Dict[str, Any]
    purchase_history: List[Dict[str, Any]]
    loyalty_status: Dict[str, Any]
    interaction_count: int
    last_interaction: Optional[datetime] = None

@dataclass
class LocationContext:
    """Location and store context data structure."""
    nearest_stores: List[Dict[str, Any]]
    selected_store: Optional[Dict[str, Any]]
    distance_to_nearest: float
    weather_context: Dict[str, Any]

@dataclass
class StoreInfo:
    """Store information with operational status."""
    id: str
    name: str
    latitude: float
    longitude: float
    distance_km: float
    is_open: bool
    open_hours: Dict[str, str]
    current_promotions: List[Dict[str, Any]]
    key_inventory: Dict[str, Any]

class CustomerContextService:
    """Service for retrieving comprehensive customer context."""
    
    def __init__(self):
        """Initialize the customer context service."""
        self.cache_ttl = 1800  # 30 minutes
    
    async def get_customer_context(self, customer_id: str) -> Optional[CustomerContext]:
        """
        Retrieve comprehensive customer context.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            CustomerContext object or None if customer not found
        """
        # Check cache first
        cache_key = f"customer_context:{customer_id}"
        cached_data = await cache_get(cache_key)
        
        if cached_data:
            logger.info("Customer context served from cache", 
                       extra={"customer_id": customer_id})
            return CustomerContext(**cached_data)
        
        # Fetch from database
        async for db in get_db():
            try:
                # Get customer basic info
                customer_result = await db.execute(
                    select(Customer).where(Customer.id == customer_id)
                )
                customer = customer_result.scalar_one_or_none()
                
                if not customer:
                    logger.warning("Customer not found", 
                                 extra={"customer_id": customer_id})
                    return None
                
                # Get interaction statistics
                interaction_stats = await db.execute(
                    select(
                        func.count(Interaction.id).label('interaction_count'),
                        func.max(Interaction.created_at).label('last_interaction')
                    ).where(Interaction.customer_id == customer_id)
                )
                stats = interaction_stats.first()
                
                # Get recent purchase history from stored data
                recent_purchases = customer.purchase_history[-10:] if customer.purchase_history else []
                
                # Calculate loyalty status
                loyalty_status = self._calculate_loyalty_status(customer, recent_purchases)
                
                # Build customer context
                context = CustomerContext(
                    customer_id=customer_id,
                    basic_info={
                        'name': customer.name,
                        'masked_phone': customer.masked_phone,
                        'masked_email': customer.masked_email
                    },
                    preferences={
                        'favorite_categories': customer.preferences.get('favorite_categories', ['coffee']),
                        'loyalty_tier': customer.loyalty_tier,
                        'store_format': customer.preferences.get('store_format', 'casual'),
                        'dietary_restrictions': customer.preferences.get('dietary_restrictions', []),
                        'preferred_time_slots': customer.preferences.get('preferred_time_slots', ['morning'])
                    },
                    purchase_history=recent_purchases,
                    loyalty_status=loyalty_status,
                    interaction_count=stats.interaction_count or 0,
                    last_interaction=stats.last_interaction
                )
                
                # Cache the result
                await cache_set(cache_key, asdict(context), ttl=self.cache_ttl)
                
                logger.info("Customer context retrieved from database", 
                           extra={"customer_id": customer_id, 
                                 "interaction_count": context.interaction_count})
                
                return context
                
            except Exception as e:
                logger.error(f"Failed to get customer context: {e}", 
                           extra={"customer_id": customer_id})
                return None
            finally:
                break
    
    def _calculate_loyalty_status(self, customer: Customer, purchases: List[Dict]) -> Dict[str, Any]:
        """Calculate loyalty tier status and progress."""
        total_spent = sum(purchase.get('amount', 0) for purchase in purchases)
        purchase_count = len(purchases)
        current_tier = customer.loyalty_tier
        
        # Define tier thresholds
        tier_thresholds = {
            'bronze': {'min_spent': 0, 'next_tier': 'silver', 'next_threshold': 2500},
            'silver': {'min_spent': 2500, 'next_tier': 'gold', 'next_threshold': 7500},
            'gold': {'min_spent': 7500, 'next_tier': 'platinum', 'next_threshold': 15000},
            'platinum': {'min_spent': 15000, 'next_tier': None, 'next_threshold': None}
        }
        
        tier_info = tier_thresholds.get(current_tier, tier_thresholds['bronze'])
        
        # Calculate points (₹1 = 1 point)
        total_points = int(total_spent)
        
        # Determine next reward milestone
        if current_tier == 'bronze':
            next_reward = max(0, 125 - (total_points % 125))
        elif current_tier == 'silver':
            next_reward = max(0, 125 - (total_points % 125))
        elif current_tier == 'gold':
            next_reward = max(0, 100 - (total_points % 100))
        else:  # platinum
            next_reward = max(0, 75 - (total_points % 75))
        
        return {
            'tier': current_tier,
            'total_points': total_points,
            'total_spent': total_spent,
            'purchases_count': purchase_count,
            'next_tier': tier_info['next_tier'],
            'points_to_next_tier': max(0, tier_info['next_threshold'] - total_spent) if tier_info['next_threshold'] else 0,
            'next_reward_milestone': next_reward
        }

class LocationService:
    """Service for location-based context and store information."""
    
    def __init__(self):
        """Initialize the location service."""
        self.cache_ttl = 900  # 15 minutes for location data
    
    async def get_nearest_stores(
        self, 
        latitude: float, 
        longitude: float, 
        radius_km: float = 5.0,
        limit: int = 5
    ) -> List[StoreInfo]:
        """
        Get nearest stores with operational status.
        
        Args:
            latitude: User latitude
            longitude: User longitude
            radius_km: Search radius in kilometers
            limit: Maximum number of stores
            
        Returns:
            List of StoreInfo objects sorted by distance
        """
        cache_key = f"nearest_stores:{latitude:.4f}:{longitude:.4f}:{radius_km}:{limit}"
        cached_stores = await cache_get(cache_key)
        
        if cached_stores:
            return [StoreInfo(**store) for store in cached_stores]
        
        async for db in get_db():
            try:
                # Get all stores
                result = await db.execute(select(Store))
                all_stores = result.scalars().all()
                
                # Calculate distances and filter
                nearby_stores = []
                current_time = datetime.now().time()
                
                for store in all_stores:
                    distance = self.calculate_distance(
                        latitude, longitude, store.latitude, store.longitude
                    )
                    
                    if distance <= radius_km:
                        is_open = self.is_store_open_time(store.open_hours, current_time)
                        
                        store_info = StoreInfo(
                            id=store.id,
                            name=store.name,
                            latitude=store.latitude,
                            longitude=store.longitude,
                            distance_km=round(distance, 2),
                            is_open=is_open,
                            open_hours=store.open_hours,
                            current_promotions=store.current_promotions,
                            key_inventory=self._get_key_inventory(store.inventory)
                        )
                        nearby_stores.append(store_info)
                
                # Sort by distance and apply limit
                nearby_stores.sort(key=lambda x: x.distance_km)
                nearby_stores = nearby_stores[:limit]
                
                # Cache results
                cache_data = [asdict(store) for store in nearby_stores]
                await cache_set(cache_key, cache_data, ttl=self.cache_ttl)
                
                logger.info(f"Found {len(nearby_stores)} nearby stores", 
                           extra={"latitude": latitude, "longitude": longitude})
                
                return nearby_stores
                
            except Exception as e:
                logger.error(f"Failed to get nearby stores: {e}")
                return []
            finally:
                break
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.
        
        Returns:
            Distance in kilometers
        """
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of Earth in kilometers
        r = 6371
        return c * r
    
    def is_store_open(self, store_hours: Dict[str, str], check_time: Optional[datetime] = None) -> bool:
        """Check if store is currently open."""
        if check_time is None:
            check_time = datetime.now()
        
        return self.is_store_open_time(store_hours, check_time.time())
    
    def is_store_open_time(self, store_hours: Dict[str, str], check_time: time) -> bool:
        """Check if store is open at given time."""
        day_name = datetime.now().strftime('%A').lower()
        
        if day_name not in store_hours:
            return False
        
        hours_str = store_hours[day_name]
        if hours_str.lower() == 'closed':
            return False
        
        try:
            # Parse hours like "07:00-22:00"
            start_str, end_str = hours_str.split('-')
            start_time = datetime.strptime(start_str.strip(), '%H:%M').time()
            end_time = datetime.strptime(end_str.strip(), '%H:%M').time()
            
            return start_time <= check_time <= end_time
        except (ValueError, AttributeError):
            logger.warning(f"Invalid store hours format: {hours_str}")
            return False
    
    async def get_store_inventory(self, store_id: str) -> Dict[str, Any]:
        """Get store inventory for key items."""
        cache_key = f"store_inventory:{store_id}"
        cached_inventory = await cache_get(cache_key)
        
        if cached_inventory:
            return cached_inventory
        
        async for db in get_db():
            try:
                result = await db.execute(select(Store).where(Store.id == store_id))
                store = result.scalar_one_or_none()
                
                if not store:
                    return {}
                
                key_inventory = self._get_key_inventory(store.inventory)
                await cache_set(cache_key, key_inventory, ttl=600)  # 10 minutes
                
                return key_inventory
                
            except Exception as e:
                logger.error(f"Failed to get store inventory: {e}")
                return {}
            finally:
                break
    
    def _get_key_inventory(self, full_inventory: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key inventory items for display."""
        key_items = {
            'beverages': ['hot_cocoa', 'coffee_beans', 'cold_brew'],
            'food': ['sandwiches', 'pastries', 'cookies'],
            'merchandise': ['mugs', 'tumblers']
        }
        
        key_inventory = {}
        for category, items in key_items.items():
            if category in full_inventory:
                category_data = {}
                for item in items:
                    if item in full_inventory[category]:
                        category_data[item] = full_inventory[category][item]
                if category_data:
                    key_inventory[category] = category_data
        
        return key_inventory

class WeatherService:
    """Mock weather service for hackathon purposes."""
    
    def get_weather_context(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get mock weather context based on location.
        In production, this would integrate with a weather API.
        """
        # Mock weather data based on Indian cities
        city_weather = {
            (28.6139, 77.2090): {'city': 'Delhi', 'temp': 18, 'condition': 'clear'},
            (19.0760, 72.8777): {'city': 'Mumbai', 'temp': 28, 'condition': 'humid'},
            (12.9716, 77.5946): {'city': 'Bangalore', 'temp': 22, 'condition': 'pleasant'},
            (17.3850, 78.4867): {'city': 'Hyderabad', 'temp': 25, 'condition': 'warm'},
            (18.5204, 73.8567): {'city': 'Pune', 'temp': 24, 'condition': 'mild'}
        }
        
        # Find closest city
        min_distance = float('inf')
        closest_weather = {'city': 'Unknown', 'temp': 22, 'condition': 'pleasant'}
        
        for (lat, lon), weather in city_weather.items():
            distance = math.sqrt((latitude - lat)**2 + (longitude - lon)**2)
            if distance < min_distance:
                min_distance = distance
                closest_weather = weather
        
        # Generate recommendations based on temperature
        temp = closest_weather['temp']
        if temp < 15:
            recommendations = ['Hot beverages', 'Hot chocolate', 'Warm pastries']
            weather_category = 'cold'
        elif temp > 28:
            recommendations = ['Cold beverages', 'Iced drinks', 'Fresh juices']
            weather_category = 'hot'
        else:
            recommendations = ['Any beverage', 'Seasonal specials']
            weather_category = 'pleasant'
        
        return {
            'temperature': temp,
            'condition': closest_weather['condition'],
            'city': closest_weather['city'],
            'category': weather_category,
            'recommendations': recommendations,
            'description': f"{temp}°C, {closest_weather['condition']} weather in {closest_weather['city']}"
        }

class PromptContextBuilder:
    """Builds formatted context for chat prompt injection."""
    
    def __init__(self):
        """Initialize the prompt context builder."""
        self.customer_service = CustomerContextService()
        self.location_service = LocationService()
        self.weather_service = WeatherService()
    
    async def build_context_dict(
        self, 
        customer_id: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        store_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build comprehensive context dictionary for prompt injection.
        
        Returns:
            Formatted context dict ready for prompt templates
        """
        context = {
            'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'customer_name': 'Valued Customer',
            'loyalty_tier': 'bronze',
            'favorite_categories': ['coffee', 'snacks'],
            'distance_to_store': 'nearby',
            'store_name': 'Starbucks',
            'weather': 'pleasant',
            'weather_recommendations': []
        }
        
        # Get customer context
        if customer_id:
            customer_context = await self.customer_service.get_customer_context(customer_id)
            if customer_context:
                context.update({
                    'customer_name': customer_context.basic_info['name'],
                    'loyalty_tier': customer_context.preferences['loyalty_tier'],
                    'favorite_categories': customer_context.preferences['favorite_categories'],
                    'interaction_count': customer_context.interaction_count,
                    'total_spent': customer_context.loyalty_status['total_spent'],
                    'dietary_restrictions': customer_context.preferences['dietary_restrictions']
                })
        
        # Get location context
        if latitude and longitude:
            # Get weather context
            weather_context = self.weather_service.get_weather_context(latitude, longitude)
            context.update({
                'weather': weather_context['description'],
                'weather_recommendations': weather_context['recommendations'],
                'temperature': weather_context['temperature']
            })
            
            # Get nearest stores
            nearby_stores = await self.location_service.get_nearest_stores(
                latitude, longitude, radius_km=10.0, limit=3
            )
            
            if nearby_stores:
                nearest_store = nearby_stores[0]
                context.update({
                    'distance_to_store': f"{nearest_store.distance_km} km",
                    'store_name': nearest_store.name,
                    'store_is_open': nearest_store.is_open,
                    'store_promotions': [promo['title'] for promo in nearest_store.current_promotions]
                })
        
        # Get specific store context
        if store_id:
            inventory = await self.location_service.get_store_inventory(store_id)
            context['store_inventory'] = inventory
        
        return context

# Global service instances
customer_context_service = CustomerContextService()
location_service = LocationService()
weather_service = WeatherService()
prompt_context_builder = PromptContextBuilder()

# Convenience functions
async def get_customer_context(customer_id: str) -> Optional[CustomerContext]:
    """Get customer context by ID."""
    return await customer_context_service.get_customer_context(customer_id)

async def get_nearest_stores(lat: float, lon: float, radius_km: float = 5.0) -> List[StoreInfo]:
    """Get nearest stores to location."""
    return await location_service.get_nearest_stores(lat, lon, radius_km)

async def build_prompt_context(
    customer_id: Optional[str] = None,
    latitude: Optional[float] = None, 
    longitude: Optional[float] = None,
    store_id: Optional[str] = None
) -> Dict[str, Any]:
    """Build context for prompt injection."""
    return await prompt_context_builder.build_context_dict(
        customer_id, latitude, longitude, store_id
    )