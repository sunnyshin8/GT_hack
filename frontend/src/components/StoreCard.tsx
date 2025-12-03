import React from 'react';
import { MapPin, Clock, Star, Phone, Tag } from 'lucide-react';
import { StoreCardProps } from '@/types';
import { formatDistance } from '@/utils/api';

const StoreCard: React.FC<StoreCardProps> = ({ store, onStoreClick }) => {
  const handleClick = () => {
    onStoreClick?.(store);
  };

  const storeStatusClass = store.is_open ? 'store-card-open' : 'store-card-closed';
  const statusColor = store.is_open ? 'text-green-600' : 'text-red-600';
  const statusText = store.is_open ? 'Open' : 'Closed';

  return (
    <div
      className={`store-card ${storeStatusClass} cursor-pointer`}
      onClick={handleClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 text-sm mb-1 line-clamp-2">
            {store.name}
          </h3>
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
          <span>{formatDistance(store.distance_meters)}</span>
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
      {store.current_promotions.length > 0 && (
        <div className="space-y-1">
          {store.current_promotions.slice(0, 2).map((promotion, index) => (
            <div key={index} className="promotion-badge">
              <Tag className="w-3 h-3 mr-1" />
              <span>{promotion}</span>
            </div>
          ))}
          {store.current_promotions.length > 2 && (
            <span className="text-xs text-gray-500">
              +{store.current_promotions.length - 2} more offers
            </span>
          )}
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