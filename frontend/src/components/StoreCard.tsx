import React from 'react';
import { MapPin, Clock, Star, Phone, Tag, Coffee, UtensilsCrossed, Zap, Cookie } from 'lucide-react';
import { StoreCardProps } from '@/types';
import { formatDistance } from '@/utils/api';

const StoreCard: React.FC<StoreCardProps> = ({ store, onStoreClick }) => {
  const handleClick = () => {
    onStoreClick?.(store);
  };

  const storeStatusClass = store.is_open ? 'store-card-open' : 'store-card-closed';
  const statusColor = store.is_open ? 'text-green-600' : 'text-red-600';
  const statusText = store.is_open ? 'Open' : 'Closed';
  
  // Get appropriate icon for store type
  const getStoreIcon = (storeType: string) => {
    switch (storeType) {
      case 'cafe': return <Coffee className="w-4 h-4 text-amber-600" />;
      case 'restaurant': return <UtensilsCrossed className="w-4 h-4 text-orange-600" />;
      case 'fast_food': return <Zap className="w-4 h-4 text-red-600" />;
      case 'bakery': return <Cookie className="w-4 h-4 text-yellow-600" />;
      case 'pizza': return <UtensilsCrossed className="w-4 h-4 text-red-600" />;
      default: return <UtensilsCrossed className="w-4 h-4 text-gray-600" />;
    }
  };
  
  const formatStoreType = (type: string) => {
    return type.replace('_', ' ').split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const distance = store.distance_km || (store.distance_meters ? store.distance_meters / 1000 : 0);

  return (
    <div
      className={`store-card ${storeStatusClass} cursor-pointer`}
      onClick={handleClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            {store.store_type && getStoreIcon(store.store_type)}
            <h3 className="font-semibold text-gray-900 text-sm line-clamp-1">
              {store.name}
            </h3>
          </div>
          {store.store_type && (
            <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
              <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                {formatStoreType(store.store_type)}
              </span>
              {store.cuisine_type && (
                <span className="bg-green-100 text-green-800 px-2 py-0.5 rounded-full">
                  {formatStoreType(store.cuisine_type)}
                </span>
              )}
            </div>
          )}
          {store.address && (
            <p className="text-xs text-gray-600 mb-1 line-clamp-2">
              {store.address}
            </p>
          )}
        </div>
      </div>

      {/* Distance and Status */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1 text-xs text-gray-600">
          <MapPin className="w-3 h-3" />
          <span>{distance > 0 ? `${distance.toFixed(1)} km` : 'Distance unknown'}</span>
        </div>
        <div className={`flex items-center gap-1 text-xs font-medium ${statusColor}`}>
          <Clock className="w-3 h-3" />
          <span>{statusText}</span>
        </div>
      </div>

      {/* Opening Hours */}
      {store.opening_hours && (
        <div className="flex items-center gap-1 mb-2">
          <Clock className="w-3 h-3 text-gray-400" />
          <span className="text-xs text-gray-600">{store.opening_hours}</span>
        </div>
      )}

      {/* Promotions */}
      {store.current_promotions && store.current_promotions.length > 0 && (
        <div className="space-y-1">
          {store.current_promotions.slice(0, 2).map((promotion, index) => {
            const promoText = typeof promotion === 'string' ? promotion : 
              (promotion.title || promotion.description || 'Special Offer');
            return (
              <div key={index} className="promotion-badge">
                <Tag className="w-3 h-3 mr-1" />
                <span>{promoText}</span>
              </div>
            );
          })}
          {store.current_promotions.length > 2 && (
            <span className="text-xs text-gray-500">
              +{store.current_promotions.length - 2} more offers
            </span>
          )}
        </div>
      )}
      
      {/* Key Inventory */}
      {store.key_inventory && Object.keys(store.key_inventory).length > 0 && (
        <div className="mt-2 pt-2 border-t border-gray-100">
          <div className="text-xs text-gray-500 mb-1">Popular items:</div>
          <div className="flex flex-wrap gap-1">
            {Object.keys(store.key_inventory).slice(0, 3).map((category) => (
              <span key={category} className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">
                {formatStoreType(category)}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Contact Info */}
      {store.contact_info?.phone && (
        <div className="flex items-center gap-1 mt-2 pt-2 border-t border-gray-100">
          <Phone className="w-3 h-3 text-gray-400" />
          <span className="text-xs text-gray-600">{store.contact_info.phone}</span>
        </div>
      )}

      {/* Hover Effect Indicator */}
      <div className="mt-2 pt-2 border-t border-gray-100">
        <span className="text-xs text-primary-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
          Click for details →
        </span>
      </div>
    </div>
  );
};

export default StoreCard;