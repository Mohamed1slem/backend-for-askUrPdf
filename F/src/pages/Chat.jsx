import { useState, useRef, useEffect, useCallback } from "react";

// Helper function to parse source strings with percentages
const parseSource = (sourceString) => {
  const regex = /(.+\.(?:txt|pdf|docx?)) \(([\d.]+)%\)/;
  const match = sourceString.match(regex);

  if (match) {
    const [, filename, percentage] = match;
    return {
      original: sourceString,
      filename: filename.trim(),
      percentage: parseFloat(percentage),
      displayName: filename.split("\\").pop().replace(".txt", ""),
    };
  }

  return {
    original: sourceString,
    filename: sourceString,
    percentage: 0,
    displayName: sourceString,
  };
};

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      content:
        "👋 Hello! I'm your Algeria Telecom assistant. How can I help you find the perfect offer today?",
      sources: [],
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState("connected");
  const [typingDots, setTypingDots] = useState(0);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  // Check server connection - removed health check for now
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);

        const res = await fetch("http://localhost:8000/", {
          signal: controller.signal,
        });
        clearTimeout(timeoutId);

        setIsOnline(res.ok);
        setConnectionStatus(res.ok ? "connected" : "server-error");
      } catch {
        setIsOnline(true); // Set to true to not block input
        setConnectionStatus("disconnected");
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  // Typing animation
  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        setTypingDots((prev) => (prev + 1) % 4);
      }, 300);
      return () => clearInterval(interval);
    } else {
      setTypingDots(0);
    }
  }, [loading]);

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const sendMessage = useCallback(async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput || loading) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: trimmedInput,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);

      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage.content }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content:
          data.answer ||
          "I couldn't find a specific answer for that. Could you rephrase your question?",
        sources: data.sources || [],
        parsedSources: (data.sources || []).map(parseSource),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content:
          error.name === "AbortError"
            ? "⏱️ Request timed out. Please try again."
            : "🚨 Unable to connect to the server. Please check your connection or try again later.",
        sources: [],
        parsedSources: [],
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }

    setLoading(false);
  }, [input, loading]);

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    },
    [sendMessage]
  );

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const ConnectionIndicator = () => {
    const statusConfig = {
      connected: { color: "bg-green-500", text: "Connected", icon: "🟢" },
      disconnected: { color: "bg-red-500", text: "Disconnected", icon: "🔴" },
      "server-error": {
        color: "bg-yellow-500",
        text: "Server Error",
        icon: "🟡",
      },
    };

    const config = statusConfig[connectionStatus] || statusConfig.disconnected;

    return (
      <div className="flex items-center gap-2 text-xs">
        <span className={`w-2 h-2 rounded-full ${config.color}`}></span>
        <span>{config.text}</span>
      </div>
    );
  };

  // Component for displaying sources with confidence scores
  const SourceDisplay = ({ sources, parsedSources }) => {
    if (!sources || sources.length === 0) return null;

    const hasParsedSources = parsedSources && parsedSources.length > 0;
    const displaySources = hasParsedSources
      ? parsedSources
      : sources.map(parseSource);

    // Sort by percentage (highest first)
    const sortedSources = [...displaySources].sort(
      (a, b) => b.percentage - a.percentage
    );

    return (
      <div className="mt-3 ml-2">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-semibold text-gray-600">
            Sources & Confidence:
          </span>
          <span className="text-xs text-gray-400">
            {sortedSources.length} document{sortedSources.length > 1 ? "s" : ""}{" "}
            referenced
          </span>
        </div>
        <div className="space-y-2">
          {sortedSources.map((source, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <div className="flex-shrink-0 w-16">
                <div className="text-xs font-semibold text-blue-600">
                  {source.percentage.toFixed(1)}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-blue-600 h-1.5 rounded-full"
                    style={{ width: `${Math.min(source.percentage, 100)}%` }}
                  />
                </div>
              </div>
              <div className="flex-1">
                <div
                  className="text-xs text-gray-700 font-medium truncate"
                  title={source.filename}
                >
                  📄 {source.displayName}
                </div>
                <div
                  className="text-xs text-gray-500 truncate"
                  title={source.filename}
                >
                  {source.filename}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="w-full h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex flex-col items-center p-4 md:p-6">
      <div className="w-full max-w-4xl h-full flex flex-col">
        {/* HEADER */}
        <div className="p-6 bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-t-2xl shadow-lg">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-xl backdrop-blur-sm">
                <span className="text-2xl">💬</span>
              </div>
              <div>
                <h1 className="text-xl font-bold">
                  Algeria Telecom – Smart Offer Finder
                </h1>
                <p className="text-blue-100 text-sm">
                  AI-powered assistance with source verification
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <ConnectionIndicator />
              <button
                onClick={() => setMessages(messages.slice(0, 1))}
                className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors text-sm backdrop-blur-sm"
              >
                Clear Chat
              </button>
            </div>
          </div>
        </div>

        {/* CHAT BODY */}

        <div className="flex-1 bg-white shadow-lg rounded-b-2xl overflow-hidden flex flex-col">
          <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 bg-gradient-to-b from-white to-gray-50">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex ${
                  m.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div className="max-w-[85%] md:max-w-[75%]">
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`text-xs font-medium ${
                        m.role === "user" ? "text-blue-600" : "text-gray-500"
                      }`}
                    >
                      {m.role === "user" ? "You" : "Algeria Telecom AI"}
                    </span>
                    <span className="text-xs text-gray-400">
                      {formatTime(m.timestamp)}
                    </span>
                    {m.role === "assistant" &&
                      m.sources &&
                      m.sources.length > 0 && (
                        <span className="px-1.5 py-0.5 bg-blue-50 text-blue-600 rounded text-xs font-medium">
                          Verified
                        </span>
                      )}
                  </div>

                  {/* Message bubble */}
                  <div
                    className={`px-4 py-3 rounded-2xl text-sm md:text-base whitespace-pre-wrap shadow-sm ${
                      m.role === "user"
                        ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-br-none"
                        : "bg-gray-100 text-gray-800 border border-gray-200 rounded-bl-none"
                    }`}
                  >
                    {m.content}
                  </div>

                  {/* Enhanced Sources Display */}
                  {m.role === "assistant" &&
                    (m.sources?.length > 0 || m.parsedSources?.length > 0) && (
                      <SourceDisplay
                        sources={m.sources}
                        parsedSources={m.parsedSources}
                        showOriginal={true} // ✅ new prop to show original DOCX/PDF
                      />
                    )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* FOOTER */}
        <div className="mt-4 text-center text-xs text-gray-500">
          <p>
            Powered by Algeria Telecom AI • All responses include source
            verification • {new Date().getFullYear()}
          </p>
        </div>
      </div>
    </div>
  );
}
