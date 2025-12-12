import { Document, DocumentCategory } from '@/types';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, FileText, Check, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { getCategoryLabel } from '@/data/mockData';
import { useState, useMemo } from 'react';

interface DocumentSearchPanelProps {
  documents: Document[];
  selectedDocuments: string[];
  onToggleDocument: (docId: string) => void;
  onConfirmSelection: () => void;
  clientMessage?: string;
}

const categories: DocumentCategory[] = ['offers', 'conventions', 'guide-ngbss', 'depot-vente'];

export function DocumentSearchPanel({
  documents,
  selectedDocuments,
  onToggleDocument,
  onConfirmSelection,
  clientMessage,
}: DocumentSearchPanelProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilters, setActiveFilters] = useState<DocumentCategory[]>([]);

  const toggleFilter = (category: DocumentCategory) => {
    setActiveFilters((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    );
  };
  // Define the onSearch function or remove this block if unnecessary
  // Example definition:
  const onSearch = async (query: string, filters: DocumentCategory[]) => {
    return documents.filter((doc) => 
      (!filters.length || filters.includes(doc.category)) &&
      (doc.title.toLowerCase().includes(query.toLowerCase()) || 
       doc.content.toLowerCase().includes(query.toLowerCase()))
    );
  };
  
  // If setDisplayedDocs is undefined, ensure it's defined or remove this line
  // setDisplayedDocs(results);
  const calculateSimilarity = (doc: Document, query: string): number => {
    if (!query && !clientMessage) return Math.random() * 30 + 50;
    
    const searchText = (query || clientMessage || '').toLowerCase();
    const docText = `${doc.title} ${doc.content}`.toLowerCase();
    
    const words = searchText.split(/\s+/).filter(w => w.length > 2);
    const matches = words.filter(word => docText.includes(word));
    
    const baseScore = (matches.length / Math.max(words.length, 1)) * 100;
    return Math.min(Math.max(baseScore + Math.random() * 20, 10), 98);
  };

  const filteredDocuments = useMemo(() => {
    let filtered = documents;

    if (activeFilters.length > 0) {
      filtered = filtered.filter((doc) => activeFilters.includes(doc.category));
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (doc) =>
          doc.title.toLowerCase().includes(query) ||
          doc.content.toLowerCase().includes(query)
      );
    }

    return filtered.map((doc) => ({
      ...doc,
      similarity: calculateSimilarity(doc, searchQuery),
    })).sort((a, b) => (b.similarity || 0) - (a.similarity || 0));
  }, [documents, activeFilters, searchQuery, clientMessage]);

  const getSimilarityClass = (similarity: number): string => {
    if (similarity >= 70) return 'similarity-high';
    if (similarity >= 40) return 'similarity-medium';
    return 'similarity-low';
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border space-y-4">
        <div className="flex items-center gap-2">
          <Search className="w-5 h-5 text-primary" />
          <h3 className="font-semibold text-foreground">Document Search</h3>
        </div>

        {/* Search Input */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documents..."
            className="pl-10"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => toggleFilter(category)}
              className={cn(
                "filter-chip",
                activeFilters.includes(category) ? "active" : "border-border"
              )}
            >
              {getCategoryLabel(category)}
            </button>
          ))}
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto p-4">
        {filteredDocuments.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No documents found</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredDocuments.map((doc, index) => (
              <button
                key={doc.id}
                onClick={() => onToggleDocument(doc.id)}
                className={cn(
                  "document-card w-full text-left animate-fade-in",
                  selectedDocuments.includes(doc.id) && "selected"
                )}
                style={{ animationDelay: `${index * 30}ms` }}
              >
                <div className="flex items-start gap-3">
                  <div className={cn(
                    "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0",
                    selectedDocuments.includes(doc.id)
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  )}>
                    {selectedDocuments.includes(doc.id) ? (
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
                      <span className={cn("similarity-badge", getSimilarityClass(doc.similarity || 0))}>
                        {Math.round(doc.similarity || 0)}%
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                      {doc.excerpt || doc.content.slice(0, 100)}...
                    </p>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground">
                      {getCategoryLabel(doc.category)}
                    </span>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Selection Footer */}
      {selectedDocuments.length > 0 && (
        <div className="p-4 border-t border-border bg-card animate-fade-in">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">
              {selectedDocuments.length} document{selectedDocuments.length > 1 ? 's' : ''} selected
            </span>
            <Button onClick={onConfirmSelection} className="gap-2">
              <Check className="w-4 h-4" />
              Confirm Selection
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
