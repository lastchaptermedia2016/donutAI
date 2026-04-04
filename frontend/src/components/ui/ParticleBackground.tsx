"use client";

import React, { useEffect, useState, useMemo } from "react";

interface ParticleBackgroundProps {
  particleCount?: number;
  className?: string;
}

/**
 * ParticleBackground - Subtle floating particles for a luxurious atmosphere
 * Creates depth and movement without being distracting
 */
export const ParticleBackground: React.FC<ParticleBackgroundProps> = ({
  particleCount = 30,
  className = "",
}) => {
  const [particles, setParticles] = useState<
    Array<{ id: number; left: number; delay: number; duration: number; size: number }>
  >([]);

  useEffect(() => {
    const newParticles = Array.from({ length: particleCount }, (_, i) => ({
      id: i,
      left: Math.random() * 100,
      delay: Math.random() * 20,
      duration: 15 + Math.random() * 20,
      size: 1 + Math.random() * 2,
    }));
    setParticles(newParticles);
  }, [particleCount]);

  return (
    <div className={`particle-container ${className}`} aria-hidden="true">
      {particles.map((particle) => (
        <div
          key={particle.id}
          className="particle"
          style={{
            left: `${particle.left}%`,
            bottom: "-10px",
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            animationDelay: `${particle.delay}s`,
            animationDuration: `${particle.duration}s`,
          }}
        />
      ))}
    </div>
  );
};

export default ParticleBackground;