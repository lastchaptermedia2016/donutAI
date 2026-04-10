"use client";

import { useState, useRef, useEffect } from "react";
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Music, X } from "lucide-react";

interface MusicTrack {
  id: string;
  title: string;
  artist: string;
  duration: string;
  audioUrl: string;
  watchUrl: string;
}

interface MusicPlayerProps {
  track: MusicTrack | null;
  onClose: () => void;
}

export function MusicPlayer({ track, onClose }: MusicPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [isMuted, setIsMuted] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressRef = useRef<HTMLInputElement>(null);

  // Auto-play when track changes
  useEffect(() => {
    if (track && audioRef.current) {
      setIsPlaying(true);
      setCurrentTime(0);
    }
  }, [track]);

  // Handle play/pause
  const togglePlay = () => {
    if (!audioRef.current) return;
    
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play().catch(e => console.log("Playback failed:", e));
    }
    setIsPlaying(!isPlaying);
  };

  // Handle time update
  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  // Handle loaded metadata
  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  // Handle seek
  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
    setCurrentTime(time);
  };

  // Handle volume change
  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const vol = parseFloat(e.target.value);
    setVolume(vol);
    if (audioRef.current) {
      audioRef.current.volume = vol;
    }
    setIsMuted(vol === 0);
  };

  // Toggle mute
  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  // Format time (seconds to MM:SS)
  const formatTime = (time: number) => {
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Handle playback ended
  const handleEnded = () => {
    setIsPlaying(false);
    setCurrentTime(0);
  };

  if (!track) return null;

  return (
    <div className="fixed bottom-24 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md animate-slide-up">
      <div className="glass-card rounded-2xl p-4 border border-billionaire-gold-500/20 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Music className="w-5 h-5 text-billionaire-gold-400" />
            <span className="text-sm font-medium text-billionaire-platinum/80">Now Playing</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-full hover:bg-billionaire-gold-500/10 transition-colors"
          >
            <X className="w-4 h-4 text-billionaire-platinum/60" />
          </button>
        </div>

        {/* Track Info */}
        <div className="mb-4">
          <h3 className="text-lg font-bold text-billionaire-gold-400 truncate">
            {track.title}
          </h3>
          <p className="text-sm text-billionaire-platinum/60 truncate">
            {track.artist}
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <input
            ref={progressRef}
            type="range"
            min="0"
            max={duration || 100}
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-1 bg-billionaire-platinum/20 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-billionaire-gold-500"
          />
          <div className="flex justify-between text-xs text-billionaire-platinum/50 mt-1">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between">
          {/* Volume */}
          <div className="flex items-center gap-2">
            <button
              onClick={toggleMute}
              className="p-2 rounded-full hover:bg-billionaire-gold-500/10 transition-colors"
            >
              {isMuted ? (
                <VolumeX className="w-4 h-4 text-billionaire-platinum/60" />
              ) : (
                <Volume2 className="w-4 h-4 text-billionaire-platinum/60" />
              )}
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={isMuted ? 0 : volume}
              onChange={handleVolumeChange}
              className="w-16 h-1 bg-billionaire-platinum/20 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-2 [&::-webkit-slider-thumb]:h-2 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-billionaire-platinum/60"
            />
          </div>

          {/* Play/Pause */}
          <button
            onClick={togglePlay}
            className="w-12 h-12 rounded-full bg-billionaire-gold-500 flex items-center justify-center hover:bg-billionaire-gold-400 transition-colors"
          >
            {isPlaying ? (
              <Pause className="w-5 h-5 text-billionaire-charcoal" />
            ) : (
              <Play className="w-5 h-5 text-billionaire-charcoal ml-0.5" />
            )}
          </button>

          {/* Skip (placeholder) */}
          <div className="flex items-center gap-2">
            <button
              className="p-2 rounded-full hover:bg-billionaire-gold-500/10 transition-colors disabled:opacity-30"
              disabled
            >
              <SkipBack className="w-4 h-4 text-billionaire-platinum/60" />
            </button>
            <button
              className="p-2 rounded-full hover:bg-billionaire-gold-500/10 transition-colors disabled:opacity-30"
              disabled
            >
              <SkipForward className="w-4 h-4 text-billionaire-platinum/60" />
            </button>
          </div>
        </div>

        {/* Hidden Audio Element */}
        <audio
          ref={audioRef}
          src={track.audioUrl}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onEnded={handleEnded}
          onError={(e) => console.log("Audio error:", e)}
        />
      </div>
    </div>
  );
}