"use client";

import { useState, useRef, useCallback, useEffect } from "react";

interface UseWakeWordDetectionOptions {
  onWakeWordDetected?: () => void;
  wakeWord?: string;
  sensitivity?: number;
}

interface UseWakeWordDetectionReturn {
  isStandby: boolean;
  isListening: boolean;
  startStandby: () => void;
  stopStandby: () => void;
  isSupported: boolean;
  error: string | null;
  permissionStatus: 'granted' | 'denied' | 'prompt' | 'unknown';
}

export function useWakeWordDetection({
  onWakeWordDetected,
  wakeWord = "donut",
  sensitivity = 0.8,
}: UseWakeWordDetectionOptions = {}): UseWakeWordDetectionReturn {
  const [isStandby, setIsStandby] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [permissionStatus, setPermissionStatus] = useState<'granted' | 'denied' | 'prompt' | 'unknown'>('unknown');
  const recognitionRef = useRef<any>(null);
  const standbyTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const permissionRequestedRef = useRef(false);

  const isSupported =
    typeof window !== "undefined" &&
    !!(
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition
    );

  // Check for browser compatibility
  useEffect(() => {
    if (!isSupported && typeof window !== "undefined") {
      const errorMessage = "Wake word detection is not supported in this browser. Please use Chrome, Edge, or Safari.";
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

  // Initialize SpeechRecognition for wake word detection
  useEffect(() => {
    if (!isSupported) return;

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = true; // Keep listening for wake word
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 3;

    recognition.onstart = () => {
      console.log("Wake word detection started");
      setIsListening(true);
      setError(null);
    };

    recognition.onresult = (event: any) => {
      let finalTranscript = "";
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPart = event.results[i][0].transcript.toLowerCase();
        if (event.results[i].isFinal) {
          finalTranscript += transcriptPart.trim();
        }
      }
      
      // Check if wake word is detected in the transcript
      if (finalTranscript) {
        const wakeWordVariants = [
          wakeWord.toLowerCase(),
          `hey ${wakeWord.toLowerCase()}`,
          `ok ${wakeWord.toLowerCase()}`,
          `hello ${wakeWord.toLowerCase()}`,
        ];
        
        const detected = wakeWordVariants.some(variant => 
          finalTranscript.includes(variant)
        );
        
        if (detected) {
          console.log(`Wake word "${wakeWord}" detected!`);
          onWakeWordDetected?.();
          
          // Stop standby mode after detection
          stopStandby();
        }
      }
    };

    recognition.onerror = (event: any) => {
      console.error("Wake word detection error:", event.error);
      
      let userMessage = "Wake word detection error";
      
      switch(event.error) {
        case 'not-allowed':
          userMessage = "Microphone permission denied. Please allow microphone access.";
          setPermissionStatus('denied');
          break;
        case 'no-speech':
          // Don't show error for no speech - just keep listening
          return;
        case 'audio-capture':
          userMessage = "No microphone detected.";
          break;
        case 'network':
          userMessage = "Network error. Check your internet connection.";
          break;
        case 'aborted':
          console.log("Wake word detection aborted");
          return;
        default:
          userMessage = `Voice error: ${event.error}`;
      }
      
      setError(userMessage);
      setIsStandby(false);
      setIsListening(false);

      // Auto-clear non-critical errors after 6 seconds
      if (event.error !== 'not-allowed') {
        setTimeout(() => setError(null), 6000);
      }
    };

    recognition.onend = () => {
      console.log("Wake word detection ended");
      setIsListening(false);
      
      // Auto-restart if we're still in standby mode
      if (isStandby && recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch (e) {
          console.log("Failed to restart wake word detection:", e);
        }
      }
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
  }, [onWakeWordDetected, wakeWord, isStandby, isSupported]);

  // Function to explicitly request microphone permission
  const requestMicrophoneAccess = useCallback(async (): Promise<boolean> => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.error("getUserMedia not supported");
      return false;
    }

    try {
      console.log("Requesting microphone access for wake word detection...");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Immediately stop all tracks - we just needed permission
      stream.getTracks().forEach(track => {
        console.log("Stopping microphone track:", track.kind);
        track.stop();
      });
      
      setPermissionStatus('granted');
      permissionRequestedRef.current = true;
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
      
      permissionRequestedRef.current = true;
      return false;
    }
  }, []);

  const startStandby = useCallback(async () => {
    console.log("startStandby called");
    console.log("  isStandby:", isStandby);
    console.log("  permissionStatus:", permissionStatus);
    console.log("  isSupported:", isSupported);
    console.log("  recognitionRef.current:", !!recognitionRef.current);

    if (!isSupported) {
      setError("Wake word detection is not supported in this browser. Please use Chrome, Edge, or Safari.");
      return;
    }

    if (!recognitionRef.current) {
      setError("Wake word detection not available. Please try refreshing the page.");
      return;
    }

    if (permissionStatus === 'denied') {
      setError("Microphone permission was denied. Please enable it in your browser settings and refresh the page.");
      return;
    }

    // If permission hasn't been requested yet or is unknown/prompt, request it first
    if (!permissionRequestedRef.current || permissionStatus === 'prompt' || permissionStatus === 'unknown') {
      console.log("Requesting microphone permission first...");
      const granted = await requestMicrophoneAccess();
      if (!granted) {
        return;
      }
    }

    // Clear any existing error
    setError(null);
    setIsStandby(true);
    
    try {
      if (isListening) {
        console.log("Already listening, stopping first...");
        recognitionRef.current.stop();
        // Wait a bit before restarting
        setTimeout(() => {
          try {
            console.log("Restarting wake word detection...");
            recognitionRef.current.start();
          } catch (e) {
            console.error("Failed to restart recognition:", e);
            setError("Failed to start wake word detection. Please try again.");
          }
        }, 200);
      } else {
        console.log("Starting wake word detection...");
        recognitionRef.current.start();
      }
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
            setError("Failed to start wake word detection. Please try again.");
          }
        }, 300);
      } else {
        setError("Failed to activate wake word detection. Please try again.");
      }
    }
  }, [isStandby, isListening, permissionStatus, isSupported, requestMicrophoneAccess]);

  const stopStandby = useCallback(() => {
    if (!recognitionRef.current) return;
    
    try {
      console.log("Stopping wake word detection...");
      recognitionRef.current.stop();
      setIsStandby(false);
      setIsListening(false);
    } catch (e) {
      console.log("Already stopped or error:", e);
    }
  }, []);

  return {
    isStandby,
    isListening,
    startStandby,
    stopStandby,
    isSupported,
    error,
    permissionStatus,
  };
}