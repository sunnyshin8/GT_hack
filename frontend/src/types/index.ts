// TypeScript interfaces for the customer support chatbot

export interface Message {
  id: string;
  sender: 'user' | 'bot';
  content: string;
  timestamp: Date;
  stores?: Store[];
  processing_time?: number;
}

export interface Store {
  store_id: string;
  name: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  distance_meters: number;
  distance_km?: number;
  is_open: boolean;
  opening_hours?: string;
  current_promotions: string[];
  contact_info?: {
    phone?: string;
    email?: string;
  };
}

export interface Location {
  latitude: number;
  longitude: number;
}

export interface Customer {
  customer_id: string;
  name: string;
  preferences: string[];
  loyalty_tier: 'Bronze' | 'Silver' | 'Gold' | 'Platinum';
  total_interactions: number;
  last_interaction?: Date;
  created_at: Date;
}

export interface ChatRequest {
  customer_id: string;
  message: string;
  location?: Location;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  nearest_stores: Store[];
  suggested_action?: 'visit_store' | 'place_order' | 'check_hours' | null;
  timestamp: string;
  processing_time: number;
  sources_used: string[];
}

export interface AppState {
  messages: Message[];
  isLoading: boolean;
  nearbyStores: Store[];
  customerId: string;
  location: Location;
  error: string | null;
  customer?: Customer;
}

export interface APIError {
  detail: string;
  status_code?: number;
}

export interface HealthCheck {
  status: 'healthy' | 'unhealthy' | 'degraded';
  components: Record<string, string>;
  timestamp: string;
  version: string;
}

// Component Props
export interface ChatInterfaceProps {
  messages: Message[];
  nearbyStores: Store[];
  onSendMessage: (message: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export interface MessageInputProps {
  onSendMessage: (message: string) => Promise<void>;
  isLoading: boolean;
  placeholder?: string;
}

export interface StoreCardProps {
  store: Store;
  onStoreClick?: (store: Store) => void;
}

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export interface ErrorDisplayProps {
  error: string;
  onDismiss?: () => void;
}