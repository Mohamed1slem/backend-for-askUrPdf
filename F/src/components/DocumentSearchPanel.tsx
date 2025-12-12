import { Document, DocumentCategory, Message } from "@/types";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, FileText, Check, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { getCategoryLabel } from "@/data/mockData";
import { useState, useEffect } from "react";
import axios from "axios";

interface DocumentSearchPanelProps {
  documents: Document[]; // Add this line
  selectedDocuments: string[];
  onToggleDocument: (docId: string) => void;
  onConfirmSelection: () => void;
  clientMessage?: Message | null;
}

const categories: DocumentCategory[] = [
  "offers",
  "conventions",
  "guide-ngbss",
  "depot-vente",
];

export function DocumentSearchPanel({
  selectedDocuments,
  onToggleDocument,
  onConfirmSelection,
  clientMessage,
}: DocumentSearchPanelProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilters, setActiveFilters] = useState<DocumentCategory[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);

  const toggleFilter = (category: DocumentCategory) => {
    setActiveFilters((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    );
  };

  // Fetch documents from backend
  useEffect(() => {
    const fetchDocuments = async () => {
      if (!clientMessage && !searchQuery) {
        setDocuments([]);
        return;
      }

      setLoading(true);
      try {
        const response = await axios.post("http://127.0.0.1:8000/search", {
          query: searchQuery || clientMessage?.content,
          filters: activeFilters,
        });

        setDocuments(response.data.results);
      } catch (error) {
        console.error("Error fetching documents:", error);
        setDocuments([]);
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, [searchQuery, clientMessage, activeFilters]);

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
              onClick={() => setSearchQuery("")}
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
        {loading ? (
          <p className="text-center py-12 text-muted-foreground">Loading...</p>
        ) : documents.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No documents found</p>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc, index) => (
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
                  <div
                    className={cn(
                      "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0",
                      selectedDocuments.includes(doc.id)
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    )}
                  >
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
                      <span
                        className={cn(
                          "similarity-badge",
                          doc.similarity >= 70
                            ? "similarity-high"
                            : doc.similarity >= 40
                            ? "similarity-medium"
                            : "similarity-low"
                        )}
                      >
                        {Math.round(doc.similarity || 0)}%
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                      {doc.chunk.slice(0, 100)}...
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
              {selectedDocuments.length} document
              {selectedDocuments.length > 1 ? "s" : ""} selected
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
