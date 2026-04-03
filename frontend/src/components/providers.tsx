"use client";

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";
import { ContextMode } from "@/lib/utils";
import { ErrorBoundary } from "./error-boundary";

// App state context
interface AppState {
  contextMode: ContextMode;
  setContextMode: (mode: ContextMode) => void;
  sessionId: string;
  isDarkMode: boolean;
  toggleDarkMode: () => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

const AppStateContext = createContext<AppState | undefined>(undefined);

export function Providers({ children }: { children: ReactNode }) {
  const [contextMode, setContextMode] = useState<ContextMode>("neutral");
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleDarkMode = useCallback(() => {
    setIsDarkMode((prev) => {
      const next = !prev;
      if (typeof window !== "undefined") {
        document.documentElement.classList.toggle("dark", next);
      }
      return next;
    });
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      setIsDarkMode(prefersDark);
      document.documentElement.classList.toggle("dark", prefersDark);
    }
  }, []);

  return (
    <ErrorBoundary>
      <AppStateContext.Provider
        value={{
          contextMode,
          setContextMode,
          sessionId,
          isDarkMode,
          toggleDarkMode,
          sidebarOpen,
          setSidebarOpen,
        }}
      >
        {children}
      </AppStateContext.Provider>
    </ErrorBoundary>
  );
}

export function useAppState() {
  const context = useContext(AppStateContext);
  if (context === undefined) {
    throw new Error("useAppState must be used within a Providers");
  }
  return context;
}