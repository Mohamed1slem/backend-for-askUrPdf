import { useState, useRef, useEffect, useCallback } from "react";

// ----- Helper Functions -----
const parseSource = (sourceString) => {
  const regex = /(.+\.(txt|pdf|docx?|xlsx?|pptx?|md)) \(([\d.]+)%\)/i;
  const match = sourceString.match(regex);

  if (!match)
    return {
      original: sourceString,
      filename: sourceString,
      percentage: 0,
      displayName: sourceString,
      icon: "📎",
      isHighConfidence: false,
      isLowConfidence: true,
    };

  const [, filename, , percentage] = match;
  const displayName = filename
    .split(/[\\/]/)
    .pop()
    .replace(/\.[^/.]+$/, "");
  const icons = {
    pdf: "📕",
    doc: "📘",
    docx: "📘",
    txt: "📄",
    xls: "📊",
    xlsx: "📊",
    ppt: "📽️",
    pptx: "📽️",
    md: "📝",
  };

  return {
    original: sourceString,
    filename,
    percentage: parseFloat(percentage),
    displayName,
    icon: icons[filename.split(".").pop().toLowerCase()] || "📎",
    isHighConfidence: parseFloat(percentage) >= 80,
    isLowConfidence: parseFloat(percentage) <= 30,
  };
};

const useConnectionStatus = () => {
  const [status, setStatus] = useState("connected");
  const [latency, setLatency] = useState(0);

  useEffect(() => {
    const check = async () => {
      const start = Date.now();
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 5000);
        await fetch("http://localhost:8000/health", {
          method: "HEAD",
          signal: controller.signal,
        });
        clearTimeout(timeout);
        setLatency(Date.now() - start);
        setStatus("connected");
      } catch {
        setStatus("disconnected");
      }
    };
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, []);

  return { status, latency };
};

// ----- SourceDisplay Component -----
const SourceDisplay = ({ sources, parsedSources }) => {
  if (!sources || sources.length === 0) return null;

  const displaySources = parsedSources || sources.map(parseSource);
  const sortedSources = [...displaySources].sort((a, b) => b.percentage - a.percentage);
  const totalConfidence = sortedSources.reduce((sum, src) => sum + src.percentage, 0) / sortedSources.length;

  return (
    <div className="mt-4 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-blue-700">Source Verification</span>
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
              {sortedSources.length} source{sortedSources.length > 1 ? 's' : ''}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-32 bg-blue-100 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${totalConfidence}%` }}
              />
            </div>
            <span className="text-xs font-semibold text-blue-600">{totalConfidence.toFixed(1)}% avg confidence</span>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {sortedSources.map((source, idx) => (
          <div 
            key={idx} 
            className={`p-3 rounded-lg border transition-all duration-200 hover:shadow-sm ${
              source.isHighConfidence 
                ? 'bg-green-50 border-green-200' 
                : source.isLowConfidence
                ? 'bg-amber-50 border-amber-200'
                : 'bg-white border-blue-100'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 pt-1 text-lg">{source.icon}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-semibold text-gray-800 truncate">{source.displayName}</h4>
                    {source.isHighConfidence && (
                      <span className="px-1.5 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium">
                        High confidence
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-sm font-bold text-blue-600">{source.percentage.toFixed(1)}%</div>
                      <div className="w-16 bg-gray-200 rounded-full h-1.5">
                        <div
                          className={`h-1.5 rounded-full transition-all duration-500 ${
                            source.isHighConfidence
                              ? 'bg-gradient-to-r from-green-400 to-green-500'
                              : source.isLowConfidence
                              ? 'bg-gradient-to-r from-amber-400 to-amber-500'
                              : 'bg-gradient-to-r from-blue-400 to-blue-500'
                          }`}
                          style={{ width: `${Math.min(source.percentage, 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <div className="text-xs text-gray-500 truncate" title={source.filename}>
                  {source.filename}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ----- Main Component -----
export default function EnhancedChat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      content: "👋 Hello! I'm your Algeria Telecom assistant. How can I help you find the perfect offer today?",
      sources: [],
      parsedSources: [],
      timestamp: new Date(),
      isTyping: false,
    },
  ]);
  
  const [input, setInput] = useState("");
  const [clientInput, setClientInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [typingDots, setTypingDots] = useState(0);
  const [autoScroll, setAutoScroll] = useState(true);
  const [activeTab, setActiveTab] = useState("ai"); // "ai" or "clients"
  
  const inputRef = useRef(null);
  const clientInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const { status: connectionStatus, latency } = useConnectionStatus();

  // Client data with messages
  const [clients, setClients] = useState([
    { 
      id: 1, 
      name: "Ahmed", 
      lastMessage: "I want a new offer", 
      messages: [
        { id: 1, from: "client", content: "Hello, I'm interested in your internet packages" },
        { id: 2, from: "employee", content: "Hi Ahmed! We have several packages starting from 1000 DZD/month" },
      ] 
    },
    { 
      id: 2, 
      name: "Sara", 
      lastMessage: "My internet is not working", 
      messages: [
        { id: 1, from: "client", content: "My internet connection keeps dropping" },
        { id: 2, from: "employee", content: "I'll help you troubleshoot that. Have you tried restarting your router?" },
      ] 
    },
    { 
      id: 3, 
      name: "Khaled", 
      lastMessage: "Roaming details", 
      messages: [
        { id: 1, from: "client", content: "What are your roaming charges in Europe?" },
        { id: 2, from: "employee", content: "Our roaming packages for Europe start at 2000 DZD for 1GB" },
      ] 
    },
  ]);

  const [selectedClient, setSelectedClient] = useState(null);

  // Quick action tags
  const tags = [
    { text: "Show all offers", query: "What are all the current offers available?" },
    { text: "Business conventions", query: "Explain the business conventions and pricing" },
    { text: "Roaming packages", query: "What roaming packages do you offer?" },
    { text: "NGBSS guide", query: "Explain the NGBSS activation process" },
    { text: "Technical support", query: "What are the technical support procedures?" },
  ];

  // ----- Typing animation -----
  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => setTypingDots((prev) => (prev + 1) % 4), 200);
      return () => clearInterval(interval);
    }
    setTypingDots(0);
  }, [loading]);

  // ----- Auto scroll -----
  useEffect(() => {
    if (autoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [messages, loading, autoScroll]);

  // ----- Focus management -----
  useEffect(() => {
    if (activeTab === "ai") {
      inputRef.current?.focus();
    } else if (activeTab === "clients" && selectedClient) {
      clientInputRef.current?.focus();
    }
  }, [activeTab, selectedClient]);

  // ----- Send AI Message -----
  const sendMessage = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: trimmed,
      timestamp: new Date(),
      isTyping: false,
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    const typingMessage = {
      id: Date.now() + 0.5,
      role: "assistant",
      content: "",
      isTyping: true,
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, typingMessage]);

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 45000);

      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Request-ID": `chat-${Date.now()}`,
        },
        body: JSON.stringify({
          question: trimmed,
          context: messages.slice(-3).map((m) => m.content).join(" "),
        }),
        signal: controller.signal,
      });
      
      clearTimeout(timeout);

      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      
      const data = await response.json();
      
      // Remove typing indicator
      setMessages((prev) => prev.filter((m) => !m.isTyping));

      const botMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: data.answer || "I couldn't find a specific answer for that. Could you rephrase your question?",
        sources: data.sources || [],
        parsedSources: (data.sources || []).map(parseSource),
        timestamp: new Date(),
        responseTime: Date.now() - userMessage.id,
        isTyping: false,
      };
      
      setMessages((prev) => [...prev, botMessage]);
      setAutoScroll(true);
      
    } catch (error) {
      setMessages((prev) => prev.filter((m) => !m.isTyping));
      
      const errorMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: error.name === "AbortError"
          ? "⏱️ Request timed out. Please try again."
          : "🚨 Unable to connect to the server. Please check your connection.",
        sources: [],
        parsedSources: [],
        timestamp: new Date(),
        isTyping: false,
      };
      
      setMessages((prev) => [...prev, errorMessage]);
    }

    setLoading(false);
  }, [input, loading, messages]);

  // ----- Send Client Message -----
  const sendClientMessage = useCallback(() => {
    const trimmed = clientInput.trim();
    if (!trimmed || !selectedClient) return;

    const newMessage = {
      id: Date.now(),
      from: "employee",
      content: trimmed,
      timestamp: new Date(),
    };

    const updatedClients = clients.map(client => {
      if (client.id === selectedClient.id) {
        return {
          ...client,
          messages: [...client.messages, newMessage],
          lastMessage: trimmed,
        };
      }
      return client;
    });

    setClients(updatedClients);
    setClientInput("");
    
    // Auto-reply after 2 seconds (simulate client response)
    setTimeout(() => {
      const autoReply = {
        id: Date.now() + 1000,
        from: "client",
        content: `Thank you for your response. I'll get back to you soon about "${trimmed}"`,
        timestamp: new Date(),
      };

      const updatedWithReply = updatedClients.map(client => {
        if (client.id === selectedClient.id) {
          return {
            ...client,
            messages: [...client.messages, autoReply],
          };
        }
        return client;
      });

      setClients(updatedWithReply);
    }, 2000);
  }, [clientInput, selectedClient, clients]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === "Enter" && !e.shiftKey && activeTab === "ai") {
      e.preventDefault();
      sendMessage();
    }
  }, [sendMessage, activeTab]);

  const handleClientKeyDown = useCallback((e) => {
    if (e.key === "Enter" && !e.shiftKey && selectedClient) {
      e.preventDefault();
      sendClientMessage();
    }
  }, [sendClientMessage, selectedClient]);

  const formatTime = (date) =>
    date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });

  const formatDate = (date) =>
    date.toLocaleDateString([], {
      weekday: "short",
      month: "short",
      day: "numeric",
    });

  // ----- Connection Indicator -----
  const ConnectionIndicator = () => {
    const config = {
      connected: {
        color: "bg-green-500",
        text: "Connected",
        pulse: true,
      },
      disconnected: {
        color: "bg-red-500",
        text: "Disconnected",
        pulse: false,
      },
    }[connectionStatus] || {
      color: "bg-gray-500",
      text: "Unknown",
      pulse: false,
    };

    return (
      <div className="flex items-center gap-2 text-xs">
        <span className="relative flex h-2 w-2">
          {config.pulse && (
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          )}
          <span className={`relative inline-flex rounded-full h-2 w-2 ${config.color}`}></span>
        </span>
        <span className="font-medium">{config.text}</span>
        {latency > 0 && connectionStatus === "connected" && (
          <span className="text-gray-500">({latency}ms)</span>
        )}
      </div>
    );
  };

  // ----- Clear AI Chat -----
  const clearChat = () => {
    setMessages([
      {
        id: 1,
        role: "assistant",
        content: "👋 Hello! I'm your Algeria Telecom assistant. How can I help you today?",
        sources: [],
        parsedSources: [],
        timestamp: new Date(),
        isTyping: false,
      },
    ]);
  };

  return (
    <div className="w-full h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 flex flex-col items-center p-2 md:p-4">
      <div className="w-full max-w-6xl h-full flex flex-col">
        {/* HEADER */}
        <div className="p-6 bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white rounded-t-2xl shadow-lg">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold">Algeria Telecom – Employee Assistant</h1>
              <p className="text-blue-100 text-sm mt-1">AI-powered support & client management</p>
            </div>
            <div className="flex items-center gap-4">
              <ConnectionIndicator />
              <button
                onClick={clearChat}
                className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors text-sm backdrop-blur-sm flex items-center gap-2"
              >
                <span>🗑️</span> Clear AI Chat
              </button>
            </div>
          </div>
        </div>

        {/* TABS */}
        <div className="flex gap-2 mt-4">
          <button
            onClick={() => setActiveTab("ai")}
            className={`px-4 py-2 rounded-lg font-semibold transition-all duration-200 ${
              activeTab === "ai"
                ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md"
                : "bg-white border border-gray-200 text-gray-700 hover:bg-gray-50"
            }`}
          >
            🤖 AI Assistant
          </button>
          <button
            onClick={() => setActiveTab("clients")}
            className={`px-4 py-2 rounded-lg font-semibold transition-all duration-200 ${
              activeTab === "clients"
                ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md"
                : "bg-white border border-gray-200 text-gray-700 hover:bg-gray-50"
            }`}
          >
            👥 Client Messages
          </button>
        </div>

        {/* CONTENT AREA */}
        <div className="flex-1 flex flex-col mt-4">
          {activeTab === "ai" ? (
            // AI ASSISTANT VIEW
            <>
              {/* QUICK ACTIONS */}
              <div className="mb-4 p-4 bg-white rounded-xl shadow-sm">
                <h3 className="text-sm font-semibold text-blue-700 mb-2">🚀 Quick Actions</h3>
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setInput(tag.query);
                        inputRef.current?.focus();
                      }}
                      className="px-3 py-1.5 bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 rounded-lg text-sm hover:from-blue-100 hover:to-indigo-100 transition-all duration-200 border border-blue-100"
                    >
                      {tag.text}
                    </button>
                  ))}
                </div>
              </div>

              {/* CHAT BODY */}
              <div className="flex-1 bg-white shadow-xl rounded-b-2xl overflow-hidden flex flex-col">
                <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
                  {messages.map((m) => (
                    <div
                      key={m.id}
                      className={`flex ${m.role === "user" ? "justify-end" : "justify-start"} mb-4`}
                    >
                      <div className="max-w-[85%] md:max-w-[75%]">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`text-xs font-medium ${m.role === "user" ? "text-blue-600" : "text-gray-500"}`}>
                            {m.role === "user" ? "You" : "AI Assistant"}
                          </span>
                          <span className="text-xs text-gray-400">{formatTime(m.timestamp)}</span>
                          {m.role === "assistant" && m.sources && m.sources.length > 0 && (
                            <span className="px-1.5 py-0.5 bg-blue-50 text-blue-600 rounded text-xs font-medium">Verified</span>
                          )}
                        </div>
                        
                        <div
                          className={`px-4 py-3 rounded-2xl shadow-sm ${
                            m.role === "user"
                              ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-br-none"
                              : "bg-gray-50 text-gray-800 border border-gray-100 rounded-bl-none"
                          }`}
                        >
                          {m.isTyping ? (
                            <div className="flex items-center gap-1">
                              <span>Searching</span>
                              {[...Array(3)].map((_, i) => (
                                <div
                                  key={i}
                                  className={`w-1.5 h-1.5 rounded-full bg-blue-400 ${
                                    i === typingDots % 3 ? 'opacity-100' : 'opacity-30'
                                  }`}
                                />
                              ))}
                            </div>
                          ) : (
                            m.content
                          )}
                        </div>

                        {/* Sources Display */}
                        {m.role === "assistant" && !m.isTyping && (m.sources?.length > 0 || m.parsedSources?.length > 0) && (
                          <SourceDisplay sources={m.sources} parsedSources={m.parsedSources} />
                        )}
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>

                {/* INPUT */}
                <div className="border-t border-gray-200 bg-white p-4">
                  <div className="flex gap-3">
                    <textarea
                      ref={inputRef}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Ask about offers, pricing, support..."
                      className="flex-1 p-3 rounded-xl border border-gray-200 focus:border-blue-300 focus:ring-2 focus:ring-blue-100 resize-none"
                      rows={Math.min(4, Math.max(1, input.split("\n").length))}
                      style={{ minHeight: '56px' }}
                    />
                    <button
                      onClick={sendMessage}
                      disabled={loading || !input.trim()}
                      className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md"
                    >
                      {loading ? "Searching..." : "Ask"}
                    </button>
                  </div>
                </div>
              </div>
            </>
          ) : (
            // CLIENTS VIEW
            <div className="flex-1 flex gap-4">
              {/* CLIENTS LIST */}
              <div className="w-1/3 bg-white rounded-xl shadow-sm p-4">
                <h3 className="font-semibold text-gray-700 mb-3">Active Conversations</h3>
                <div className="space-y-2">
                  {clients.map((client) => (
                    <button
                      key={client.id}
                      onClick={() => setSelectedClient(client)}
                      className={`w-full p-3 rounded-lg text-left transition-all duration-200 ${
                        selectedClient?.id === client.id
                          ? "bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200"
                          : "bg-gray-50 hover:bg-gray-100"
                      }`}
                    >
                      <div className="font-medium text-gray-800">{client.name}</div>
                      <div className="text-sm text-gray-500 truncate">{client.lastMessage}</div>
                      <div className="text-xs text-gray-400 mt-1">
                        {client.messages.length} messages
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* CLIENT CHAT */}
              <div className="flex-1 bg-white rounded-xl shadow-sm flex flex-col">
                {selectedClient ? (
                  <>
                    <div className="p-4 border-b border-gray-200">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-gray-800">{selectedClient.name}</h3>
                        <span className="text-xs text-gray-500">
                          Last active: {formatTime(new Date())}
                        </span>
                      </div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                      {selectedClient.messages.map((msg) => (
                        <div
                          key={msg.id}
                          className={`flex ${msg.from === "employee" ? "justify-end" : "justify-start"}`}
                        >
                          <div
                            className={`max-w-[80%] px-4 py-3 rounded-2xl ${
                              msg.from === "employee"
                                ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-br-none"
                                : "bg-gray-100 text-gray-800 rounded-bl-none"
                            }`}
                          >
                            {msg.content}
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="border-t border-gray-200 p-4">
                      <div className="flex gap-2">
                        <textarea
                          ref={clientInputRef}
                          value={clientInput}
                          onChange={(e) => setClientInput(e.target.value)}
                          onKeyDown={handleClientKeyDown}
                          placeholder="Type your message to client..."
                          className="flex-1 p-3 rounded-xl border border-gray-200 focus:border-blue-300 focus:ring-2 focus:ring-blue-100 resize-none"
                          rows={2}
                        />
                        <button
                          onClick={sendClientMessage}
                          disabled={!clientInput.trim()}
                          className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Send
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center text-gray-500">
                    Select a client to start chatting
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* FOOTER */}
        <div className="mt-4 p-4 bg-white/80 backdrop-blur-sm rounded-xl shadow-sm text-xs text-gray-600">
          <div className="flex flex-col md:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-6">
              <span>📊 Real-time document search</span>
              <span>✅ Verified sources</span>
              <span>🔒 Secure communication</span>
            </div>
            <div className="text-center md:text-right">
              <p>Algeria Telecom Employee Assistant • v2.1 • {new Date().getFullYear()}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}