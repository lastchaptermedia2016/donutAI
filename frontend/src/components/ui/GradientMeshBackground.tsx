"use client";

import React from "react";

interface GradientMeshBackgroundProps {
  className?: string;
}

/**
 * GradientMeshBackground - Slow-shifting gradient mesh for luxurious depth
 * Creates a subtle, premium background with deep blue and gold tones
 */
export const GradientMeshBackground: React.FC<GradientMeshBackgroundProps> = ({
  className = "",
}) => {
  return (
    <div className={`gradient-mesh-bg ${className}`} aria-hidden="true" />
  );
};

export default GradientMeshBackground;