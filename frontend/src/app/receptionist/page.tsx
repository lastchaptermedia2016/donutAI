"use client";

import { useState, useEffect, useCallback } from "react";
import { useAppState } from "@/components/providers";
import { ContextMode, contextConfig, BACKEND_URL } from "@/lib/utils";
import {
  BarChart3,
  CheckSquare,
  Mail,
  Calendar,
  Clock,
  MessageSquare,
  User,
  Phone,
  Bell,
  AlertCircle,
  Send,
  Mic,
  MicOff,
  RefreshCw,
  Plus,
  X,
} from "lucide-react";

interface Appointment {
  id: string;
  client_name: string;
  client_contact: string;
  start_time: string;
  end_time: string;
  appointment_type: string;
  status: string;
}

interface Email {
  id: string;
  sender: string;
  subject: string;
  received_at: string;
  read: boolean;
}

interface Reminder {
  id: string;
  message: string;
  remind_at: string;
  active: boolean;
}

interface ReceptionistStatus {
  mode: string;
  business_name: string;
  working_hours: { start_hour: number; end_hour: number; slot_duration_minutes: number };
  total_unread_emails: number;
  upcoming_appointments: number;
  active_reminders: number;
}

export default function ReceptionistPage() {
  const { isDarkMode } = useAppState();
  const [status, setStatus] = useState<ReceptionistStatus | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [emails, setEmails] = useState<Email[]>([]);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [activeTab, setActiveTab] = useState<"overview" | "appointments" | "emails" | "reminders">("overview");
  const [loading, setLoading] = useState(true);
  const [showBookForm, setShowBookForm] = useState(false);
  const [newAppointment, setNewAppointment] = useState({
    client_name: "",
    client_contact: "",
    start_time: "",
    appointment_type: "general",
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [statusRes, apptsRes, emailsRes, remindersRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/receptionist/status`).then((r) => r.json()).catch(() => null),
        fetch(`${BACKEND_URL}/api/appointments`).then((r) => r.json()).catch(() => []),
        fetch(`${BACKEND_URL}/api/emails`).then((r) => r.json()).catch(() => []),
        fetch(`${BACKEND_URL}/api/reminders`).then((r) => r.json()).catch(() => []),
      ]);

      setStatus(statusRes);
      setAppointments(apptsRes);
      setEmails(emailsRes);
      setReminders(remindersRes);
    } catch (error) {
      console.error("Error fetching receptionist data:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleBookAppointment = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/appointments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...newAppointment,
          start_time: new Date(newAppointment.start_time).toISOString(),
          end_time: new Date(new Date(newAppointment.start_time).getTime() + 30 * 60000).toISOString(),
        }),
      });
      if (response.ok) {
        setShowBookForm(false);
        setNewAppointment({
          client_name: "",
          client_contact: "",
          start_time: "",
          appointment_type: "general",
        });
        fetchData();
      }
    } catch (error) {
      console.error("Error booking appointment:", error);
    }
  };

  const addDemoEmail = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/emails/demo/receive`, { method: "POST" });
      fetchData();
    } catch (error) {
      console.error("Error adding demo email:", error);
    }
  };

  if (loading && !status) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 to-stone-100 dark:from-stone-900 dark:to-stone-800 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-amber-600" />
          <p className="mt-2 text-stone-600 dark:text-stone-400">Loading receptionist dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-stone-100 dark:from-stone-900 dark:to-stone-800">
      {/* Header */}
      <header className="border-b border-stone-200 dark:border-stone-700 bg-white/60 dark:bg-stone-900/60 backdrop-blur-lg">
        <div className="mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🍩</span>
              <div>
                <h1 className="font-bold text-lg text-stone-800 dark:text-stone-200">
                  {status?.business_name || "Donut Receptionist"}
                </h1>
                <p className="text-xs text-stone-500 flex items-center gap-1">
                  <span className={`w-2 h-2 rounded-full ${status?.mode === "active" ? "bg-green-500" : "bg-red-500"}`} />
                  {status?.mode || "Unknown"}
                </p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchData}
              className="p-2 rounded-full hover:bg-stone-200 dark:hover:bg-stone-700"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={addDemoEmail}
              className="px-3 py-1 rounded-full bg-stone-600 text-white text-sm hover:bg-stone-700"
            >
              + Demo Email
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar Tabs */}
        <aside className="w-48 min-h-screen border-r border-stone-200 dark:border-stone-700 bg-white/40 dark:bg-stone-900/40 p-4">
          <nav className="space-y-2">
            {[
              { key: "overview", label: "Overview", icon: BarChart3 },
              { key: "appointments", label: "Appointments", icon: Calendar },
              { key: "emails", label: "Inbox", icon: Mail },
              { key: "reminders", label: "Reminders", icon: Bell },
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key as typeof activeTab)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  activeTab === key
                    ? "bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200 font-medium"
                    : "text-stone-600 dark:text-stone-400 hover:bg-stone-100 dark:hover:bg-stone-800"
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
                {key === "emails" && status && status.total_unread_emails > 0 && (
                  <span className="ml-auto bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-full">
                    {status.total_unread_emails}
                  </span>
                )}
              </button>
            ))}
          </nav>

          {/* Working Hours */}
          {status && (
            <div className="mt-8 p-3 bg-white/60 dark:bg-stone-800/60 rounded-lg">
              <h3 className="text-xs font-medium text-stone-500 uppercase mb-2">Working Hours</h3>
              <p className="text-sm text-stone-700 dark:text-stone-300">
                {status.working_hours?.start_hour ?? 9}:00 - {status.working_hours?.end_hour ?? 17}:00
              </p>
              <p className="text-xs text-stone-500 mt-1">
                {((status.working_hours?.end_hour ?? 17) - (status.working_hours?.start_hour ?? 9)) * 2} slots ({status.working_hours?.slot_duration_minutes ?? 30}min each)
              </p>
            </div>
          )}
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {activeTab === "overview" && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold text-stone-800 dark:text-stone-200">Dashboard Overview</h2>

              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatCard
                  icon={Calendar}
                  label="Today's Appointments"
                  value={appointments.length}
                  color="amber"
                />
                <StatCard
                  icon={Mail}
                  label="Unread Emails"
                  value={status?.total_unread_emails ?? 0}
                  color="blue"
                />
                <StatCard
                  icon={Bell}
                  label="Active Reminders"
                  value={status?.active_reminders ?? 0}
                  color="green"
                />
                <StatCard
                  icon={Clock}
                  label="Working Hours"
                  value={`${status?.working_hours?.start_hour ?? 9}-${status?.working_hours?.end_hour ?? 17}`}
                  color="purple"
                />
              </div>

              {/* Today's Schedule */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Upcoming Appointments */}
                <div className="bg-white dark:bg-stone-800 rounded-xl p-4 border border-stone-200 dark:border-stone-700">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-stone-800 dark:text-stone-200 flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-amber-600" />
                      Upcoming Appointments
                    </h3>
                    <button
                      onClick={() => setShowBookForm(true)}
                      className="p-1 rounded-full hover:bg-stone-100 dark:hover:bg-stone-700"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                  {appointments.length > 0 ? (
                    <div className="space-y-2">
                      {appointments.slice(0, 5).map((apt) => (
                        <div
                          key={apt.id}
                          className="flex items-center gap-3 p-2 rounded-lg bg-stone-50 dark:bg-stone-700/50"
                        >
                          <div className="w-2 h-2 rounded-full bg-amber-500" />
                          <div className="flex-1">
                            <p className="text-sm font-medium text-stone-800 dark:text-stone-200">{apt.client_name}</p>
                            <p className="text-xs text-stone-500">{apt.appointment_type}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs font-medium text-stone-700 dark:text-stone-300">
                              {new Date(apt.start_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                            </p>
                            <p className="text-xs text-stone-500">{apt.status}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-stone-500 p-4 text-center">No appointments scheduled</p>
                  )}
                </div>

                {/* Recent Emails */}
                <div className="bg-white dark:bg-stone-800 rounded-xl p-4 border border-stone-200 dark:border-stone-700">
                  <h3 className="font-semibold text-stone-800 dark:text-stone-200 flex items-center gap-2 mb-4">
                    <Mail className="w-4 h-4 text-blue-600" />
                    Recent Emails
                  </h3>
                  {emails.length > 0 ? (
                    <div className="space-y-2">
                      {emails.slice(0, 5).map((email) => (
                        <div
                          key={email.id}
                          className={`flex items-center gap-3 p-2 rounded-lg ${
                            !email.read ? "bg-blue-50 dark:bg-blue-900/20" : "bg-stone-50 dark:bg-stone-700/50"
                          }`}
                        >
                          <Mail className={`w-4 h-4 ${!email.read ? "text-blue-500" : "text-stone-400"}`} />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-stone-800 dark:text-stone-200 truncate">
                              {email.sender || "Unknown"}
                            </p>
                            <p className="text-xs text-stone-500 truncate">{email.subject}</p>
                          </div>
                          {!email.read && <Bell className="w-3 h-3 text-blue-500 flex-shrink-0" />}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-stone-500 p-4 text-center">No emails in inbox</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === "appointments" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-stone-800 dark:text-stone-200">Appointments</h2>
                <button
                  onClick={() => setShowBookForm(true)}
                  className="px-4 py-2 rounded-lg bg-amber-600 text-white hover:bg-amber-700 flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Book Appointment
                </button>
              </div>

              {showBookForm && (
                <div className="bg-white dark:bg-stone-800 rounded-xl p-4 border border-stone-200 dark:border-stone-700">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold">Book New Appointment</h3>
                    <button onClick={() => setShowBookForm(false)}>
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <input
                      type="text"
                      placeholder="Client Name"
                      value={newAppointment.client_name}
                      onChange={(e) => setNewAppointment({ ...newAppointment, client_name: e.target.value })}
                      className="px-3 py-2 rounded-lg border border-stone-200 dark:border-stone-600 bg-white dark:bg-stone-700"
                    />
                    <input
                      type="text"
                      placeholder="Contact Info"
                      value={newAppointment.client_contact}
                      onChange={(e) => setNewAppointment({ ...newAppointment, client_contact: e.target.value })}
                      className="px-3 py-2 rounded-lg border border-stone-200 dark:border-stone-600 bg-white dark:bg-stone-700"
                    />
                    <input
                      type="datetime-local"
                      value={newAppointment.start_time}
                      onChange={(e) => setNewAppointment({ ...newAppointment, start_time: e.target.value })}
                      className="px-3 py-2 rounded-lg border border-stone-200 dark:border-stone-600 bg-white dark:bg-stone-700"
                    />
                    <select
                      value={newAppointment.appointment_type}
                      onChange={(e) => setNewAppointment({ ...newAppointment, appointment_type: e.target.value })}
                      className="px-3 py-2 rounded-lg border border-stone-200 dark:border-stone-600 bg-white dark:bg-stone-700"
                    >
                      <option value="general">General</option>
                      <option value="consultation">Consultation</option>
                      <option value="followup">Follow-up</option>
                      <option value="urgent">Urgent</option>
                    </select>
                  </div>
                  <button
                    onClick={handleBookAppointment}
                    disabled={!newAppointment.client_name || !newAppointment.start_time}
                    className="mt-4 px-4 py-2 rounded-lg bg-amber-600 text-white hover:bg-amber-700 disabled:opacity-50"
                  >
                    Confirm Booking
                  </button>
                </div>
              )}

              <div className="space-y-2">
                {appointments.length > 0 ? (
                  appointments.map((apt) => (
                    <div
                      key={apt.id}
                      className="bg-white dark:bg-stone-800 rounded-xl p-4 border border-stone-200 dark:border-stone-700 flex items-center gap-4"
                    >
                      <div className="p-2 rounded-full bg-amber-100 dark:bg-amber-900/30">
                        <Calendar className="w-5 h-5 text-amber-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-stone-800 dark:text-stone-200">{apt.client_name}</p>
                        <p className="text-sm text-stone-500">{apt.client_contact} · {apt.appointment_type}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-stone-700 dark:text-stone-300">
                          {new Date(apt.start_time).toLocaleDateString()}
                        </p>
                        <p className="text-sm text-stone-500">
                          {new Date(apt.start_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                        </p>
                      </div>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          apt.status === "confirmed"
                            ? "bg-green-100 dark:bg-green-900/30 text-green-700"
                            : "bg-stone-100 dark:bg-stone-700 text-stone-600"
                        }`}
                      >
                        {apt.status}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12">
                    <Calendar className="w-12 h-12 mx-auto text-stone-400 mb-4" />
                    <p className="text-stone-500">No appointments scheduled</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "emails" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-stone-800 dark:text-stone-200">Inbox</h2>
                <button
                  onClick={addDemoEmail}
                  className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Demo Email
                </button>
              </div>
              <div className="space-y-2">
                {emails.length > 0 ? (
                  emails.map((email) => (
                    <div
                      key={email.id}
                      className={`bg-white dark:bg-stone-800 rounded-xl p-4 border border-stone-200 dark:border-stone-700 flex items-start gap-4 ${
                        !email.read ? "ring-2 ring-blue-200 dark:ring-blue-800" : ""
                      }`}
                    >
                      <div className="p-2 rounded-full bg-blue-100 dark:bg-blue-900/30 flex-shrink-0">
                        <Mail className="w-5 h-5 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="font-medium text-stone-800 dark:text-stone-200">
                            {email.sender || "Unknown Sender"}
                          </p>
                          {!email.read && (
                            <Bell className="w-3 h-3 text-blue-500" />
                          )}
                        </div>
                        <p className="text-sm font-medium text-stone-700 dark:text-stone-300">{email.subject}</p>
                        <p className="text-xs text-stone-500 mt-1">
                          {email.received_at
                            ? new Date(email.received_at).toLocaleString()
                            : "Just now"}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12">
                    <Mail className="w-12 h-12 mx-auto text-stone-400 mb-4" />
                    <p className="text-stone-500">No emails in inbox</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "reminders" && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-stone-800 dark:text-stone-200">Reminders</h2>
              <div className="space-y-2">
                {reminders.length > 0 ? (
                  reminders.map((reminder) => (
                    <div
                      key={reminder.id}
                      className="bg-white dark:bg-stone-800 rounded-xl p-4 border border-stone-200 dark:border-stone-700 flex items-center gap-4"
                    >
                      <div className="p-2 rounded-full bg-green-100 dark:bg-green-900/30 flex-shrink-0">
                        <Bell className="w-5 h-5 text-green-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-stone-800 dark:text-stone-200">{reminder.message}</p>
                        <p className="text-xs text-stone-500">
                          {reminder.remind_at
                            ? new Date(reminder.remind_at).toLocaleString()
                            : ""}
                        </p>
                      </div>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          reminder.active
                            ? "bg-green-100 dark:bg-green-900/30 text-green-700"
                            : "bg-stone-100 dark:bg-stone-700 text-stone-600"
                        }`}
                      >
                        {reminder.active ? "Active" : "Inactive"}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12">
                    <Bell className="w-12 h-12 mx-auto text-stone-400 mb-4" />
                    <p className="text-stone-500">No reminders set</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: any;
  label: string;
  value: string | number;
  color: string;
}) {
  const colorMap: Record<string, string> = {
    amber: "bg-amber-100 dark:bg-amber-900/30 text-amber-600",
    blue: "bg-blue-100 dark:bg-blue-900/30 text-blue-600",
    green: "bg-green-100 dark:bg-green-900/30 text-green-600",
    purple: "bg-purple-100 dark:bg-purple-900/30 text-purple-600",
  };

  return (
    <div className="bg-white dark:bg-stone-800 rounded-xl p-4 border border-stone-200 dark:border-stone-700">
      <div className="flex items-center gap-3">
        <div className={`p-2.5 rounded-lg ${colorMap[color] || colorMap.amber}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <p className="text-xs text-stone-500 uppercase">{label}</p>
          <p className="text-xl font-bold text-stone-800 dark:text-stone-200">{value}</p>
        </div>
      </div>
    </div>
  );
}