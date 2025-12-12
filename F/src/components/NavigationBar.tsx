import { Sparkles, Search, MessageSquare, Bot, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Link } from 'react-router-dom';

type ActivePanel = 'conversation' | 'ai-assistant' | 'document-search';

interface NavigationBarProps {
  activePanel: ActivePanel;
  onPanelChange: (panel: ActivePanel) => void;
  hasSelectedClient: boolean;
  onDeselectClient?: () => void;
}

export function NavigationBar({ activePanel, onPanelChange, hasSelectedClient, onDeselectClient }: NavigationBarProps) {
  return (
    <header className="h-16 border-b border-border bg-card px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
          <MessageSquare className="w-5 h-5 text-primary-foreground" />
        </div>
        <h1 className="text-xl font-semibold text-foreground">ClientAssist AI</h1>
      </div>

      <nav className="flex items-center gap-2">
        {!hasSelectedClient ? (
          <Link to="/chatbot">
            <button className="nav-button flex items-center gap-2">
              <Bot className="w-4 h-4" />
              <span>AI Chatbot</span>
            </button>
          </Link>
        ) : (
          <>
            <button
              onClick={() => onPanelChange('ai-assistant')}
              className={cn(
                "nav-button flex items-center gap-2",
                activePanel === 'ai-assistant' && "active"
              )}
            >
              <Sparkles className="w-4 h-4" />
              <span>AI Assistant</span>
            </button>
            
            <button
              onClick={() => onPanelChange('document-search')}
              className={cn(
                "nav-button flex items-center gap-2",
                activePanel === 'document-search' && "active"
              )}
            >
              <Search className="w-4 h-4" />
              <span>Search Documents</span>
            </button>
            
            {onDeselectClient && (
              <button
                onClick={onDeselectClient}
                className="nav-button flex items-center gap-2 ml-2 hover:bg-destructive hover:text-destructive-foreground"
                title="Close conversation"
              >
                <X className="w-4 h-4" />
                <span>Close</span>
              </button>
            )}
          </>
        )}
      </nav>

      <div className="w-[200px]" /> {/* Spacer for balance */}
    </header>
  );
}
