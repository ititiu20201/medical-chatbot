import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Textarea } from '@/components/ui/textarea';

const MedicalChat = () => {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      content: 'Xin chào! Tôi là trợ lý y tế ảo. Tôi có thể giúp gì cho bạn hôm nay?'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { type: 'user', content: input }]);
    setLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });

      const data = await response.json();
      
      setMessages(prev => [...prev, { type: 'bot', content: data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        type: 'error', 
        content: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.'
      }]);
    }

    setLoading(false);
    setInput('');
  };

  return (
    <div className="max-w-4xl mx-auto p-4 h-screen flex flex-col">
      <Card className="flex-1 flex flex-col overflow-hidden p-4 bg-white">
        <ScrollArea className="flex-1 pr-4" ref={scrollRef}>
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div 
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex gap-3 max-w-[80%] ${
                  message.type === 'user' ? 'flex-row-reverse' : ''
                }`}>
                  <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full border bg-background">
                    {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                  </div>
                  <div className={`rounded-lg p-3 ${
                    message.type === 'user' 
                      ? 'bg-primary text-primary-foreground' 
                      : message.type === 'error'
                      ? 'bg-destructive text-destructive-foreground'
                      : 'bg-muted'
                  }`}>
                    {message.content}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full border bg-background">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div className="flex items-center rounded-lg p-3 bg-muted">
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <form onSubmit={handleSubmit} className="mt-4 flex gap-4">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Nhập tin nhắn của bạn..."
            className="min-h-[60px]"
          />
          <Button type="submit" size="icon" disabled={loading}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </Card>
    </div>
  );
};

export default MedicalChat;