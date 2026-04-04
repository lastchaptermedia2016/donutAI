"use client";

import { useState, useEffect, useRef } from "react";
import { Mic, MicOff, RefreshCw, CheckCircle, XCircle, AlertCircle } from "lucide-react";

export default function MicTestPage() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [permissionStatus, setPermissionStatus] = useState<'granted' | 'denied' | 'prompt' | 'unknown'>('unknown');
  const [isSupported, setIsSupported] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const recognitionRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationRef = useRef<number>();

  // Check browser support
  useEffect(() => {
    const supported = !!(
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition
    );
    setIsSupported(supported);
  }, []);

  // Check permissions
  useEffect(() => {
    if (navigator.permissions) {
      navigator.permissions.query({ name: 'microphone' as PermissionName })
        .then((status) => {
          setPermissionStatus(status.state as any);
          status.addEventListener('change', () => {
            setPermissionStatus(status.state as any);
          });
        })
        .catch(() => setPermissionStatus('unknown'));
    }
  }, []);

  // Initialize speech recognition
  useEffect(() => {
    if (!isSupported) return;

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
      startAudioMonitoring();
    };

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPart = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcriptPart.trim();
        }
      }
      if (finalTranscript) {
        setTranscript(finalTranscript);
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setError(event.error);
      setIsListening(false);
      stopAudioMonitoring();
    };

    recognition.onend = () => {
      setIsListening(false);
      stopAudioMonitoring();
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.abort();
      stopAudioMonitoring();
    };
  }, [isSupported]);

  const startAudioMonitoring = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContextRef.current = new AudioContext();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      source.connect(analyserRef.current);
      
      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
      
      const updateLevel = () => {
        if (!analyserRef.current) return;
        analyserRef.current.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        setAudioLevel(Math.min(100, average));
        animationRef.current = requestAnimationFrame(updateLevel);
      };
      
      updateLevel();
    } catch (err) {
      console.error('Failed to start audio monitoring:', err);
    }
  };

  const stopAudioMonitoring = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    setAudioLevel(0);
  };

  const toggleListening = async () => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      setTranscript("");
      setError(null);
      
      // Request permission first if needed
      if (permissionStatus === 'prompt' || permissionStatus === 'unknown') {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          stream.getTracks().forEach(track => track.stop());
          setPermissionStatus('granted');
        } catch (err) {
          setPermissionStatus('denied');
          setError('Microphone permission denied');
          return;
        }
      }
      
      recognitionRef.current.start();
    }
  };

  const getStatusColor = () => {
    switch (permissionStatus) {
      case 'granted': return 'bg-green-500';
      case 'denied': return 'bg-red-500';
      case 'prompt': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-2">🎤 Microphone Test</h1>
        <p className="text-purple-200 mb-8">Test and diagnose microphone functionality</p>

        {/* Status Cards */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor()} animate-pulse`} />
              <span className="text-sm text-purple-200">Permission Status</span>
            </div>
            <p className="text-2xl font-bold text-white capitalize">{permissionStatus}</p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
            <div className="flex items-center gap-2 mb-2">
              {isSupported ? (
                <CheckCircle className="w-4 h-4 text-green-400" />
              ) : (
                <XCircle className="w-4 h-4 text-red-400" />
              )}
              <span className="text-sm text-purple-200">Browser Support</span>
            </div>
            <p className="text-2xl font-bold text-white">{isSupported ? 'Yes' : 'No'}</p>
          </div>
        </div>

        {/* Audio Level Meter */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 mb-8">
          <h3 className="text-lg font-semibold text-white mb-4">Audio Level</h3>
          <div className="h-16 bg-black/30 rounded-lg overflow-hidden flex items-end">
            <div 
              className="bg-gradient-to-t from-green-500 via-yellow-500 to-red-500 transition-all duration-100 ease-out"
              style={{ 
                width: '100%', 
                height: `${audioLevel}%`,
                opacity: isListening ? 1 : 0.3
              }}
            />
          </div>
          <p className="text-sm text-purple-200 mt-2">
            {isListening ? `Level: ${Math.round(audioLevel)}%` : 'Click the mic button to start'}
          </p>
        </div>

        {/* Microphone Button */}
        <div className="flex justify-center mb-8">
          <button
            onClick={toggleListening}
            disabled={!isSupported}
            className={`
              w-24 h-24 rounded-full flex items-center justify-center
              transition-all duration-300 transform
              ${isListening 
                ? 'bg-red-500 hover:bg-red-600 animate-pulse scale-110' 
                : 'bg-gradient-to-br from-purple-500 to-pink-500 hover:scale-105'
              }
              ${!isSupported ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            {isListening ? (
              <MicOff className="w-12 h-12 text-white" />
            ) : (
              <Mic className="w-12 h-12 text-white" />
            )}
          </button>
        </div>

        {/* Transcript Display */}
        {transcript && (
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 mb-8">
            <h3 className="text-lg font-semibold text-white mb-2">Transcript</h3>
            <p className="text-xl text-purple-100">{transcript}</p>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-500/20 backdrop-blur-lg rounded-xl p-6 border border-red-500/30 mb-8">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-5 h-5 text-red-400" />
              <h3 className="text-lg font-semibold text-red-400">Error</h3>
            </div>
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {/* Troubleshooting Tips */}
        <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4">Troubleshooting Tips</h3>
          <ul className="space-y-2 text-purple-200 text-sm">
            <li>• Make sure your browser has permission to access the microphone</li>
            <li>• Check that your microphone is not muted in system settings</li>
            <li>• Try using Chrome or Edge for best compatibility</li>
            <li>• Ensure no other application is exclusively using the microphone</li>
            <li>• If using HTTPS, make sure the certificate is valid</li>
            <li>• Check browser console for detailed error messages</li>
          </ul>
        </div>

        {/* Reset Button */}
        <div className="mt-8 text-center">
          <button
            onClick={() => {
              setTranscript("");
              setError(null);
              setAudioLevel(0);
              if (isListening && recognitionRef.current) {
                recognitionRef.current.stop();
              }
            }}
            className="flex items-center gap-2 mx-auto px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-purple-200 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Reset Test
          </button>
        </div>
      </div>
    </div>
  );
}