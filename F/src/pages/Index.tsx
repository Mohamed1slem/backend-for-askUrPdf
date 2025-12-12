import { useState, useCallback } from "react";
import { Client, Message, Document } from "@/types";
import { mockClients, mockConversations, mockDocuments } from "@/data/mockData";
import { ClientList } from "@/components/ClientList";
import { ConversationView } from "@/components/ConversationView";
import { AIAssistantPanel } from "@/components/AIAssistantPanel";
import { DocumentSearchPanel } from "@/components/DocumentSearchPanel";
import { NavigationBar } from "@/components/NavigationBar";
import { MessageSquare } from "lucide-react";

type ActivePanel = "conversation" | "ai-assistant" | "document-search";

const Index = () => {
  const [clients] = useState<Client[]>(mockClients);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [conversations, setConversations] = useState(mockConversations);
  const [activePanel, setActivePanel] = useState<ActivePanel>("ai-assistant");

  // AI Assistant state
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedResponse, setGeneratedResponse] = useState<string | null>(
    null
  );
  const [aiSources, setAiSources] = useState<Document[]>([]);
  const [selectedAiSources, setSelectedAiSources] = useState<string[]>([]);

  // Document search state
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [attachedDocuments, setAttachedDocuments] = useState<Document[]>([]);

  // Response to use in conversation
  const [pendingResponse, setPendingResponse] = useState<string | null>(null);

  const handleSelectClient = useCallback((client: Client) => {
    setSelectedClient(client);
    setGeneratedResponse(null);
    setAiSources([]);
    setSelectedAiSources([]);
    setPendingResponse(null);
  }, []);

  const getLastClientMessage = useCallback((): Message | null => {
    if (!selectedClient) return null;
    const messages = conversations[selectedClient.id] || [];
    const clientMessages = messages.filter((m) => m.sender === "client");
    return clientMessages[clientMessages.length - 1] || null;
  }, [selectedClient, conversations]);

  const handleGenerateResponse = useCallback(async () => {
    const lastMessage = getLastClientMessage();
    if (!lastMessage) return;

    setIsGenerating(true);

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: lastMessage.content }),
      });

      const data = await response.json();

      setGeneratedResponse(data.answer);
      setAiSources(
        (data.sources || []).map((src, index) => ({
          id: `source-${index}`,
          title: src,
          content: "", // or fetch content later
        }))
      );
    } catch (error) {
      console.error("AI Generation Error:", error);
      setGeneratedResponse("❌ Server error while generating answer.");
      setAiSources([]);
    }

    setIsGenerating(false);
  }, [getLastClientMessage]);

  const handleToggleAiSource = useCallback((docId: string) => {
    setSelectedAiSources((prev) =>
      prev.includes(docId)
        ? prev.filter((id) => id !== docId)
        : [...prev, docId]
    );
  }, []);

  const handleUseResponse = useCallback(
    (includeDocuments: boolean) => {
      if (!generatedResponse) return;

      setPendingResponse(generatedResponse);

      if (includeDocuments) {
        const docsToAttach = aiSources.filter((doc) =>
          selectedAiSources.includes(doc.id)
        );
        setAttachedDocuments((prev) => {
          const existingIds = new Set(prev.map((d) => d.id));
          const newDocs = docsToAttach.filter((d) => !existingIds.has(d.id));
          return [...prev, ...newDocs];
        });
      }

      setActivePanel("conversation");
    },
    [generatedResponse, aiSources, selectedAiSources]
  );

  const handleToggleDocument = useCallback((docId: string) => {
    setSelectedDocuments((prev) =>
      prev.includes(docId)
        ? prev.filter((id) => id !== docId)
        : [...prev, docId]
    );
  }, []);
  const handleDocumentSearch = useCallback(
    async (query: string, filters: string[]) => {
      try {
        const response = await fetch("http://localhost:8000/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query, filters }),
        });

        const data = await response.json();
        return data.results;
      } catch (error) {
        console.error("Search error:", error);
        return [];
      }
    },
    []
  );
  const handleConfirmDocumentSelection = useCallback(() => {
    const docsToAttach = mockDocuments.filter((doc) =>
      selectedDocuments.includes(doc.id)
    );
    setAttachedDocuments((prev) => {
      const existingIds = new Set(prev.map((d) => d.id));
      const newDocs = docsToAttach.filter((d) => !existingIds.has(d.id));
      return [...prev, ...newDocs];
    });
    setSelectedDocuments([]);
    setActivePanel("ai-assistant");
  }, [selectedDocuments]);

  const handleRemoveDocument = useCallback((docId: string) => {
    setAttachedDocuments((prev) => prev.filter((d) => d.id !== docId));
  }, []);

  const handleSendMessage = useCallback(
    (content: string, attachments?: Document[]) => {
      if (!selectedClient) return;

      const newMessage: Message = {
        id: `m${Date.now()}`,
        content,
        sender: "employee",
        timestamp: new Date(),
        attachments: attachments || attachedDocuments,
      };

      setConversations((prev) => ({
        ...prev,
        [selectedClient.id]: [...(prev[selectedClient.id] || []), newMessage],
      }));

      // Reset states
      setAttachedDocuments([]);
      setPendingResponse(null);
      setGeneratedResponse(null);
      setSelectedAiSources([]);
    },
    [selectedClient, attachedDocuments]
  );

  const currentMessages = selectedClient
    ? conversations[selectedClient.id] || []
    : [];
  const lastClientMessage = getLastClientMessage();

  return (
    <div className="h-screen flex flex-col bg-background">
      <NavigationBar
        activePanel={activePanel}
        onPanelChange={setActivePanel}
        hasSelectedClient={!!selectedClient}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Client List Sidebar */}
        <aside className="w-80 border-r border-border flex-shrink-0">
          <ClientList
            clients={clients}
            selectedClientId={selectedClient?.id || null}
            onSelectClient={handleSelectClient}
          />
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex overflow-hidden">
          {selectedClient ? (
            <>
              {/* Conversation View */}
              <div className="flex-1 border-r border-border">
                <ConversationView
                  client={selectedClient}
                  messages={currentMessages}
                  selectedDocuments={attachedDocuments}
                  aiResponse={pendingResponse}
                  onSendMessage={handleSendMessage}
                  onRemoveDocument={handleRemoveDocument}
                />
              </div>

              {/* Right Panel */}
              <aside className="w-96 bg-card flex-shrink-0">
                {activePanel === "ai-assistant" ? (
                  <AIAssistantPanel
                    clientMessage={lastClientMessage?.content}
                    isGenerating={isGenerating}
                    generatedResponse={generatedResponse}
                    sources={aiSources}
                    selectedSources={selectedAiSources}
                    onGenerateResponse={handleGenerateResponse}
                    onToggleSource={handleToggleAiSource}
                    onUseResponse={handleUseResponse}
                  />
                ) : (
                  <DocumentSearchPanel
                    documents={mockDocuments}
                    selectedDocuments={selectedDocuments}
                    onToggleDocument={handleToggleDocument}
                    onConfirmSelection={handleConfirmDocumentSelection}
                    clientMessage={lastClientMessage} // ✅ FIXED
                  />
                )}
              </aside>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center mx-auto mb-6">
                  <MessageSquare className="w-10 h-10 text-muted-foreground" />
                </div>
                <h2 className="text-2xl font-semibold text-foreground mb-2">
                  Select a Conversation
                </h2>
                <p className="text-muted-foreground max-w-sm">
                  Choose a client message from the sidebar to start responding
                  with AI assistance
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Index;
