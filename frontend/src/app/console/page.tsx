"use client";

import { useState, useEffect } from "react";
import { useAppState } from "@/components/providers";
import { BACKEND_URL } from "@/lib/utils";
import Link from "next/link";
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
        <main className="flex-1 overflow-y-auto">
          <header className="flex items-center justify-between px-4 py-3 border-b border-sophisticated-charcoal/30 bg-sophisticated-midnight/50 dark:bg-sophisticated-midnight/80">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-full hover:bg-sophisticated-charcoal/30"
              >
                <Menu className="w-5 h-5" />
              </button>
              <h1 className="text-xl font-bold">
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
    <div className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30">
      <div className={`flex items-center gap-2 text-sm w-fit px-2 py-1 rounded-lg ${colorClasses[color]}`}>
        <Icon className="w-4 h-4" />
        {title}
      </div>
      <p className="text-2xl font-bold mt-2 text-sophisticated-ivory">{value}</p>
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
      <div className="bg-sophisticated-midnight/50 rounded-xl p-6 border border-sophisticated-charcoal/30 text-center">
        <MessageSquare className="w-12 h-12 mx-auto text-sophisticated-taupe mb-4" />
        <p className="text-sophisticated-taupe">No conversations yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {conversations.map((conv) => (
        <div
          key={conv.id}
          className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30"
        >
          <div className="flex justify-between items-start gap-4">
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{conv.user_message}</p>
              <p className="text-sm text-sophisticated-taupe mt-1">{conv.agent_response?.substring(0, 100)}...</p>
            </div>
            <div className="text-xs text-sophisticated-taupe whitespace-nowrap">
              <div className="px-2 py-1 rounded bg-sophisticated-charcoal/30">{conv.context_mode}</div>
              <div className="mt-1">{new Date(conv.created_at).toLocaleString()}</div>
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
      <div className="bg-sophisticated-midnight/50 rounded-xl p-6 border border-sophisticated-charcoal/30 text-center">
        <CheckSquare className="w-12 h-12 mx-auto text-sophisticated-taupe mb-4" />
        <p className="text-sophisticated-taupe">No tasks yet</p>
      </div>
    );
  }

  const priorityColors: Record<string, string> = {
    urgent: "bg-sophisticated-burgundy",
    high: "bg-sophisticated-emerald",
    medium: "bg-sophisticated-gold",
    low: "bg-sophisticated-silver",
  };

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <div
          key={task.id}
          className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30 flex items-center gap-3"
        >
          <div className={`w-3 h-3 rounded-full flex-shrink-0 ${priorityColors[task.priority] || "bg-sophisticated-taupe"}`} />
          <div className="flex-1 min-w-0">
            <p className="font-medium text-sophisticated-ivory">{task.title}</p>
            {task.description && (
              <p className="text-sm text-sophisticated-taupe truncate">{task.description}</p>
            )}
          </div>
          <span className="text-xs text-sophisticated-taupe px-2 py-1 rounded bg-sophisticated-charcoal/30">
            {task.context_mode}
          </span>
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
    <div className="max-w-lg space-y-4">
      <div className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30">
        <h3 className="font-medium mb-2">API Configuration</h3>
        <p className="text-sm text-sophisticated-taupe">
          Backend URL: <code className="bg-sophisticated-charcoal/20 px-2 py-0.5 rounded">{BACKEND_URL}</code>
        </p>
      </div>

      <div className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30">
        <h3 className="font-medium mb-2">Model Settings</h3>
        <p className="text-sm text-sophisticated-taupe">
          LLM Model: Groq llama-3.3-70b-versatile
        </p>
        <p className="text-sm text-sophisticated-taupe">
          Intent Model: Groq llama-3.1-8b-instant
        </p>
      </div>

      <div className="bg-sophisticated-midnight/50 rounded-xl p-4 border border-sophisticated-charcoal/30">
        <h3 className="font-medium mb-2">Voice Settings</h3>
        <p className="text-sm text-sophisticated-taupe">
          STT: Web Speech API (browser built-in)
        </p>
        <p className="text-sm text-sophisticated-taupe">
          TTS: SpeechSynthesis API (browser built-in)
        </p>
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