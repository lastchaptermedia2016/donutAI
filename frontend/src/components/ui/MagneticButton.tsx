"use client";

import React, { useRef, useState, useCallback, ReactNode } from "react";

interface MagneticButtonProps {
  children: ReactNode;
  className?: string;
  intensity?: number;
  range?: number;
  onClick?: () => void;
  disabled?: boolean;
}

/**
 * MagneticButton - A luxury button that subtly follows the cursor
 * Creates a premium, tactile feel with smooth magnetic attraction
 */
export const MagneticButton: React.FC<MagneticButtonProps> = ({
  children,
  className = "",
  intensity = 0.3,
  range = 100,
  onClick,
  disabled = false,
}) => {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLButtonElement>) => {
      if (!buttonRef.current || disabled) return;

      const rect = buttonRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      const deltaX = (e.clientX - centerX) / range;
      const deltaY = (e.clientY - centerY) / range;

      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

      if (distance < 1) {
        const magneticX = -deltaX * intensity * 20 * (1 - distance);
        const magneticY = -deltaY * intensity * 20 * (1 - distance);
        setPosition({ x: magneticX, y: magneticY });
      }
    },
    [intensity, range, disabled]
  );

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false);
    setPosition({ x: 0, y: 0 });
  }, []);

  return (
    <button
      ref={buttonRef}
      className={`magnetic-btn ${className}`}
      style={{
        transform: isHovered
          ? `translate(${position.x}px, ${position.y}px) scale(1.05)`
          : "translate(0, 0) scale(1)",
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

export default MagneticButton;