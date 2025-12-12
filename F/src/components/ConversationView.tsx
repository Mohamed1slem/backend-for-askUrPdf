import { Message, Client, Document } from '@/types';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';
import { Send, Paperclip, FileText, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useState, useRef, useEffect } from 'react';

interface ConversationViewProps {
  client: Client;
  messages: Message[];
  selectedDocuments: Document[];
  aiResponse: string | null;
  onSendMessage: (content: string, attachments?: Document[]) => void;
  onRemoveDocument: (docId: string) => void;
}

export function ConversationView({
  client,
  messages,
  selectedDocuments,
  aiResponse,
  onSendMessage,
  onRemoveDocument,
}: ConversationViewProps) {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (aiResponse) {
      setInputValue(aiResponse);
    }
  }, [aiResponse]);

  const handleSend = () => {
    if (inputValue.trim() || selectedDocuments.length > 0) {
      onSendMessage(inputValue.trim(), selectedDocuments);
      setInputValue('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="p-4 border-b border-border bg-card">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
            <span className="text-primary font-semibold">
              {client.name.charAt(0)}
            </span>
          </div>
          <div>
            <h3 className="font-semibold text-foreground">{client.name}</h3>
            <p className="text-sm text-muted-foreground">{client.email}</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={message.id}
            className={cn(
              "flex animate-fade-in",
              message.sender === 'employee' ? "justify-end" : "justify-start"
            )}
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div
              className={cn(
                "max-w-[70%]",
                message.sender === 'employee'
                  ? "message-bubble-employee"
                  : "message-bubble-client"
              )}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              
              {message.attachments && message.attachments.length > 0 && (
                <div className="mt-3 space-y-2">
                  {message.attachments.map((doc) => (
                    <div
                      key={doc.id}
                      className={cn(
                        "flex items-center gap-2 p-2 rounded-md text-sm",
                        message.sender === 'employee'
                          ? "bg-primary-foreground/10"
                          : "bg-foreground/5"
                      )}
                    >
                      <FileText className="w-4 h-4 flex-shrink-0" />
                      <span className="truncate">{doc.title}</span>
                    </div>
                  ))}
                </div>
              )}
              
              <p className={cn(
                "text-xs mt-2 opacity-70",
                message.sender === 'employee' ? "text-right" : "text-left"
              )}>
                {format(message.timestamp, 'HH:mm')}
              </p>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Selected Documents */}
      {selectedDocuments.length > 0 && (
        <div className="px-4 py-2 border-t border-border bg-muted/50">
          <p className="text-xs text-muted-foreground mb-2">Attached documents:</p>
          <div className="flex flex-wrap gap-2">
            {selectedDocuments.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center gap-2 px-3 py-1.5 bg-card rounded-full text-sm border border-border"
              >
                <FileText className="w-3.5 h-3.5 text-primary" />
                <span className="truncate max-w-[150px]">{doc.title}</span>
                <button
                  onClick={() => onRemoveDocument(doc.id)}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-border bg-card">
        <div className="flex gap-3">
          <Textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your response..."
            className="min-h-[80px] resize-none bg-background"
          />
          <div className="flex flex-col gap-2">
            <Button
              onClick={handleSend}
              disabled={!inputValue.trim() && selectedDocuments.length === 0}
              className="flex-1"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
