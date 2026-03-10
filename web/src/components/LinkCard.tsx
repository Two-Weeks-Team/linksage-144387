"use client";

import TagBadge from "@/components/TagBadge";

export interface LinkCardProps {
  title: string;
  url: string;
  summary: string;
  tags: string[];
}

export default function LinkCard({
  title,
  url,
  summary,
  tags,
}: LinkCardProps) {
  const openLink = () => window.open(url, "_blank");
  return (
    <div className="bg-card rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
      <h3
        className="text-primary font-semibold text-lg cursor-pointer"
        onClick={openLink}
      >
        {title}
      </h3>
      <p className="text-sm mt-2 text-foreground/80">{summary}</p>
      <div className="mt-3 flex flex-wrap">
        {tags.map((t) => (
          <TagBadge key={t} tag={t} />
        ))}
      </div>
    </div>
  );
}