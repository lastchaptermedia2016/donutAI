"use client";

import { useState, useEffect, useRef, useCallback } from "react";

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
  const finalTranscriptRef = useRef("");
  const onResultRef = useRef(onResult);
  const onErrorRef = useRef(onError);

  // Update refs to avoid stale closures
  onResultRef.current = onResult;
  onErrorRef.current = onError;

  const isSupported =
    typeof window !== "undefined" &&
    !!(
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition
    );

  // Check for browser compatibility
  useEffect(() => {
    if (!isSupported && typeof window !== "undefined") {
      const errorMessage = "Voice functionality is not supported in this browser. Please use Chrome, Edge, or Safari.";
      console.error(errorMessage);
      setError(errorMessage);
      
      const timer = setTimeout(() => {
        setError(null);
      }, 8000);
      
      return () => clearTimeout(timer);
    }
  }, [isSupported]);

  // Check microphone permissions on mount
  useEffect(() => {
    if (typeof window !== "undefined" && navigator.permissions) {
      navigator.permissions.query({ name: 'microphone' as PermissionName })
        .then((status) => {
          console.log("Microphone permission status:", status.state);
          setPermissionStatus(status.state as 'granted' | 'denied' | 'prompt');
          status.addEventListener('change', () => {
            console.log("Microphone permission changed to:", status.state);
            setPermissionStatus(status.state as 'granted' | 'denied' | 'prompt');
          });
        })
        .catch((err) => {
          console.warn("Could not check microphone permission:", err);
          setPermissionStatus('unknown');
        });
    }
  }, []);

  // Initialize SpeechRecognition - only once with empty dependency array
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
      console.log("Speech recognition started");
      setIsListening(true);
      setError(null);
    };

    recognition.onresult = (event: any) => {
      let interim = "";
      let final = "";

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          final += result[0].transcript;
        } else {
          interim += result[0].transcript;
        }
      }

      if (final) {
        finalTranscriptRef.current = final;
        setTranscript(final);
        console.log("Final transcript received:", final);
        onResultRef.current?.(final);
      } else if (interim) {
        setTranscript(interim);
      }
    };

    recognition.onerror = (event: any) => {
      console.error("Speech recognition error:", event.error);
      
      let userMessage = "Voice recognition error";
      
      switch(event.error) {
        case 'not-allowed':
          userMessage = "Microphone permission denied. Please allow microphone access in your browser settings, then refresh the page.";
          setPermissionStatus('denied');
          break;
        case 'no-speech':
          userMessage = "No speech detected. Try speaking louder or check your microphone.";
          break;
        case 'audio-capture':
          userMessage = "No microphone detected. Please connect a microphone and try again.";
          break;
        case 'network':
          userMessage = "Network error. Check your internet connection.";
          break;
        case 'aborted':
          console.log("Speech recognition aborted by user");
          return;
        case 'service-not-allowed':
          userMessage = "Speech recognition service not available. Try again later.";
          break;
        default:
          userMessage = `Voice error: ${event.error}`;
      }
      
      setError(userMessage);
      onErrorRef.current?.(new Error(userMessage));
      setIsListening(false);

      // Auto-clear non-critical errors after 6 seconds
      if (event.error !== 'not-allowed') {
        setTimeout(() => setError(null), 6000);
      }
    };

    recognition.onend = () => {
      console.log("Speech recognition ended");
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
  }, [isSupported]); // Only depend on isSupported, not callbacks or lang

  // Function to explicitly request microphone permission
  const requestMicrophoneAccess = useCallback(async (): Promise<boolean> => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.error("getUserMedia not supported");
      return false;
    }

    try {
      console.log("Requesting microphone access...");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Immediately stop all tracks - we just needed permission
      stream.getTracks().forEach(track => {
        console.log("Stopping microphone track:", track.kind);
        track.stop();
      });
      
      setPermissionStatus('granted');
      console.log("Microphone permission granted!");
      return true;
    } catch (err: any) {
      console.error("Microphone permission denied:", err.name, err.message);
      
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setPermissionStatus('denied');
        setError("Microphone permission was denied. Please enable it in your browser settings and refresh the page.");
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setError("No microphone found. Please connect a microphone and try again.");
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        setError("Microphone is in use by another application. Please close other apps using the microphone.");
      } else {
        setError(`Microphone error: ${err.message}`);
      }
      
      return false;
    }
  }, []);

  const startListening = useCallback(async () => {
    console.log("startListening called");
    console.log("  isListening:", isListening);
    console.log("  permissionStatus:", permissionStatus);
    console.log("  isSupported:", isSupported);
    console.log("  recognitionRef.current:", !!recognitionRef.current);

    if (!isSupported) {
      setError("Voice recognition is not supported in this browser. Please use Chrome, Edge, or Safari.");
      return;
    }

    if (!recognitionRef.current) {
      setError("Voice recognition not available. Please try refreshing the page.");
      return;
    }

    if (permissionStatus === 'denied') {
      setError("Microphone permission was denied. Please enable it in your browser settings and refresh the page.");
      return;
    }

    // If permission hasn't been granted yet, request it first
    if (permissionStatus === 'prompt' || permissionStatus === 'unknown') {
      console.log("Requesting microphone permission first...");
      const granted = await requestMicrophoneAccess();
      if (!granted) {
        return;
      }
    }

    // Don't start if already listening
    if (isListening) {
      console.log("Already listening, ignoring start request");
      return;
    }

    // Clear any existing error and transcript
    setTranscript("");
    finalTranscriptRef.current = "";
    setError(null);
    
    try {
      console.log("Starting speech recognition...");
      recognitionRef.current.start();
    } catch (e: any) {
      console.error("Error starting recognition:", e);
      
      if (e.name === 'InvalidStateError') {
        console.log("InvalidStateError - recognition already running, restarting...");
        try {
          recognitionRef.current.stop();
        } catch {}
        setTimeout(() => {
          try {
            recognitionRef.current.start();
          } catch (e2) {
            console.error("Failed to start after stop:", e2);
            setError("Failed to start microphone. Please try again.");
          }
        }, 300);
      } else {
        setError("Failed to activate microphone. Please try again.");
      }
    }
  }, [isListening, permissionStatus, isSupported, requestMicrophoneAccess]);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current) return;
    
    try {
      console.log("Stopping speech recognition...");
      recognitionRef.current.stop();
    } catch (e) {
      console.log("Already stopped or error:", e);
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