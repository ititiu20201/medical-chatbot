import React from 'react';
import { User, Bot } from 'lucide-react';

const ChatMessage = ({ message, isUser }) => {
  return (
    <div className={`flex w-full gap-2 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className="flex-shrink-0">
        <div className={`flex h-8 w-8 items-center justify-center rounded-full ${
          isUser ? 'bg-blue-500' : 'bg-gray-500'
        }`}>
          {isUser ? (
            <User className="h-5 w-5 text-white" />
          ) : (
            <Bot className="h-5 w-5 text-white" />
          )}
        </div>
      </div>

      {/* Message Content */}
      <div className={`flex max-w-[80%] flex-col gap-1 ${
        isUser ? 'items-end' : 'items-start'
      }`}>
        <div className={`rounded-lg px-4 py-2 ${
          isUser ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-900'
        }`}>
          <p className="text-sm">{message}</p>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;