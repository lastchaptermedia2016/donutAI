"use client";

import { useState, useEffect, useCallback } from "react";
import { useAppState } from "@/components/providers";
import { BACKEND_URL } from "@/lib/utils";
import Link from "next/link";
import { MagneticButton } from "@/components/ui";
import {
  MessageSquare,
  CheckSquare,
  BookOpen,
  Brain,
  Bell,
  Calendar,
  ArrowLeft,
  Moon,
  Sun,
  Menu,
  X,
  Activity,
  TrendingUp,
  Clock,
} from "lucide-react";

interface DashboardStats {
  total_conversations: number;
  total_tasks: number;
  completed_tasks: number;
  total_memories: number;
  total_diary_entries: number;
  active_reminders: number;
  uptime_hours: number;
  avg_response_time_ms: number;
}

export default function ConsolePage() {
  const { isDarkMode, toggleDarkMode, sidebarOpen, setSidebarOpen } = useAppState();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("dashboard");

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/console/dashboard`);
      const data = await res.json();
      setStats(data);
    } catch (e) {
      console.error("Failed to fetch dashboard:", e);
    } finally {
      setLoading(false);
    }
  };

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: Activity },
    { id: "conversations", label: "Conversations", icon: MessageSquare },
    { id: "tasks", label: "Tasks", icon: CheckSquare },
    { id: "diary", label: "Diary", icon: BookOpen },
    { id: "memories", label: "Memories", icon: Brain },
    { id: "calendar", label: "Calendar", icon: Calendar },
    { id: "settings", label: "Settings", icon: Clock },
  ];

  return (
    <div className="min-h-screen bg-sophisticated-midnight/5 dark:bg-sophisticated-midnight/10">
      <div className="flex h-screen">
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
            w-64 bg-sophisticated-midnight/50 dark:bg-sophisticated-midnight/80 border-r border-sophisticated-charcoal/30
            transform transition-transform duration-300 ease-in-out
            ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
          `}
        >
          <div className="p-4 space-y-4">
            <div className="flex items-center justify-between">
              <Link href="/" className="flex items-center gap-2">
                <span className="text-2xl">🍩</span>
                <span className="font-bold text-lg text-sophisticated-ivory">Donut</span>
              </Link>
              <button
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden p-2 rounded-full hover:bg-sophisticated-charcoal/30"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <nav className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`
                      w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors
                      ${
                        isActive
                          ? "bg-sophisticated-burgundy/20 text-sophisticated-ivory font-medium"
                          : "text-sophisticated-taupe hover:bg-sophisticated-charcoal/20"
                      }
                    `}
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </button>
                );
              })}
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto lg:ml-64">
          <header className="flex items-center justify-between px-4 py-3 border-b border-sophisticated-charcoal/30 bg-sophisticated-midnight/50 dark:bg-sophisticated-midnight/80">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-full hover:bg-sophisticated-charcoal/30"
              >
                <Menu className="w-5 h-5" />
              </button>
              <h1 className="text-xl font-bold text-sophisticated-ivory">
                {navItems.find((n) => n.id === activeTab)?.label || "Console"}
              </h1>
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

          <div className="p-6">
            {activeTab === "dashboard" && (
              <div className="space-y-6">
                {/* Stat Cards */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <StatCard
                    title="Conversations"
                    value={stats?.total_conversations ?? 0}
                    icon={MessageSquare}
                    color="burgundy"
                  />
                  <StatCard
                    title="Tasks"
                    value={stats?.total_tasks ?? 0}
                    icon={CheckSquare}
                    color="emerald"
                  />
                  <StatCard
                    title="Memories"
                    value={stats?.total_memories ?? 0}
                    icon={Brain}
                    color="gold"
                  />
                  <StatCard
                    title="Diary Entries"
                    value={stats?.total_diary_entries ?? 0}
                    icon={BookOpen}
                    color="silver"
                  />
                </div>

                {/* Secondary Row */}
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30">
                    <div className="flex items-center gap-2 text-sm text-sophisticated-taupe">
                      <TrendingUp className="w-4 h-4" />
                      Completed Tasks
                    </div>
                    <p className="text-2xl font-bold mt-2 text-sophisticated-ivory">
                      {stats?.completed_tasks ?? 0}
                    </p>
                  </div>

                  <div className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30">
                    <div className="flex items-center gap-2 text-sm text-sophisticated-taupe">
                      <Bell className="w-4 h-4" />
                      Active Reminders
                    </div>
                    <p className="text-2xl font-bold mt-2 text-sophisticated-ivory">
                      {stats?.active_reminders ?? 0}
                    </p>
                  </div>

                  <div className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30">
                    <div className="flex items-center gap-2 text-sm text-sophisticated-taupe">
                      <Clock className="w-4 h-4" />
                      Uptime
                    </div>
                    <p className="text-2xl font-bold mt-2 text-sophisticated-ivory">
                      {stats?.uptime_hours?.toFixed(1) ?? 0}h
                    </p>
                  </div>
                </div>

                {/* Welcome Banner */}
                <div className="bg-gradient-to-r from-sophisticated-burgundy/20 via-sophisticated-slate/20 to-sophisticated-charcoal/20 rounded-xl p-6 border border-sophisticated-burgundy/20">
                  <h2 className="text-lg font-semibold flex items-center gap-2">
                    🍩 Welcome back to Donut Console
                  </h2>
                  <p className="text-sophisticated-taupe mt-1 text-sm">
                    Monitor your AI assistant's performance, manage tasks, review conversations, and configure settings.
                  </p>
                </div>
              </div>
            )}

            {activeTab === "conversations" && <ConversationsTab />}
            {activeTab === "tasks" && <TasksTab />}
            {activeTab === "diary" && <DiaryTab />}
            {activeTab === "memories" && <MemoriesTab />}
            {activeTab === "calendar" && (
              <div className="bg-sophisticated-midnight/50 rounded-xl p-6 border border-sophisticated-charcoal/30 text-center">
                <Calendar className="w-12 h-12 mx-auto text-sophisticated-taupe mb-4" />
                <h3 className="font-medium">Calendar Integration</h3>
                <p className="text-sophisticated-taupe text-sm mt-1">
                  Connect Google Calendar to manage events and scheduling
                </p>
              </div>
            )}
            {activeTab === "settings" && <SettingsTab />}
          </div>
        </main>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  color,
}: {
  title: string;
  value: number;
  icon: any;
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    burgundy: "text-sophisticated-burgundy bg-sophisticated-burgundy/20",
    emerald: "text-sophisticated-emerald bg-sophisticated-emerald/20",
    gold: "text-sophisticated-gold bg-sophisticated-gold/20",
    silver: "text-sophisticated-silver bg-sophisticated-silver/20",
  };

  return (
    <div className="luxury-glass-card rounded-xl p-4 holographic float-depth">
      <div className={`flex items-center gap-2 text-sm w-fit px-2 py-1 rounded-lg ${colorClasses[color]}`}>
        <Icon className="w-4 h-4" />
        {title}
      </div>
      <p className="text-2xl font-bold mt-2 text-sophisticated-ivory gold-gradient-text">{value}</p>
    </div>
  );
}

// Tab Components
function ConversationsTab() {
  const [conversations, setConversations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/console/conversations`)
      .then((r) => r.json())
      .then((data) => {
        setConversations(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSkeleton />;

  if (conversations.length === 0) {
    return (
      <div className="bg-sophisticated-midnight/50 rounded-xl p-8 border border-sophisticated-charcoal/30 text-center">
        <MessageSquare className="w-12 h-12 mx-auto text-sophisticated-taupe mb-4" />
        <h3 className="font-medium text-sophisticated-ivory text-lg">No conversations yet</h3>
        <p className="text-sophisticated-taupe mt-2">Start chatting with Donut to see your conversation history here</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {conversations.map((conv) => (
        <div
          key={conv.id}
          className="bg-sophisticated-midnight/50 rounded-xl p-5 border border-sophisticated-charcoal/30 hover:border-sophisticated-burgundy/40 transition-colors"
        >
          <div className="flex flex-col gap-3">
            {/* User Message */}
            <div className="flex items-start gap-3">
              <span className="text-xs font-semibold text-sophisticated-gold uppercase tracking-wide mt-0.5">You</span>
              <p className="font-medium text-sophisticated-ivory break-words flex-1">{conv.user_message}</p>
            </div>
            
            {/* Agent Response */}
            <div className="flex items-start gap-3">
              <span className="text-xs font-semibold text-sophisticated-burgundy uppercase tracking-wide mt-0.5">Donut</span>
              <p className="text-sm text-sophisticated-taupe break-words flex-1 leading-relaxed">
                {conv.agent_response?.length > 200 
                  ? `${conv.agent_response.substring(0, 200)}...` 
                  : conv.agent_response}
              </p>
            </div>

            {/* Meta Information */}
            <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-sophisticated-charcoal/20">
              <span className={`px-2.5 py-1 rounded-full text-xs font-medium bg-sophisticated-burgundy/20 text-sophisticated-burgundy border border-sophisticated-burgundy/30`}>
                {conv.context_mode || 'Neutral'}
              </span>
              <span className="text-xs text-sophisticated-taupe">
                {new Date(conv.created_at).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function TasksTab() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/tasks?context_mode=all&show_completed=false`)
      .then((r) => r.json())
      .then((data) => {
        setTasks(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSkeleton />;

  if (tasks.length === 0) {
    return (
      <div className="bg-sophisticated-midnight/50 rounded-xl p-8 border border-sophisticated-charcoal/30 text-center">
        <CheckSquare className="w-12 h-12 mx-auto text-sophisticated-taupe mb-4" />
        <h3 className="font-medium text-sophisticated-ivory text-lg">No tasks yet</h3>
        <p className="text-sophisticated-taupe mt-2">Ask Donut to create a task and it will appear here</p>
      </div>
    );
  }

  const priorityColors: Record<string, string> = {
    urgent: "bg-sophisticated-burgundy shadow-lg shadow-sophisticated-burgundy/50",
    high: "bg-sophisticated-emerald shadow-lg shadow-sophisticated-emerald/50",
    medium: "bg-sophisticated-gold shadow-lg shadow-sophisticated-gold/50",
    low: "bg-sophisticated-silver shadow-lg shadow-sophisticated-silver/50",
  };

  const priorityLabels: Record<string, string> = {
    urgent: "Urgent",
    high: "High",
    medium: "Medium",
    low: "Low",
  };

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <div
          key={task.id}
          className="bg-sophisticated-midnight/50 rounded-xl p-5 border border-sophisticated-charcoal/30 hover:border-sophisticated-emerald/40 transition-colors"
        >
          <div className="flex flex-col gap-3">
            <div className="flex items-start gap-4">
              {/* Priority Indicator */}
              <div className="flex flex-col items-center gap-1 mt-0.5">
                <div className={`w-3 h-3 rounded-full flex-shrink-0 ${priorityColors[task.priority] || "bg-sophisticated-taupe"}`} />
                <span className="text-[10px] text-sophisticated-taupe uppercase tracking-wide">
                  {priorityLabels[task.priority] || task.priority}
                </span>
              </div>
              
              {/* Task Content */}
              <div className="flex-1 min-w-0">
                <h4 className="font-semibold text-sophisticated-ivory break-words">{task.title}</h4>
                {task.description && (
                  <p className="text-sm text-sophisticated-taupe mt-1 break-words leading-relaxed">
                    {task.description}
                  </p>
                )}
              </div>
            </div>

            {/* Task Meta */}
            <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-sophisticated-charcoal/20">
              <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-sophisticated-burgundy/20 text-sophisticated-burgundy border border-sophisticated-burgundy/30">
                {task.context_mode || 'Neutral'}
              </span>
              {task.due_date && (
                <span className="text-xs text-sophisticated-taupe flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {new Date(task.due_date).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function DiaryTab() {
  const [entries, setEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/diary?limit=20`)
      .then((r) => r.json())
      .then((data) => {
        setEntries(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSkeleton />;

  if (entries.length === 0) {
    return (
      <div className="bg-sophisticated-midnight/50 rounded-xl p-6 border border-sophisticated-charcoal/30 text-center">
        <BookOpen className="w-12 h-12 mx-auto text-sophisticated-taupe mb-4" />
        <p className="text-sophisticated-taupe">No diary entries yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {entries.map((entry) => (
        <div
          key={entry.id}
          className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30"
        >
          <div className="flex items-center gap-2 text-xs text-sophisticated-taupe mb-2">
            <span>{new Date(entry.created_at).toLocaleDateString()}</span>
            {entry.mood && <span>• {entry.mood}</span>}
          </div>
          <p className="text-sm text-sophisticated-ivory whitespace-pre-wrap">{entry.content}</p>
        </div>
      ))}
    </div>
  );
}

function MemoriesTab() {
  const [memories, setMemories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/memory/all`)
      .then((r) => r.json())
      .then((data) => {
        setMemories(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSkeleton />;

  if (memories.length === 0) {
    return (
      <div className="bg-sophisticated-midnight/50 rounded-xl p-6 border border-sophisticated-charcoal/30 text-center">
        <Brain className="w-12 h-12 mx-auto text-sophisticated-taupe mb-4" />
        <p className="text-sophisticated-taupe">No memories stored yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {memories.map((memory) => (
        <div
          key={memory.id}
          className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30"
        >
          <p className="text-sm text-sophisticated-ivory">{memory.content}</p>
          <div className="flex items-center gap-2 mt-2 text-xs text-sophisticated-taupe">
            <span className="px-2 py-1 rounded bg-sophisticated-charcoal/30">{memory.context_mode}</span>
            {memory.tags?.map((tag: string) => (
              <span key={tag} className="px-2 py-1 rounded bg-sophisticated-burgundy/20">#{tag}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function SettingsTab() {
  return (
    <div className="max-w-4xl space-y-6">
      <AISettingsSection />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30">
          <h3 className="font-medium mb-2">API Configuration</h3>
          <p className="text-sm text-sophisticated-taupe">
            Backend URL: <code className="bg-sophisticated-charcoal/20 px-2 py-0.5 rounded">{BACKEND_URL}</code>
          </p>
        </div>

        <div className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30">
          <h3 className="font-medium mb-2">Model Settings</h3>
          <p className="text-sm text-sophisticated-taupe">
            LLM: Groq llama-3.3-70b-versatile
          </p>
          <p className="text-sm text-sophisticated-taupe">
            Intent: Groq llama-3.1-8b-instant
          </p>
        </div>
      </div>
    </div>
  );
}

interface AISettings {
  personality_tone: string;
  response_length: string;
  formality_level: number;
  emotion: string;
  tts_voice: string;
  tts_speed: number;
  tts_provider: string;
  llm_temperature: number;
  llm_max_tokens: number;
}

interface SettingsOptions {
  [key: string]: {
    options?: Array<{ value: string; label: string; description: string }>;
    min?: number;
    max?: number;
    default?: number | string;
    step?: number;
    labels?: Record<string, string>;
    description?: string;
  };
}

// Default slider configurations (used when API fails)
const DEFAULT_SLIDER_CONFIG = {
  formality_level: { min: 1, max: 10, step: 1, default: 5 },
  tts_speed: { min: 0.5, max: 2.0, step: 0.1, default: 1.0 },
  llm_temperature: { min: 0.1, max: 1.0, step: 0.05, default: 0.7 },
  llm_max_tokens: { min: 256, max: 4096, step: 256, default: 1024 },
};

// Debounce utility for slider updates
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

function AISettingsSection() {
  const [settings, setSettings] = useState<AISettings | null>(null);
  const [options, setOptions] = useState<SettingsOptions | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  // Local slider values for immediate feedback during drag
  const [localSliderValues, setLocalSliderValues] = useState<Record<string, number>>({});

  useEffect(() => {
    fetchAISettings();
    fetchAISettingsOptions();
  }, []);

  const fetchAISettings = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/ai-settings`);
      const data = await res.json();
      setSettings(data);
      console.log("AI Settings loaded:", data);
    } catch (e) {
      console.error("Failed to fetch AI settings:", e);
    } finally {
      setLoading(false);
    }
  };

  const fetchAISettingsOptions = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/ai-settings/options`);
      const data = await res.json();
      setOptions(data);
      console.log("AI Settings options loaded:", data);
    } catch (e) {
      console.error("Failed to fetch AI settings options:", e);
      // Options fetch failure is not critical - sliders will use defaults
    }
  };

  // Helper to get slider config with fallbacks
  const getSliderConfig = (key: keyof typeof DEFAULT_SLIDER_CONFIG) => {
    const config = options?.[key];
    const defaults = DEFAULT_SLIDER_CONFIG[key];
    return {
      min: config?.min ?? defaults.min,
      max: config?.max ?? defaults.max,
      step: config?.step ?? defaults.step,
      default: config?.default ?? defaults.default,
    };
  };

  // Debounced API call to avoid rate limiting
  const debouncedUpdateSetting = useCallback(
    debounce(async (key: string, value: any) => {
      if (!settings) return;
      
      setSaving(true);
      setMessage(null);
      
      try {
        console.log(`Saving ${key} = ${value}`);
        const res = await fetch(`${BACKEND_URL}/api/ai-settings`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ [key]: value }),
        });
        
        if (res.ok) {
          const data = await res.json();
          setSettings(data);
          setMessage({ type: 'success', text: 'Settings saved successfully' });
        } else if (res.status === 429) {
          setMessage({ type: 'error', text: 'Too many requests. Please wait a moment.' });
        } else {
          throw new Error('Failed to save settings');
        }
      } catch (e: any) {
        console.error("Failed to save AI settings:", e);
        setMessage({ type: 'error', text: e.message || 'Failed to save settings' });
      } finally {
        setSaving(false);
        setTimeout(() => setMessage(null), 3000);
      }
    }, 500), // 500ms debounce delay
    [settings]
  );

  // Handler for slider changes - updates local state immediately, API call is debounced
  const handleSliderChange = (key: string, value: number) => {
    // Update local state for immediate visual feedback
    setLocalSliderValues(prev => ({ ...prev, [key]: value }));
    // Debounced API call
    debouncedUpdateSetting(key, value);
  };

  // Get the current value for a slider (local or from settings)
  const getSliderValue = (key: string, defaultValue: number): number => {
    if (localSliderValues[key] !== undefined) {
      return localSliderValues[key];
    }
    const value = settings?.[key as keyof AISettings];
    if (typeof value === 'number') {
      return value;
    }
    return defaultValue;
  };

  // Direct update for non-slider inputs (dropdowns)
  const updateSetting = async (key: string, value: any) => {
    if (!settings) return;
    
    setSaving(true);
    setMessage(null);
    
    try {
      const res = await fetch(`${BACKEND_URL}/api/ai-settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [key]: value }),
      });
      
      if (res.ok) {
        const data = await res.json();
        setSettings(data);
        setMessage({ type: 'success', text: 'Settings saved successfully' });
      } else if (res.status === 429) {
        setMessage({ type: 'error', text: 'Too many requests. Please wait a moment.' });
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (e: any) {
      console.error("Failed to save AI settings:", e);
      setMessage({ type: 'error', text: e.message || 'Failed to save settings' });
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(null), 3000);
    }
  };

  const resetToDefaults = async () => {
    setSaving(true);
    setMessage(null);
    
    try {
      const res = await fetch(`${BACKEND_URL}/api/ai-settings/reset`, {
        method: 'POST',
      });
      
      if (res.ok) {
        const data = await res.json();
        setSettings(data);
        setMessage({ type: 'success', text: 'Settings reset to defaults' });
      } else {
        throw new Error('Failed to reset settings');
      }
    } catch (e) {
      console.error("Failed to reset AI settings:", e);
      setMessage({ type: 'error', text: 'Failed to reset settings' });
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(null), 3000);
    }
  };

  if (loading) return <LoadingSkeleton />;

  return (
    <div className="bg-sophisticated-midnight/50 rounded-xl p-6 border border-sophisticated-charcoal/30">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold">AI Personality & Voice</h2>
          <p className="text-sm text-sophisticated-taupe mt-1">
            Customize how Donut thinks, speaks, and responds
          </p>
        </div>
        <button
          onClick={resetToDefaults}
          disabled={saving}
          className="px-4 py-2 text-sm text-sophisticated-taupe hover:text-sophisticated-ivory border border-sophisticated-charcoal/50 rounded-lg hover:bg-sophisticated-charcoal/30 transition-colors disabled:opacity-50"
        >
          Reset to Defaults
        </button>
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded-lg text-sm ${
          message.type === 'success' 
            ? 'bg-sophisticated-emerald/20 text-sophisticated-emerald border border-sophisticated-emerald/30' 
            : 'bg-sophisticated-burgundy/20 text-sophisticated-burgundy border border-sophisticated-burgundy/30'
        }`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Personality Tone */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-sophisticated-ivory">Personality Tone</label>
          <select
            value={settings?.personality_tone || 'warm'}
            onChange={(e) => updateSetting('personality_tone', e.target.value)}
            className="w-full bg-sophisticated-charcoal/50 border border-sophisticated-charcoal/60 rounded-lg px-3 py-2 text-sm text-sophisticated-ivory focus:outline-none focus:border-sophisticated-burgundy/70 focus:ring-2 focus:ring-sophisticated-burgundy/20 transition-all cursor-pointer hover:border-sophisticated-charcoal/80"
          >
            {options?.personality_tone?.options?.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-sophisticated-slate text-sophisticated-ivory">
                {opt.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-sophisticated-taupe">
            {options?.personality_tone?.options?.find(o => o.value === settings?.personality_tone)?.description}
          </p>
        </div>

        {/* Emotion */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-sophisticated-ivory">Emotional Tone</label>
          <select
            value={settings?.emotion || 'neutral'}
            onChange={(e) => updateSetting('emotion', e.target.value)}
            className="w-full bg-sophisticated-charcoal/50 border border-sophisticated-charcoal/60 rounded-lg px-3 py-2 text-sm text-sophisticated-ivory focus:outline-none focus:border-sophisticated-burgundy/70 focus:ring-2 focus:ring-sophisticated-burgundy/20 transition-all cursor-pointer hover:border-sophisticated-charcoal/80"
          >
            {options?.emotion?.options?.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-sophisticated-slate text-sophisticated-ivory">
                {opt.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-sophisticated-taupe">
            {options?.emotion?.options?.find(o => o.value === settings?.emotion)?.description}
          </p>
        </div>

        {/* Response Length */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-sophisticated-ivory">Response Length</label>
          <select
            value={settings?.response_length || 'balanced'}
            onChange={(e) => updateSetting('response_length', e.target.value)}
            className="w-full bg-sophisticated-charcoal/50 border border-sophisticated-charcoal/60 rounded-lg px-3 py-2 text-sm text-sophisticated-ivory focus:outline-none focus:border-sophisticated-burgundy/70 focus:ring-2 focus:ring-sophisticated-burgundy/20 transition-all cursor-pointer hover:border-sophisticated-charcoal/80"
          >
            {options?.response_length?.options?.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-sophisticated-slate text-sophisticated-ivory">
                {opt.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-sophisticated-taupe">
            {options?.response_length?.options?.find(o => o.value === settings?.response_length)?.description}
          </p>
        </div>

        {/* Formality Level */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="text-sm font-medium text-sophisticated-ivory">Formality Level</label>
            <span className="text-sm font-bold text-sophisticated-gold">{getSliderValue('formality_level', 5)}</span>
          </div>
          <input
            type="range"
            min={options?.formality_level?.min || 1}
            max={options?.formality_level?.max || 10}
            step={options?.formality_level?.step || 1}
            value={getSliderValue('formality_level', 5)}
            onChange={(e) => handleSliderChange('formality_level', parseInt(e.target.value))}
            className="w-full h-2 bg-sophisticated-charcoal/50 rounded-lg appearance-none cursor-pointer accent-sophisticated-burgundy hover:accent-sophisticated-gold active:accent-sophisticated-gold transition-all"
          />
          <div className="flex justify-between text-xs text-sophisticated-taupe">
            <span>Casual</span>
            <span>Balanced</span>
            <span>Formal</span>
          </div>
        </div>

        {/* TTS Voice */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-sophisticated-ivory">AI Voice</label>
          <select
            value={settings?.tts_voice || 'autumn'}
            onChange={(e) => updateSetting('tts_voice', e.target.value)}
            className="w-full bg-sophisticated-charcoal/50 border border-sophisticated-charcoal/60 rounded-lg px-3 py-2 text-sm text-sophisticated-ivory focus:outline-none focus:border-sophisticated-burgundy/70 focus:ring-2 focus:ring-sophisticated-burgundy/20 transition-all cursor-pointer hover:border-sophisticated-charcoal/80"
          >
            {options?.tts_voice?.options?.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-sophisticated-slate text-sophisticated-ivory">
                {opt.label} - {opt.description}
              </option>
            ))}
          </select>
        </div>

        {/* TTS Speed */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="text-sm font-medium text-sophisticated-ivory">Voice Speed</label>
            <span className="text-sm font-bold text-sophisticated-gold">{getSliderValue('tts_speed', 1.0).toFixed(1)}x</span>
          </div>
          <input
            type="range"
            min={options?.tts_speed?.min || 0.5}
            max={options?.tts_speed?.max || 2.0}
            step={options?.tts_speed?.step || 0.1}
            value={getSliderValue('tts_speed', 1.0)}
            onChange={(e) => handleSliderChange('tts_speed', parseFloat(e.target.value))}
            className="w-full h-2 bg-sophisticated-charcoal/50 rounded-lg appearance-none cursor-pointer accent-sophisticated-burgundy hover:accent-sophisticated-gold active:accent-sophisticated-gold transition-all"
          />
          <div className="flex justify-between text-xs text-sophisticated-taupe">
            <span>0.5x</span>
            <span>1.0x</span>
            <span>2.0x</span>
          </div>
        </div>

        {/* TTS Provider */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-sophisticated-ivory">TTS Provider</label>
          <select
            value={settings?.tts_provider || 'groq'}
            onChange={(e) => updateSetting('tts_provider', e.target.value)}
            className="w-full bg-sophisticated-charcoal/50 border border-sophisticated-charcoal/60 rounded-lg px-3 py-2 text-sm text-sophisticated-ivory focus:outline-none focus:border-sophisticated-burgundy/70 focus:ring-2 focus:ring-sophisticated-burgundy/20 transition-all cursor-pointer hover:border-sophisticated-charcoal/80"
          >
            {options?.tts_provider?.options?.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-sophisticated-slate text-sophisticated-ivory">
                {opt.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-sophisticated-taupe">
            {options?.tts_provider?.options?.find(o => o.value === settings?.tts_provider)?.description}
          </p>
        </div>

        {/* LLM Temperature */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="text-sm font-medium text-sophisticated-ivory">Creativity (Temperature)</label>
            <span className="text-sm font-bold text-sophisticated-gold">{getSliderValue('llm_temperature', 0.7).toFixed(2)}</span>
          </div>
          <input
            type="range"
            min={options?.llm_temperature?.min || 0.1}
            max={options?.llm_temperature?.max || 1.0}
            step={options?.llm_temperature?.step || 0.05}
            value={getSliderValue('llm_temperature', 0.7)}
            onChange={(e) => handleSliderChange('llm_temperature', parseFloat(e.target.value))}
            className="w-full h-2 bg-sophisticated-charcoal/50 rounded-lg appearance-none cursor-pointer accent-sophisticated-burgundy hover:accent-sophisticated-gold active:accent-sophisticated-gold transition-all"
          />
          <div className="flex justify-between text-xs text-sophisticated-taupe">
            <span>Focused</span>
            <span>Balanced</span>
            <span>Creative</span>
          </div>
        </div>

        {/* LLM Max Tokens */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="text-sm font-medium text-sophisticated-ivory">Max Response Length</label>
            <span className="text-sm font-bold text-sophisticated-gold">{getSliderValue('llm_max_tokens', 1024)}</span>
          </div>
          <input
            type="range"
            min={options?.llm_max_tokens?.min || 256}
            max={options?.llm_max_tokens?.max || 4096}
            step={options?.llm_max_tokens?.step || 256}
            value={getSliderValue('llm_max_tokens', 1024)}
            onChange={(e) => handleSliderChange('llm_max_tokens', parseInt(e.target.value))}
            className="w-full h-2 bg-sophisticated-charcoal/50 rounded-lg appearance-none cursor-pointer accent-sophisticated-burgundy hover:accent-sophisticated-gold active:accent-sophisticated-gold transition-all"
          />
          <div className="flex justify-between text-xs text-sophisticated-taupe">
            <span>Short</span>
            <span>Medium</span>
            <span>Long</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30 animate-pulse"
        >
          <div className="h-4 bg-sophisticated-charcoal/30 rounded w-3/4" />
          <div className="h-3 bg-sophisticated-charcoal/20 rounded w-1/2 mt-2" />
        </div>
      ))}
    </div>
  );
}