// API utility functions for the customer support chatbot

import { ChatRequest, ChatResponse, Customer, Store, Location, HealthCheck, APIError } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // Use default error message if JSON parsing fails
        }
        
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  // Chat endpoint
  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('/api/v1/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Customer profile endpoint
  async getCustomerProfile(customerId: string): Promise<Customer> {
    return this.request<Customer>(`/api/v1/customers/${customerId}`);
  }

  // Nearby stores endpoint
  async getNearbyStores(
    latitude: number,
    longitude: number,
    radiusKm: number = 5,
    limit: number = 10,
    storeTypes?: string[],
    cuisineTypes?: string[]
  ): Promise<{ stores: Store[]; total_count: number; search_radius_km: number; user_location: Location }> {
    const params = new URLSearchParams({
      lat: latitude.toString(),
      lon: longitude.toString(),
      radius_km: radiusKm.toString(),
      limit: limit.toString(),
    });

    if (storeTypes && storeTypes.length > 0) {
      params.append('store_types', storeTypes.join(','));
    }

    if (cuisineTypes && cuisineTypes.length > 0) {
      params.append('cuisine_types', cuisineTypes.join(','));
    }

    return this.request<{ stores: Store[]; total_count: number; search_radius_km: number; user_location: Location }>(
      `/api/v1/stores/nearby?${params}`
    );
  }

  // Document search endpoint
  async searchDocuments(
    query: string,
    limit: number = 5
  ): Promise<{ documents: any[]; total_count: number; query: string; search_time: number }> {
    const params = new URLSearchParams({
      query,
      limit: limit.toString(),
    });

    return this.request<{ documents: any[]; total_count: number; query: string; search_time: number }>(
      `/api/v1/documents/search?${params}`
    );
  }

  // Health check endpoint
  async getHealthCheck(): Promise<HealthCheck> {
    return this.request<HealthCheck>('/api/v1/health');
  }
}

// Create singleton instance
export const apiClient = new APIClient();

// Utility functions
export const formatError = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'An unexpected error occurred';
};

export const isAPIError = (error: any): error is APIError => {
  return error && typeof error.detail === 'string';
};

// Location utilities
export const getCurrentLocation = (): Promise<Location> => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported by this browser'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
      },
      (error) => {
        reject(new Error('Unable to retrieve your location'));
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000, // 1 minute
      }
    );
  });
};

// Default Delhi location (fallback)
export const DEFAULT_LOCATION: Location = {
  latitude: 28.7041,
  longitude: 77.1025,
};

// Distance calculation utility
export const calculateDistance = (
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number => {
  const R = 6371; // Earth's radius in kilometers
  const dLat = (lat2 - lat1) * (Math.PI / 180);
  const dLon = (lon2 - lon1) * (Math.PI / 180);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) *
      Math.cos(lat2 * (Math.PI / 180)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;
  return distance;
};

// Format distance for display
export const formatDistance = (meters: number): string => {
  if (meters < 1000) {
    return `${Math.round(meters)}m`;
  }
  return `${(meters / 1000).toFixed(1)}km`;
};

// Format time for display
export const formatTime = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  }).format(date);
};

// Generate unique message ID
export const generateMessageId = (): string => {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};