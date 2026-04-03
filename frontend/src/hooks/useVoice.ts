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
  permissionStatus: 'granted' | 'denied' | 'prompt' | 'unknown';
}

export function useVoice({
  onResult,
  onError,
  lang = "en-US",
}: UseVoiceOptions = {}): UseVoiceReturn {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [permissionStatus, setPermissionStatus] = useState<'granted' | 'denied' | 'prompt' | 'unknown'>('unknown');
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
      const errorMessage = "Voice functionality is not supported in this browser. Please use Chrome, Edge, or Safari.";
      console.error(errorMessage);
      setError(errorMessage);
      
      // Clear error after 8 seconds
      const timer = setTimeout(() => {
        setError(null);
      }, 8000);
      
      return () => clearTimeout(timer);
    }
  }, [isSupported]);

  // Check microphone permissions
  useEffect(() => {
    if (typeof window !== "undefined" && navigator.mediaDevices) {
      navigator.permissions?.query({ name: 'microphone' as PermissionName })
        .then((status) => {
          setPermissionStatus(status.state as 'granted' | 'denied' | 'prompt');
          status.addEventListener('change', () => {
            setPermissionStatus(status.state as 'granted' | 'denied' | 'prompt');
          });
        })
        .catch(() => {
          setPermissionStatus('unknown');
        });
    }
  }, []);

  useEffect(() => {
    if (!isSupported) return;

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = lang;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    recognition.onresult = (event: any) => {
      let fullTranscript = transcript;
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPart = event.results[i][0].transcript;
        fullTranscript = event.results[i].isFinal 
          ? transcriptPart.trim() 
          : transcriptPart;
      }
      
      setTranscript(fullTranscript);

      if (event.results[event.resultIndex]?.isFinal) {
        onResult?.(fullTranscript.trim());
      }
    };

    recognition.onerror = (event: any) => {
      console.error("Speech recognition error:", event.error);
      
      let userMessage = "Voice recognition error";
      
      switch(event.error) {
        case 'not-allowed':
          userMessage = "Microphone permission denied. Please allow microphone access in your browser settings.";
          setPermissionStatus('denied');
          break;
        case 'no-speech':
          userMessage = "No speech detected. Try speaking louder.";
          break;
        case 'audio-capture':
          userMessage = "No microphone detected. Please check your audio device.";
          break;
        case 'network':
          userMessage = "Network error. Check your internet connection.";
          break;
      }
      
      setError(userMessage);
      onError?.(new Error(userMessage));
      setIsListening(false);

      // Auto-clear non-critical errors after 4 seconds
      if (event.error !== 'not-allowed') {
        setTimeout(() => setError(null), 4000);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.onend = null;
      recognition.onerror = null;
      try {
        recognition.abort();
      } catch (e) {
        // Ignore abort errors
      }
    };
  }, [onResult, onError, lang, isSupported, transcript]);

  const startListening = useCallback(() => {
    if (!recognitionRef.current) {
      setError("Voice recognition not available");
      return;
    }

    if (permissionStatus === 'denied') {
      setError("Microphone permission blocked. Please enable it in your browser settings.");
      return;
    }

    setTranscript("");
    setError(null);
    
    try {
      if (isListening) {
        recognitionRef.current.stop();
        setTimeout(() => recognitionRef.current.start(), 100);
      } else {
        recognitionRef.current.start();
      }
    } catch (e: any) {
      if (e.name === 'InvalidStateError') {
        // Already running, restart after short delay
        setTimeout(() => {
          try {
            recognitionRef.current.start();
          } catch {}
        }, 200);
      } else {
        console.error("Failed to start recognition:", e);
        setError("Failed to activate microphone. Please try again.");
      }
    }
  }, [isListening, permissionStatus]);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current) return;
    
    try {
      recognitionRef.current.stop();
      setIsListening(false);
    } catch (e) {
      // Already stopped, ignore
    }
  }, []);

  return {
    isListening,
    transcript,
    startListening,
    stopListening,
    isSupported,
    error,
    permissionStatus,
  };
}
