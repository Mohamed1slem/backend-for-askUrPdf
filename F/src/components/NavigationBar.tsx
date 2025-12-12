import { Sparkles, Search, MessageSquare, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Link } from 'react-router-dom';

type ActivePanel = 'conversation' | 'ai-assistant' | 'document-search';

interface NavigationBarProps {
  activePanel: ActivePanel;
  onPanelChange: (panel: ActivePanel) => void;
  hasSelectedClient: boolean;
}

export function NavigationBar({ activePanel, onPanelChange, hasSelectedClient }: NavigationBarProps) {
  return (
    <header className="h-16 border-b border-border bg-card px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
          <MessageSquare className="w-5 h-5 text-primary-foreground" />
        </div>
        <h1 className="text-xl font-semibold text-foreground">ClientAssist AI</h1>
      </div>

      <nav className="flex items-center gap-2">
        <Link to="/chatbot">
          <button className="nav-button flex items-center gap-2">
            <Bot className="w-4 h-4" />
            <span>AI Chatbot</span>
          </button>
        </Link>
        
        {hasSelectedClient && (
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
          </>
        )}
      </nav>

      <div className="w-[200px]" /> {/* Spacer for balance */}
    </header>
  );
}
