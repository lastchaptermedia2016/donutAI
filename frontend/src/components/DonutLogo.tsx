import React from 'react';

interface DonutLogoProps {
  size?: number;
  animated?: boolean;
  className?: string;
}

export const DonutLogo: React.FC<DonutLogoProps> = ({ 
  size = 64, 
  animated = false,
  className = "" 
}) => {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 100 100" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={`${animated ? 'animate-float' : ''} ${className}`}
    >
      <defs>
        {/* Billionaire Gold Gradient */}
        <linearGradient id="billionaireGold" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#F7E9C1" />
          <stop offset="25%" stopColor="#E5C777" />
          <stop offset="50%" stopColor="#C9A96E" />
          <stop offset="75%" stopColor="#A68743" />
          <stop offset="100%" stopColor="#826524" />
        </linearGradient>
        
        <linearGradient id="billionaireGlow" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#C9A96E" stopOpacity="0.3" />
          <stop offset="100%" stopColor="#C9A96E" stopOpacity="0" />
        </linearGradient>
        
        <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>
      
      {/* Outer glow ring */}
      <circle 
        cx="50" 
        cy="50" 
        r="45" 
        fill="url(#billionaireGlow)" 
        opacity="0.5"
      />
      
      {/* Main geometric hexagon frame */}
      <path
        d="M50 3.5 L90 26.75 L90 73.25 L50 96.5 L10 73.25 L10 26.75 Z"
        stroke="url(#billionaireGold)"
        strokeWidth="1.5"
        fill="none"
        filter="url(#softGlow)"
      />
      
      {/* Inner abstract geometric shape - hidden D + donut form */}
      <path
        d="M72 50 C72 36.7 61.3 26 48 26 L48 74 C61.3 74 72 63.3 72 50 Z"
        fill="url(#billionaireGold)"
        opacity="0.9"
      />
      
      {/* Central accent point */}
      <circle cx="50" cy="50" r="4" fill="url(#billionaireGold)" opacity="0.8" />
      
      {/* Subtle ring accents */}
      <circle 
        cx="50" 
        cy="50" 
        r="38" 
        stroke="url(#billionaireGold)" 
        strokeWidth="0.5" 
        fill="none" 
        opacity="0.4"
      />
      
      <circle 
        cx="50" 
        cy="50" 
        r="28" 
        stroke="url(#billionaireGold)" 
        strokeWidth="0.5" 
        fill="none" 
        opacity="0.25"
      />
      
      {/* Decorative corner elements */}
      <circle cx="10" cy="26.75" r="1.5" fill="url(#billionaireGold)" opacity="0.6" />
      <circle cx="90" cy="26.75" r="1.5" fill="url(#billionaireGold)" opacity="0.6" />
      <circle cx="10" cy="73.25" r="1.5" fill="url(#billionaireGold)" opacity="0.6" />
      <circle cx="90" cy="73.25" r="1.5" fill="url(#billionaireGold)" opacity="0.6" />
      <circle cx="50" cy="3.5" r="1.5" fill="url(#billionaireGold)" opacity="0.6" />
      <circle cx="50" cy="96.5" r="1.5" fill="url(#billionaireGold)" opacity="0.6" />
    </svg>
  );
};

export default DonutLogo;