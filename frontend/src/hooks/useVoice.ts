"use client";

import { useState, useRef, useCallback, useEffect } from "react";

interface UseVoiceOptions {
  onResult?: (text: string) => void;
  onError?: (error: Error) => void;
  lang?: string;
}

interface UseVoiceReturn {
  isListening: boolean;
  transcript: string;
  startListening: () => void;
  stopListening: () => void;
  isSupported: boolean;
  error: string | null;
}

export function useVoice({
  onResult,
  onError,
  lang = "en-US",
}: UseVoiceOptions = {}): UseVoiceReturn {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);

  const isSupported =
    typeof window !== "undefined" &&
    !!(
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition
    );

  // Check for browser compatibility and provide user feedback via state
  useEffect(() => {
    if (!isSupported && typeof window !== "undefined") {
      const errorMessage = "Voice functionality is not supported in this browser. Please use Chrome, Firefox, or Edge.";
      console.error(errorMessage);
      setError(errorMessage);
      
      // Clear error after 5 seconds
      const timer = setTimeout(() => {
        setError(null);
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [isSupported]);

  useEffect(() => {
    if (!isSupported) return;

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = lang;

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event: any) => {
      let currentTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        currentTranscript += event.results[i][0].transcript;
      }
      setTranscript(currentTranscript);

      if (event.results[0].isFinal) {
        onResult?.(currentTranscript);
      }
    };
    recognition.onerror = (event: any) => {
      const error = new Error(
        `Speech recognition error: ${event.error || event.message}`
      );
      onError?.(error);
      setIsListening(false);
    };
    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;

    return () => {
      recognition.onend = null;
      recognition.abort?.();
    };
  }, [onResult, onError, lang, isSupported]);

  const startListening = useCallback(() => {
    if (!recognitionRef.current) return;
    setTranscript("");
    try {
      recognitionRef.current.start();
    } catch (e) {
      // Already running
    }
  }, []);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current) return;
    try {
      recognitionRef.current.stop();
    } catch (e) {
      // Already stopped
    }
  }, []);

  return {
    isListening,
    transcript,
    startListening,
    stopListening,
    isSupported,
    error,
  };
}