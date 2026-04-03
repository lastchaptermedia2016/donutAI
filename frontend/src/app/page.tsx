"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useAppState } from "@/components/providers";
import { ContextMode, contextConfig, BACKEND_URL } from "@/lib/utils";
import { useVoice } from "@/hooks/useVoice";
import {
  Mic,
  MicOff,
  Send,
  Moon,
  Sun,
  Menu,
  X,
  Circle,
  CircleDot,
  CircleSlash,
  MessageSquare,
  BookOpen,
  CheckSquare,
  Brain,
  Settings,
  BarChart3,
} from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export default function HomePage() {
  const { contextMode, setContextMode, sessionId, isDarkMode, toggleDarkMode, sidebarOpen, setSidebarOpen } =
    useAppState();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const config = contextConfig[contextMode];
  const { isListening, startListening, stopListening, isSupported } = useVoice({
    onResult: (text) => {
      setInputText(text);
      handleSend(text);
    },
  });

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // WebSocket connection with reconnection logic
  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimer: NodeJS.Timeout | null = null;
    const maxReconnectAttempts = 3;
    let reconnectAttempts = 0;

    const connect = () => {
      try {
        const wsUrl = `${BACKEND_URL.replace("http", "ws")}/ws/chat`;
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
          console.log("WebSocket connected");
          setWs(socket);
          reconnectAttempts = 0; // Reset on successful connection
        };

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === "text") {
              setMessages((prev) => [
                ...prev,
                {
                  role: "assistant",
                  content: data.content,
                  timestamp: new Date().toISOString(),
                },
              ]);
              setIsLoading(false);

              // Speak response
              if ("speechSynthesis" in window) {
                const utterance = new SpeechSynthesisUtterance(data.content);
                speechSynthesis.speak(utterance);
              }
            } else if (data.type === "status") {
              // Show status in UI
            }
          } catch (error) {
            console.error("Error parsing WebSocket message:", error);
          }
        };

        socket.onerror = (error) => {
          console.error("WebSocket error:", error);
        };

        socket.onclose = (event) => {
          console.log("WebSocket closed:", event.code, event.reason);
          setWs(null);
          
          // Attempt reconnection if not a normal closure
          if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            console.log(`Attempting WebSocket reconnection (${reconnectAttempts}/${maxReconnectAttempts})...`);
            reconnectTimer = setTimeout(connect, 2000 * reconnectAttempts); // Exponential backoff
          }
        };
      } catch (error) {
        console.error("Failed to create WebSocket connection:", error);
      }
    };

    connect();

    return () => {
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
      if (socket) {
        socket.onclose = null; // Prevent reconnection on cleanup
        socket.close();
      }
    };
  }, []);

  const handleSend = useCallback(
    async (text?: string) => {
      const messageText = text || inputText;
      if (!messageText.trim() || isLoading) return;

      const userMessage: Message = {
        role: "user",
        content: messageText,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setInputText("");
      setIsLoading(true);

      // Send via WebSocket if available, otherwise HTTP
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(
          JSON.stringify({
            type: "message",
            content: messageText,
            context_mode: contextMode,
          })
        );
      } else {
        try {
          const response = await fetch(`${BACKEND_URL}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              message: messageText,
              context_mode: contextMode,
              session_id: sessionId,
            }),
          });
          const data = await response.json();
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: data.response,
              timestamp: new Date().toISOString(),
            },
          ]);

          // Speak response using browser TTS
          if ("speechSynthesis" in window && data.response) {
            const utterance = new SpeechSynthesisUtterance(data.response);
            speechSynthesis.speak(utterance);
          }
        } catch (error) {
          console.error("Error sending message:", error);
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: "Sorry, I encountered an error processing your request.",
              timestamp: new Date().toISOString(),
            },
          ]);
        } finally {
          setIsLoading(false);
        }
      }
    },
    [inputText, isLoading, ws, contextMode, sessionId]
  );

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={`min-h-screen ${config.gradient} transition-all duration-300`}>
      <div className="flex h-screen">
        {/* Mobile Sidebar Overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Sidebar */}
        <aside
          className={`
            fixed lg:static inset-y-0 left-0 z-50
            w-72 ${config.gradient} backdrop-blur-xl
            border-r border-sophisticated-charcoal/30
            transform transition-transform duration-300 ease-in-out
            ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
          `}
        >
          <div className="p-4 space-y-4">
            {/* Logo */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-2xl">🍩</span>
                <div>
                  <h1 className="font-bold text-lg text-sophisticated-ivory">
                    Donut
                  </h1>
                  <p className="text-xs text-sophisticated-taupe">Executive Co-Pilot</p>
                </div>
              </div>
              <button
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden p-2 rounded-full hover:bg-sophisticated-charcoal/30"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Context Selector */}
            <div className="space-y-2">
              <p className="text-xs font-medium text-sophisticated-taupe uppercase">Context</p>
              {(Object.keys(contextConfig) as ContextMode[]).map((mode) => {
                const c = contextConfig[mode];
                const isActive = mode === contextMode;
                const Icon =
                  mode === "business" ? CircleDot : mode === "personal" ? Circle : CircleSlash;
                return (
                  <button
                    key={mode}
                    onClick={() => setContextMode(mode)}
                    className={`
                      w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors
                      ${
                        isActive
                          ? `bg-sophisticated-burgundy/20 ${c.color} font-medium`
                          : "text-sophisticated-taupe hover:bg-sophisticated-charcoal/20"
                      }
                    `}
                  >
                    <span>{c.icon}</span>
                    <span>{c.label}</span>
                    {isActive && <CircleDot className="w-4 h-4 ml-auto" />}
                  </button>
                );
              })}
            </div>

            {/* Navigation */}
            <div className="space-y-2">
              <p className="text-xs font-medium text-sophisticated-taupe uppercase">Navigation</p>
              <a
                href="/"
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm bg-sophisticated-burgundy/20 font-medium text-sophisticated-ivory"
              >
                <MessageSquare className="w-4 h-4" />
                Chat
              </a>
              <a
                href="/console"
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-sophisticated-taupe hover:bg-sophisticated-charcoal/20"
              >
                <BarChart3 className="w-4 h-4" />
                Console
              </a>
            </div>
          </div>
        </aside>

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col min-w-0">
          {/* Header */}
          <header className="flex items-center justify-between px-4 py-3 border-b border-sophisticated-charcoal/30 bg-sophisticated-midnight/50 backdrop-blur-lg">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-full hover:bg-sophisticated-charcoal/30"
              >
                <Menu className="w-5 h-5" />
              </button>
              <div className="flex items-center gap-2">
                <span className={`w-3 h-3 rounded-full ${config.color.replace("text-", "bg-")}`} />
                <span className={`text-sm font-medium ${config.color}`}>
                  {config.label} Mode
                </span>
              </div>
            </div>
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-full hover:bg-sophisticated-charcoal/30"
            >
              {isDarkMode ? (
                <Sun className="w-5 h-5" />
              ) : (
                <Moon className="w-5 h-5" />
              )}
            </button>
          </header>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
                <span className="text-6xl">🍩</span>
                <div>
                  <h2 className="text-2xl font-bold text-sophisticated-ivory">
                    Hello, I'm Donut
                  </h2>
                  <p className="text-sophisticated-taupe mt-1 max-w-sm">
                    Your executive function co-pilot. Ask me to manage tasks, write diary entries,
                    search the web, or remember things for you.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 justify-center mt-4">
                  {[
                    "Add a task to review Q3 report",
                    "Write in my diary about today",
                    "Remember my boss prefers emails",
                    "Search for AI news today",
                  ].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => handleSend(suggestion)}
                      className="px-4 py-2 text-sm rounded-full bg-sophisticated-charcoal/20 
                        border border-sophisticated-charcoal/30 hover:border-sophisticated-burgundy 
                        transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`
                    max-w-[80%] rounded-2xl px-4 py-3
                    ${
                      msg.role === "user"
                        ? "bg-sophisticated-burgundy text-sophisticated-ivory rounded-br-sm"
                        : "bg-sophisticated-slate text-sophisticated-platinum rounded-bl-sm"
                    }
                  `}
                >
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">
                    {msg.content}
                  </p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-sophisticated-slate rounded-2xl rounded-bl-sm px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-sophisticated-charcoal rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                      <div className="w-2 h-2 bg-sophisticated-charcoal rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                      <div className="w-2 h-2 bg-sophisticated-charcoal rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                    <span className="text-xs text-sophisticated-taupe">Thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-sophisticated-charcoal/30 p-4 space-y-3 bg-sophisticated-midnight/50 backdrop-blur-lg">
            {/* Voice Button + Text Input */}
            <div className="flex items-center gap-3">
              <button
                onClick={isListening ? stopListening : startListening}
                disabled={!isSupported}
                className={`
                  flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center
                  transition-all duration-200
                  ${
                    isListening
                      ? "bg-red-500 text-white animate-pulse ring-4 ring-red-200"
                      : "bg-sophisticated-burgundy hover:bg-sophisticated-emerald hover:text-white"
                  }
                  ${!isSupported ? "opacity-50 cursor-not-allowed" : ""}
                `}
                title={isListening ? "Tap to stop" : "Tap to speak"}
              >
                {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>

              <div className="flex-1 flex gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Type a message..."
                  className="flex-1 px-4 py-3 rounded-full bg-sophisticated-charcoal/20 text-sophisticated-ivory placeholder-sophisticated-charcoal/50 border border-sophisticated-charcoal/30 focus:outline-none focus:ring-2 focus:ring-sophisticated-gold"
                  autoFocus={true}
                  autoComplete="off"
                />
                <button
                  onClick={() => handleSend()}
                  disabled={(!inputText.trim() || isLoading) || false}
                  className="w-12 h-12 rounded-full bg-sophisticated-burgundy hover:bg-sophisticated-emerald hover:text-white flex items-center justify-center transition-colors disabled:opacity-50"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>

            {isListening && (
              <p className="text-center text-xs text-red-500 animate-pulse">
                Listening... speak now
              </p>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}