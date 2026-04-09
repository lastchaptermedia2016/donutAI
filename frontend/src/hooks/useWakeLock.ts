/**
 * useWakeLock Hook
 * 
 * Provides Wake Lock API functionality to prevent the device from sleeping
 * when the app is active. This ensures Donut AI continues running even when
 * the phone screen is on but not actively touched.
 */

import { useState, useEffect, useCallback, useRef } from 'react';

interface UseWakeLockOptions {
  /** Whether wake lock should be enabled */
  enabled?: boolean;
  /** Callback when wake lock is acquired */
  onAcquire?: () => void;
  /** Callback when wake lock is released */
  onRelease?: () => void;
  /** Callback when wake lock fails */
  onError?: (error: Error) => void;
}

interface UseWakeLockReturn {
  /** Whether wake lock is currently active */
  isActive: boolean;
  /** Whether wake lock is supported in this browser */
  isSupported: boolean;
  /** Manually acquire wake lock */
  acquire: () => Promise<void>;
  /** Manually release wake lock */
  release: () => void;
  /** Current error state */
  error: Error | null;
}

export function useWakeLock(options: UseWakeLockOptions = {}): UseWakeLockReturn {
  const {
    enabled = true,
    onAcquire,
    onRelease,
    onError,
  } = options;

  const [isActive, setIsActive] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const wakeLockRef = useRef<WakeLockSentinel | null>(null);
  const isAcquiringRef = useRef(false);

  // Check if Wake Lock API is supported
  useEffect(() => {
    const supported = 'wakeLock' in navigator;
    setIsSupported(supported);
    
    if (!supported && enabled) {
      console.log('Wake Lock API not supported in this browser');
    }
  }, [enabled]);

  // Acquire wake lock
  const acquire = useCallback(async () => {
    if (!enabled || !isSupported || isAcquiringRef.current || wakeLockRef.current) {
      return;
    }

    isAcquiringRef.current = true;

    try {
      // Request screen wake lock
      const wakeLock = await navigator.wakeLock.request('screen');
      wakeLockRef.current = wakeLock;
      setIsActive(true);
      setError(null);

      // Handle wake lock release events
      wakeLock.addEventListener('release', () => {
        console.log('Wake Lock released');
        setIsActive(false);
        wakeLockRef.current = null;
        onRelease?.();
      });

      // Handle visibility change to reacquire wake lock
      const handleVisibilityChange = async () => {
        if (document.visibilityState === 'visible' && !wakeLockRef.current) {
          console.log('Reacquiring Wake Lock after visibility change');
          try {
            const newWakeLock = await navigator.wakeLock.request('screen');
            wakeLockRef.current = newWakeLock;
            setIsActive(true);
            onAcquire?.();
          } catch (err) {
            console.log('Failed to reacquire Wake Lock:', err);
          }
        }
      };

      document.addEventListener('visibilitychange', handleVisibilityChange);
      
      // Store cleanup function
      wakeLockRef.current.addEventListener('release', () => {
        document.removeEventListener('visibilitychange', handleVisibilityChange);
      });

      console.log('Wake Lock acquired successfully');
      onAcquire?.();
    } catch (err) {
      const error = err as Error;
      console.error('Failed to acquire Wake Lock:', error);
      setError(error);
      setIsActive(false);
      onError?.(error);
    } finally {
      isAcquiringRef.current = false;
    }
  }, [enabled, isSupported, onAcquire, onRelease, onError]);

  // Release wake lock
  const release = useCallback(() => {
    if (wakeLockRef.current) {
      wakeLockRef.current.release();
      wakeLockRef.current = null;
      setIsActive(false);
      console.log('Wake Lock released manually');
    }
  }, []);

  // Auto-acquire on mount if enabled
  useEffect(() => {
    if (enabled && isSupported) {
      acquire();
    }

    return () => {
      release();
    };
  }, [enabled, isSupported, acquire, release]);

  // Handle page visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && enabled && isSupported && !wakeLockRef.current) {
        // Small delay to ensure the page is fully visible
        setTimeout(() => {
          acquire();
        }, 100);
      } else if (document.visibilityState === 'hidden' && wakeLockRef.current) {
        // Keep wake lock when page is hidden (app is still running)
        console.log('Page hidden, keeping Wake Lock active');
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [enabled, isSupported, acquire]);

  // Handle beforeunload to release wake lock
  useEffect(() => {
    const handleBeforeUnload = () => {
      release();
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [release]);

  return {
    isActive,
    isSupported,
    acquire,
    release,
    error,
  };
}

export default useWakeLock;