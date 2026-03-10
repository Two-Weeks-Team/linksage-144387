"use client";

import { useState } from "react";
import { createLink } from "@/lib/api";
import LoadingState from "@/components/LoadingState";
import DashboardShell from "@/components/DashboardShell";

export default function Hero() {
  const [linksInput, setLinksInput] = useState("");
  const [processing, setProcessing] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleOrganize = async () => {
    const urls = linksInput
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean);
    if (urls.length === 0) return;
    setProcessing(true);
    setError(null);
    try {
      await Promise.all(urls.map((url) => createLink({ url })));
      setShowDashboard(true);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setProcessing(false);
    }
  };

  if (showDashboard) {
    return <DashboardShell />;
  }

  return (
    <section className="flex flex-col items-center justify-center min-h-screen px-4 text-center">
      <h1 className="text-4xl md:text-5xl font-bold text-primary mb-4">
        Your Web, Reimagined
      </h1>
      <p className="text-lg md:text-xl text-foreground mb-8 max-w-2xl">
        Paste a chaotic collection of links, let AI generate summaries and smart tags,
        then instantly discover your top reads.
      </p>

      <textarea
        value={linksInput}
        onChange={(e) => setLinksInput(e.target.value)}
        placeholder="Enter one URL per line..."
        className="w-full max-w-xl h-32 p-3 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-none mb-4"
      />

      {error && <p className="text-warning mb-2">{error}</p>}

      <button
        onClick={handleOrganize}
        disabled={processing}
        className="bg-accent text-white font-medium py-2 px-6 rounded-md hover:bg-orange-600 transition-colors disabled:opacity-50"
      >
        {processing ? "Organizing…" : "Organize"}
      </button>

      {processing && <LoadingState count={3} className="mt-6" />}
    </section>
  );
}