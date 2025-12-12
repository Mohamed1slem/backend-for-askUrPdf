import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Copy, Check, FileText, History, X, Clock } from 'lucide-react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { toast } from '@/hooks/use-toast';
import { documents, documentTypes } from '@/data/mockData';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  attachedDocs?: typeof documents;
  timestamp: Date;
}

interface SearchHistoryItem {
  id: string;
  query: string;
  timestamp: Date;
}

const CHAT_HISTORY_KEY = 'ai-chatbot-search-history';

const AIChatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Bonjour ! Je suis votre assistant IA. Je peux vous aider à rédiger des réponses pour vos clients et à trouver les documents pertinents. Comment puis-je vous aider aujourd\'hui ?',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load search history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(CHAT_HISTORY_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      setSearchHistory(parsed.map((item: any) => ({ ...item, timestamp: new Date(item.timestamp) })));
    }
  }, []);

  // Save search history to localStorage
  const saveToHistory = (query: string) => {
    const newItem: SearchHistoryItem = {
      id: Date.now().toString(),
      query: query.slice(0, 100),
      timestamp: new Date(),
    };
    const updated = [newItem, ...searchHistory.filter(h => h.query !== query)].slice(0, 10);
    setSearchHistory(updated);
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(updated));
  };

  const removeFromHistory = (id: string) => {
    const updated = searchHistory.filter(h => h.id !== id);
    setSearchHistory(updated);
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(updated));
  };

  const clearHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem(CHAT_HISTORY_KEY);
    toast({ title: 'Historique effacé', description: 'Votre historique de recherche a été supprimé.' });
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

// Only showing the relevant changes inside AIChatbot component

const handleSend = async () => {
  if (!inputValue.trim() || isLoading) return;

  const queryText = inputValue.trim();
  saveToHistory(queryText);

  const userMessage: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: queryText,
    timestamp: new Date(),
  };

  setMessages((prev) => [...prev, userMessage]);
  setInputValue('');
  setIsLoading(true);
  setShowHistory(false);

  try {
    // ---------- Send message to Python backend ----------
    const response = await fetch('http://localhost:8000/query', { // change URL if needed
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: queryText }),
    });

    if (!response.ok) {
      throw new Error('Erreur du serveur');
    }

    const data: { content: string; attachedDocs?: typeof documents } = await response.json();

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: data.content,
      attachedDocs: data.attachedDocs || [],
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);
  } catch (error) {
    toast({
      title: 'Erreur',
      description: 'Une erreur est survenue lors de la génération de la réponse.',
      variant: 'destructive',
    });
  } finally {
    setIsLoading(false);
  }
};


  const handleCopy = async (content: string, id: string) => {
    await navigator.clipboard.writeText(content);
    setCopiedId(id);
    toast({
      title: 'Copié',
      description: 'La réponse a été copiée dans le presse-papiers.',
    });
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleHistoryClick = (query: string) => {
    setInputValue(query);
    setShowHistory(false);
  };

  return (
    <DashboardLayout>
      <div className="animate-fade-in h-[calc(100vh-8rem)] flex flex-col">
        <div className="mb-6 flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground mb-2">Assistant IA</h1>
            <p className="text-muted-foreground">
              Décrivez la demande du client pour obtenir une suggestion de réponse avec les documents pertinents
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowHistory(!showHistory)}
            className="gap-2"
          >
            <History className="w-4 h-4" />
            Historique
          </Button>
        </div>

        {/* Search History Panel */}
        {showHistory && searchHistory.length > 0 && (
          <div className="mb-4 card-elevated p-4 animate-slide-up">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-sm text-foreground">Recherches récentes</h3>
              <Button variant="ghost" size="sm" onClick={clearHistory} className="text-xs text-muted-foreground">
                Tout effacer
              </Button>
            </div>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {searchHistory.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between gap-2 p-2 rounded-lg hover:bg-muted/50 group cursor-pointer"
                  onClick={() => handleHistoryClick(item.query)}
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <Clock className="w-3 h-3 text-muted-foreground flex-shrink-0" />
                    <span className="text-sm text-foreground truncate">{item.query}</span>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="w-6 h-6 opacity-0 group-hover:opacity-100"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFromHistory(item.id);
                    }}
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {showHistory && searchHistory.length === 0 && (
          <div className="mb-4 card-elevated p-6 text-center animate-slide-up">
            <Clock className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">Aucun historique de recherche</p>
          </div>
        )}

        {/* Chat Container */}
        <div className="flex-1 card-elevated overflow-hidden flex flex-col">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-4 animate-slide-up ${
                  message.role === 'user' ? 'flex-row-reverse' : ''
                }`}
              >
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.role === 'assistant'
                      ? 'bg-primary/10'
                      : 'bg-muted'
                  }`}
                >
                  {message.role === 'assistant' ? (
                    <Bot className="w-5 h-5 text-primary" />
                  ) : (
                    <User className="w-5 h-5 text-muted-foreground" />
                  )}
                </div>

                <div
                  className={`flex-1 max-w-[80%] ${
                    message.role === 'user' ? 'text-right' : ''
                  }`}
                >
                  <div
                    className={`inline-block p-4 rounded-2xl ${
                      message.role === 'assistant'
                        ? 'bg-muted/50 rounded-tl-sm'
                        : 'bg-primary text-primary-foreground rounded-tr-sm'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>

                  {/* Attached Documents */}
                  {message.attachedDocs && message.attachedDocs.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-xs text-muted-foreground">Documents suggérés :</p>
                      <div className="flex flex-wrap gap-2">
                        {message.attachedDocs.map((doc) => (
                          <span
                            key={doc.id}
                            className="inline-flex items-center gap-1 px-3 py-1.5 bg-primary/10 text-primary text-xs rounded-full"
                          >
                            <FileText className="w-3 h-3" />
                            {doc.title}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Copy Button for Assistant Messages */}
                  {message.role === 'assistant' && message.id !== '1' && (
                    <div className="mt-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleCopy(message.content, message.id)}
                        className="text-xs text-muted-foreground hover:text-foreground"
                      >
                        {copiedId === message.id ? (
                          <>
                            <Check className="w-3 h-3 mr-1" />
                            Copié
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3 mr-1" />
                            Copier la réponse
                          </>
                        )}
                      </Button>
                    </div>
                  )}

                  <p className="text-xs text-muted-foreground mt-1">
                    {message.timestamp.toLocaleTimeString('fr-FR', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex gap-4 animate-fade-in">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-primary" />
                </div>
                <div className="bg-muted/50 rounded-2xl rounded-tl-sm p-4">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-primary animate-pulse-soft" />
                    <span className="text-sm text-muted-foreground">Génération en cours...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-border bg-card">
            <div className="flex gap-3">
              <Textarea
                placeholder="Décrivez la demande du client ou collez son message ici..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={2}
                className="resize-none flex-1"
                disabled={isLoading}
              />
              <Button
                onClick={handleSend}
                disabled={!inputValue.trim() || isLoading}
                size="icon"
                className="h-auto aspect-square"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Appuyez sur Entrée pour envoyer, Maj+Entrée pour un saut de ligne
            </p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AIChatbot;
