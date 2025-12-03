import React, { useState, useEffect, useCallback } from 'react';
import Head from 'next/head';
import ChatInterface from '@/components/ChatInterface';
import {
  apiClient,
  generateMessageId,
  getCurrentLocation,
  DEFAULT_LOCATION,
  formatError,
} from '@/utils/api';
import { AppState, Message, ChatRequest, Location } from '@/types';

const Home: React.FC = () => {
  const [appState, setAppState] = useState<AppState>({
    messages: [],
    isLoading: false,
    nearbyStores: [],
    customerId: 'demo-user-001',
    location: DEFAULT_LOCATION,
    error: null,
  });

  // Initialize app and get customer location
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Try to get user's current location
        try {
          const location = await getCurrentLocation();
          setAppState((prev) => ({ ...prev, location }));
        } catch (err) {
          console.log('Using default location (Delhi)');
          // Use default location if geolocation fails
        }

        // Get nearby stores for initial location
        try {
          const response = await apiClient.getNearbyStores(
            appState.location.latitude,
            appState.location.longitude,
            5
          );
          setAppState((prev) => ({
            ...prev,
            nearbyStores: response.stores || [],
          }));
        } catch (err) {
          console.error('Failed to get nearby stores:', err);
        }

        // Get customer profile
        try {
          const customer = await apiClient.getCustomerProfile(appState.customerId);
          setAppState((prev) => ({ ...prev, customer }));
        } catch (err) {
          console.error('Failed to get customer profile:', err);
        }
      } catch (err) {
        setAppState((prev) => ({
          ...prev,
          error: 'Failed to initialize app',
        }));
      }
    };

    initializeApp();
  }, []);

  // Clear error message after 5 seconds
  useEffect(() => {
    if (appState.error) {
      const timer = setTimeout(() => {
        setAppState((prev) => ({ ...prev, error: null }));
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [appState.error]);

  const handleSendMessage = useCallback(
    async (messageContent: string) => {
      if (!messageContent.trim()) return;

      // Create user message
      const userMessage: Message = {
        id: generateMessageId(),
        sender: 'user',
        content: messageContent,
        timestamp: new Date(),
      };

      // Add user message to chat
      setAppState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
        isLoading: true,
        error: null,
      }));

      try {
        // Send chat request to API
        const chatRequest: ChatRequest = {
          customer_id: appState.customerId,
          message: messageContent,
          location: appState.location,
        };

        const response = await apiClient.sendChatMessage(chatRequest);

        // Create bot message
        const botMessage: Message = {
          id: generateMessageId(),
          sender: 'bot',
          content: response.response,
          timestamp: new Date(response.timestamp),
          stores: response.nearest_stores,
          processing_time: response.processing_time,
        };

        // Update state with bot response and nearby stores
        setAppState((prev) => ({
          ...prev,
          messages: [...prev.messages, botMessage],
          nearbyStores: response.nearest_stores || prev.nearbyStores,
          isLoading: false,
        }));
      } catch (err) {
        const errorMessage = formatError(err);
        setAppState((prev) => ({
          ...prev,
          messages: [
            ...prev.messages,
            {
              id: generateMessageId(),
              sender: 'bot',
              content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
              timestamp: new Date(),
            },
          ],
          isLoading: false,
          error: errorMessage,
        }));
      }
    },
    [appState.customerId, appState.location]
  );

  return (
    <>
      <Head>
        <title>Starbucks Customer Support - AI Assistant</title>
        <meta
          name="description"
          content="Get personalized support from your AI coffee assistant powered by Gemini AI"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <ChatInterface
        messages={appState.messages}
        nearbyStores={appState.nearbyStores}
        onSendMessage={handleSendMessage}
        isLoading={appState.isLoading}
        error={appState.error}
      />
    </>
  );
};

export default Home;