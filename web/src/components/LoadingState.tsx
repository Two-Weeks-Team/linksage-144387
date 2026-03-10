"use client";

interface LoadingStateProps {
  count?: number;
  className?: string;
}

export default function LoadingState({ count = 4, className = "" }: LoadingStateProps) {
  return (
    <div className={`grid gap-4 md:grid-cols-2 lg:grid-cols-3 ${className}`)}>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="h-48 bg-muted rounded-md animate-pulse"
        ></div>
      ))}
    </div>
  );
}