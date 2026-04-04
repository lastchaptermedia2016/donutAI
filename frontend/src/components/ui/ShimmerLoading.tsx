"use client";

import React from "react";

interface ShimmerLoadingProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: string;
  className?: string;
}

/**
 * ShimmerLoading - Elegant loading placeholder with shimmer effect
 * Provides visual feedback during loading states with a premium feel
 */
export const ShimmerLoading: React.FC<ShimmerLoadingProps> = ({
  width = "100%",
  height = "20px",
  borderRadius = "8px",
  className = "",
}) => {
  return (
    <div
      className={`shimmer-loading rounded-lg ${className}`}
      style={{
        width: typeof width === "number" ? `${width}px` : width,
        height: typeof height === "number" ? `${height}px` : height,
        borderRadius,
      }}
      aria-label="Loading..."
    />
  );
};

interface ShimmerCardProps {
  className?: string;
  children?: React.ReactNode;
}

/**
 * ShimmerCard - A card skeleton with shimmer effect for content loading
 */
export const ShimmerCard: React.FC<ShimmerCardProps> = ({
  className = "",
  children,
}) => {
  return (
    <div className={`luxury-glass-card p-4 ${className}`}>
      {children || (
        <div className="space-y-3">
          <ShimmerLoading width="60%" height="16px" />
          <ShimmerLoading width="100%" height="12px" />
          <ShimmerLoading width="80%" height="12px" />
        </div>
      )}
    </div>
  );
};

export default ShimmerLoading;