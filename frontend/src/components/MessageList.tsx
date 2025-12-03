import React from 'react';
import { Clock, Loader2 } from 'lucide-react';
import { MessageListProps, Message } from '@/types';
import { formatTime } from '@/utils/api';

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const renderMessage = (message: Message) => (
    <div
      key={message.id}
      className={`flex flex-col gap-1 animate-slide-up ${
        message.sender === 'user' ? 'items-end' : 'items-start'
      }`}
    >
      <div
        className={`${
          message.sender === 'user' ? 'message-user' : 'message-bot'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
      <div className="flex items-center gap-2 text-xs text-gray-500 px-1">
        <Clock className="w-3 h-3" />
        <span>{formatTime(message.timestamp)}</span>
        {message.processing_time && message.sender === 'bot' && (
          <span className="text-gray-400">
            • {message.processing_time.toFixed(2)}s
          </span>
        )}
      </div>
    </div>
  );

  const renderLoadingMessage = () => (
    <div className="flex flex-col gap-1 items-start animate-fade-in">
      <div className="message-bot">
        <div className="flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
          <span className="text-gray-600">Thinking...</span>
        </div>
      </div>
      <div className="flex items-center gap-2 text-xs text-gray-500 px-1">
        <Clock className="w-3 h-3" />
        <span>Now</span>
      </div>
    </div>
  );

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
      {/* Welcome message */}
      {messages.length === 0 && !isLoading && (
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="bg-primary-50 border border-primary-200 rounded-lg p-6 max-w-md">
            <h3 className="text-lg font-semibold text-primary-800 mb-2">
              Welcome to Foodie Stoopie
            </h3>
            <p className="text-primary-700">
              Hi! I'm your personal coffee assistant. Ask me about our drinks, 
              find nearby stores, or get help with your order!
            </p>
          </div>
        </div>
      )}

      {/* Messages */}
      {messages.map(renderMessage)}

      {/* Loading indicator */}
      {isLoading && renderLoadingMessage()}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;