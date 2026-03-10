"use client";

export default function TagBadge({ tag }: { tag: string }) {
  return (
    <span className="inline-block bg-accent text-white text-xs px-2 py-0.5 rounded-md mr-1">
      {tag}
    </span>
  );
}