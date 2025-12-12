import { Document, Message } from '@/types';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Sparkles, FileText, Check, Loader2, Copy, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { getCategoryLabel } from '@/data/mockData';
import { useState, useEffect } from 'react';

interface AIAssistantPanelProps {
  clientMessage: Message | null;
  isGenerating: boolean;
  generatedResponse: string | null;
  sources: Document[];
  selectedSources: string[];
  onGenerateResponse: () => void;
  onToggleSource: (docId: string) => void;
  onUseResponse: (includeDocuments: boolean) => void;
}

export function AIAssistantPanel({
  clientMessage,
  isGenerating,
  generatedResponse,
  sources,
  selectedSources,
  onGenerateResponse,
  onToggleSource,
  onUseResponse,
}: AIAssistantPanelProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (generatedResponse) {
      navigator.clipboard.writeText(generatedResponse);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (!clientMessage) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
          <Sparkles className="w-8 h-8 text-primary" />
        </div>
        <h3 className="text-lg font-semibold text-foreground mb-2">AI Assistant</h3>
        <p className="text-muted-foreground max-w-sm">
          Select a client message to generate an AI-powered response with relevant source documents.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-5 h-5 text-primary" />
          <h3 className="font-semibold text-foreground">AI Assistant</h3>
        </div>
        <div className="p-3 bg-muted rounded-lg">
          <p className="text-sm text-muted-foreground mb-1">Client's message:</p>
          <p className="text-sm text-foreground">{clientMessage.content}</p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {!generatedResponse && !isGenerating && (
          <Button
            onClick={onGenerateResponse}
            className="w-full gap-2"
            size="lg"
          >
            <Sparkles className="w-4 h-4" />
            Generate AI Response
          </Button>
        )}

        {isGenerating && (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary animate-spin mb-4" />
            <p className="text-muted-foreground">Analyzing message and finding relevant documents...</p>
          </div>
        )}

        {generatedResponse && (
          <div className="space-y-4 animate-fade-in">
            {/* Generated Response */}
            <Card className="p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-foreground">Generated Response</h4>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCopy}
                  className="gap-2"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      Copy
                    </>
                  )}
                </Button>
              </div>
              <p className="text-sm text-foreground whitespace-pre-wrap">{generatedResponse}</p>
            </Card>

            {/* Sources */}
            {sources.length > 0 && (
              <div>
                <h4 className="font-medium text-foreground mb-3">Source Documents</h4>
                <p className="text-sm text-muted-foreground mb-3">
                  Select documents to include in your response:
                </p>
                <div className="space-y-2">
                  {sources.map((doc) => (
                    <button
                      key={doc.id}
                      onClick={() => onToggleSource(doc.id)}
                      className={cn(
                        "document-card w-full text-left",
                        selectedSources.includes(doc.id) && "selected"
                      )}
                    >
                      <div className="flex items-start gap-3">
                        <div className={cn(
                          "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0",
                          selectedSources.includes(doc.id)
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted"
                        )}>
                          {selectedSources.includes(doc.id) ? (
                            <Check className="w-4 h-4" />
                          ) : (
                            <FileText className="w-4 h-4 text-muted-foreground" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium text-foreground truncate">
                              {doc.title}
                            </span>
                          </div>
                          <span className="text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground">
                            {getCategoryLabel(doc.category)}
                          </span>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <Button
                onClick={() => onUseResponse(false)}
                variant="outline"
                className="flex-1 gap-2"
              >
                Use Response Only
                <ArrowRight className="w-4 h-4" />
              </Button>
              <Button
                onClick={() => onUseResponse(true)}
                className="flex-1 gap-2"
                disabled={selectedSources.length === 0}
              >
                Include Documents ({selectedSources.length})
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
