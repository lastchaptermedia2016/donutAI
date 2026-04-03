"use client";

interface LoadingProps {
  message?: string;
  size?: "sm" | "md" | "lg";
}

export function Loading({ message = "Loading...", size = "md" }: LoadingProps) {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
  };

  return (
    <div className="flex flex-col items-center justify-center gap-3 p-4">
      <div className="flex gap-1">
        {[0, 150, 300].map((delay) => (
          <div
            key={delay}
            className={`${sizeClasses[size]} bg-sophisticated-burgundy rounded-full animate-bounce`}
            style={{ animationDelay: `${delay}ms` }}
          />
        ))}
      </div>
      <p className="text-sophisticated-taupe text-sm">{message}</p>
    </div>
  );
}

export function LoadingPage({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-sophisticated-midnight">
      <Loading message={message} size="lg" />
    </div>
  );
}