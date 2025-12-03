import React from 'react';
import { MessageSquare, MapPin, User, Zap } from 'lucide-react';
import { ChatInterfaceProps } from '@/types';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import StoreCard from './StoreCard';

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  nearbyStores,
  onSendMessage,
  isLoading,
  error,
}) => {
  const [selectedStore, setSelectedStore] = React.useState(null);

  const handleStoreClick = (store: any) => {
    setSelectedStore(store);
    // Could open a modal or navigate to store details
    console.log('Store clicked:', store);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Side - Chat (70%) */}
      <div className="flex-1 flex flex-col bg-white border-r border-gray-200" style={{ width: '70%' }}>
        {/* Chat Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-100 rounded-lg">
              <MessageSquare className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h1 className="font-semibold text-gray-900">Foodie Stoopie</h1>
              <p className="text-sm text-gray-600">Your personal diner assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span className="text-sm text-gray-600">Online</span>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mx-4 mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-red-400 rounded-full"></div>
              <span className="text-sm text-red-700">{error}</span>
            </div>
          </div>
        )}

        {/* Messages Area */}
        <MessageList messages={messages} isLoading={isLoading} />

        {/* Message Input */}
        <MessageInput
          onSendMessage={onSendMessage}
          isLoading={isLoading}
          placeholder="Ask about drinks, stores, or place an order..."
        />
      </div>

      {/* Right Side - Nearby Stores (30%) */}
      <div className="w-80 flex flex-col bg-gray-50">
        {/* Stores Header */}
        <div className="p-4 border-b border-gray-200 bg-white">
          <div className="flex items-center gap-2 mb-2">
            <MapPin className="w-5 h-5 text-primary-600" />
            <h2 className="font-semibold text-gray-900">Nearby Stores</h2>
          </div>
          {nearbyStores.length > 0 && (
            <p className="text-sm text-gray-600">
              {nearbyStores.length} stores found near you
            </p>
          )}
        </div>

        {/* Stores List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
          {nearbyStores.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-12 h-12 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                <MapPin className="w-6 h-6 text-gray-400" />
              </div>
              <h3 className="font-medium text-gray-900 mb-2">No stores found</h3>
              <p className="text-sm text-gray-600">
                We couldn't find any Food Place stores near your location. 
                Try searching in a different area.
              </p>
            </div>
          ) : (
            nearbyStores.map((store) => (
              <StoreCard
                key={store.store_id}
                store={store}
                onStoreClick={handleStoreClick}
              />
            ))
          )}
        </div>

        {/* Quick Actions */}
        <div className="p-4 border-t border-gray-200 bg-white">
          <div className="space-y-2">
            <button className="w-full btn-secondary text-left flex items-center gap-2">
              <User className="w-4 h-4" />
              <span className="text-sm">View Profile</span>
            </button>
            <button className="w-full btn-secondary text-left flex items-center gap-2">
              <Zap className="w-4 h-4" />
              <span className="text-sm">Quick Reorder</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;