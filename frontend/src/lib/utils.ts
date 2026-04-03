import { useState } from "react";
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTime(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function formatDate(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleDateString([], {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function formatRelative(date: string | Date): string {
  const now = new Date();
  const d = new Date(date);
  const diff = now.getTime() - d.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return formatDate(date);
}

export type ContextMode = "business" | "personal" | "neutral";

export const contextConfig: Record<
  ContextMode,
  { label: string; icon: string; gradient: string; color: string }
> = {
  business: {
    label: "Business",
    icon: "💼",
    gradient: "business-gradient",
    color: "text-blue-600 dark:text-blue-400",
  },
  personal: {
    label: "Personal",
    icon: "🏠",
    gradient: "personal-gradient",
    color: "text-green-600 dark:text-green-400",
  },
  neutral: {
    label: "Neutral",
    icon: "⚡",
    gradient: "neutral-gradient",
    color: "text-stone-600 dark:text-stone-400",
  },
};

export const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${BACKEND_URL}${path}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  // Always call useState - hooks must be called in the same order every time
  const [value, setValue] = useState<T>(() => {
    // Handle SSR - return initial value on server
    if (typeof window === "undefined") return initialValue;
    
    // On client, try to get from localStorage
    try {
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setStored = (newValue: T | ((prev: T) => T)) => {
    try {
      const resolved =
        typeof newValue === "function"
          ? (newValue as (prev: T) => T)(value)
          : newValue;
      setValue(resolved);
      localStorage.setItem(key, JSON.stringify(resolved));
    } catch (error) {
      console.error("Error saving to localStorage:", error);
    }
  };

  return [value, setStored];
}
