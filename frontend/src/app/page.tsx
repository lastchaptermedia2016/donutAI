"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useAppState } from "@/components/providers";
import { ContextMode, contextConfig, BACKEND_URL } from "@/lib/utils";
import { useVoice } from "@/hooks/useVoice";
import { DonutLogo } from "@/components/DonutLogo";
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
  const { isListening, startListening, stopListening, isSupported, error: voiceError } = useVoice({
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
    <div className="min-h-screen billionaire-interface-gradient transition-all duration-700">
      <div className="flex h-screen">
        {/* Mobile Sidebar Overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-40 lg:hidden backdrop-blur-sm"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Sidebar */}
        <aside
          className={`
            fixed lg:static inset-y-0 left-0 z-50
            w-72 billionaire-sidebar
            transform transition-transform duration-500 ease-out
            ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
          `}
        >
          <div className="p-5 space-y-5">
            {/* Logo */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <DonutLogo size={40} animated />
                <div>
                  <h1 className="font-bold text-lg text-billionaire-gold-400 gold-text">
                    Donut
                  </h1>
                  <p className="text-xs text-billionaire-platinum/60">Executive Co-Pilot</p>
                </div>
              </div>
              <button
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden p-2 rounded-full hover:bg-billionaire-gold-500/10 transition-colors"
              >
                <X className="w-5 h-5 text-billionaire-platinum/70" />
              </button>
            </div>

            {/* Context Selector */}
            <div className="space-y-3">
              <p className="text-xs font-medium text-billionaire-platinum/50 uppercase tracking-wider">Context</p>
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
                      w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm transition-all duration-300
                      ${
                        isActive
                          ? `bg-billionaire-gold-500/15 text-billionaire-gold-400 font-medium gold-border-glow`
                          : "text-billionaire-platinum/70 hover:bg-billionaire-gold-500/5 hover:text-billionaire-gold-400/80"
                      }
                    `}
                  >
                    <span>{c.icon}</span>
                    <span>{c.label}</span>
                    {isActive && <CircleDot className="w-4 h-4 ml-auto text-billionaire-gold-500" />}
                  </button>
                );
              })}
            </div>

            {/* Navigation */}
            <div className="space-y-2 pt-3">
              <p className="text-xs font-medium text-billionaire-platinum/50 uppercase tracking-wider">Navigation</p>
              <a
                href="/"
                className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm bg-billionaire-gold-500/10 font-medium text-billionaire-gold-400 gold-border-glow"
              >
                <MessageSquare className="w-4 h-4" />
                Chat
              </a>
              <a
                href="/console"
                className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm text-billionaire-platinum/70 hover:bg-billionaire-gold-500/5 hover:text-billionaire-gold-400/80 transition-all duration-300"
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
          <header className="flex items-center justify-between px-6 py-4 border-b border-billionaire-gold-500/10 bg-billionaire-charcoal/50 backdrop-blur-xl">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2.5 rounded-full hover:bg-billionaire-gold-500/10 transition-colors"
              >
                <Menu className="w-5 h-5 text-billionaire-platinum/80" />
              </button>
              <div className="flex items-center gap-3">
                <span className={`w-3 h-3 rounded-full ${
                  contextMode === 'business' ? 'bg-billionaire-gold-500' :
                  contextMode === 'personal' ? 'bg-billionaire-emerald' : 'bg-billionaire-platinum'
                } animate-pulse-slow`} />
                <span className={`text-sm font-medium ${
                  contextMode === 'business' ? 'text-billionaire-gold-500' :
                  contextMode === 'personal' ? 'text-billionaire-emerald' : 'text-billionaire-platinum'
                }`}>
                  {config.label} Mode
                </span>
              </div>
            </div>
            <button
              onClick={toggleDarkMode}
              className="p-2.5 rounded-full hover:bg-billionaire-gold-500/10 transition-all duration-300"
            >
              {isDarkMode ? (
                <Sun className="w-5 h-5 text-billionaire-gold-400" />
              ) : (
                <Moon className="w-5 h-5 text-billionaire-platinum/70" />
              )}
            </button>
          </header>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-6 py-8 space-y-6">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-6 animate-fade-in">
                <div className="float-slow">
                  <DonutLogo size={120} />
                </div>
                <div>
                  <h2 className="text-3xl font-bold text-billionaire-gold-400 gold-text">
                    Hello, I'm Donut
                  </h2>
                  <p className="text-billionaire-platinum/60 mt-2 max-w-md mx-auto">
                    Your executive function co-pilot. Ask me to manage tasks, write diary entries,
                    search the web, or remember things for you.
                  </p>
                </div>
                <div className="flex flex-wrap gap-3 justify-center mt-6">
                  {[
                    "Add a task to review Q3 report",
                    "Write in my diary about today",
                    "Remember my boss prefers emails",
                    "Search for AI news today",
                  ].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => handleSend(suggestion)}
                      className="px-5 py-2.5 text-sm rounded-full glass-card-hover text-billionaire-platinum/80 hover:text-billionaire-gold-400 transition-all duration-300"
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
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-slide-up`}
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <div
                  className={`
                    max-w-[80%] 
                    ${msg.role === "user" ? "message-user" : "message-assistant"}
                  `}
                >
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">
                    {msg.content}
                  </p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start animate-scale-in">
                <div className="glass-card rounded-2xl rounded-bl-sm px-5 py-3">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1.5">
                      <div className="w-2.5 h-2.5 bg-billionaire-gold-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                      <div className="w-2.5 h-2.5 bg-billionaire-gold-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                      <div className="w-2.5 h-2.5 bg-billionaire-gold-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                    <span className="text-xs text-billionaire-platinum/60">Thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-billionaire-gold-500/10 p-6 space-y-4 bg-billionaire-charcoal/50 backdrop-blur-xl">
            {/* Voice Button + Text Input */}
            <div className="flex items-center gap-4 max-w-4xl mx-auto w-full">
              <button
                onClick={isListening ? stopListening : startListening}
                disabled={!isSupported}
                className={`
                  ${isListening ? 'voice-button-listening' : 'voice-button-idle'}
                  ${!isSupported ? "opacity-50 cursor-not-allowed" : ""}
                `}
                title={isListening ? "Tap to stop" : "Tap to speak"}
              >
                {isListening ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
              </button>

              <div className="flex-1 flex gap-3">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Type a message..."
                  className="glass-input flex-1"
                  autoFocus={true}
                  autoComplete="off"
                />
                <button
                  onClick={() => handleSend()}
                  disabled={(!inputText.trim() || isLoading) || false}
                  className="gold-button w-14 h-14 p-0 flex items-center justify-center disabled:opacity-50"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>

            {isListening && (
              <p className="text-center text-xs text-billionaire-gold-400 animate-pulse max-w-4xl mx-auto">
                🎤 Listening... speak now
              </p>
            )}
            
            {voiceError && (
              <p className="text-center text-xs text-billionaire-platinum/80 bg-billionaire-burgundy/10 px-4 py-2 rounded-xl max-w-4xl mx-auto border border-billionaire-burgundy/30">
                ⚠️ {voiceError}
              </p>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
