"use client";

import { useEffect, useState } from "react";
import { fetchDashboard, LinkResponse } from "@/lib/api";
import LoadingState from "@/components/LoadingState";
import LinkCard from "@/components/LinkCard";

export default function TopReads() {
  const [reads, setReads] = useState<LinkResponse[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboard()
      .then((data) => setReads(data.top_reads))
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="p-4 text-warning">
        Unable to load top reads: {error}
      </div>
    );
  }

  if (!reads) {
    return <LoadingState count={5} />;
  }

  return (
    <section className="mt-8">
      <h2 className="text-2xl font-bold text-primary mb-4">
        Today’s Must‑Read Picks
      </h2>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {reads.map((item) => (
          <LinkCard
            key={item.id}
            title={item.title ?? item.url}
            url={item.url}
            summary={item.summary}
            tags={item.smart_tags}
          />
        ))}
      </div>
    </section>
  );
}