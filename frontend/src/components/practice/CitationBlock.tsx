"use client";

import type { Citation } from "@/lib/types";

interface Props {
  citation: Citation;
}

export function CitationBlock({ citation }: Props) {
  return (
    <div className="bg-warm-50 border border-warm-100 rounded-lg p-4">
      <div className="flex items-start gap-3">
        <span className="text-xs font-mono bg-sage-100 text-sage-700 px-1.5 py-0.5 rounded shrink-0">
          {citation.id}
        </span>
        <div className="flex-1">
          <p className="text-sm font-medium text-sage-800">
            {citation.book}
            {citation.chapter && `, Ch. ${citation.chapter}`}
            {citation.verse && `, v. ${citation.verse}`}
          </p>
          <blockquote className="text-sm italic text-warm-700 mt-1 pl-3 border-l-2 border-warm-200">
            {citation.quote}
          </blockquote>
          <p className="text-xs text-warm-500 mt-2">{citation.relevance}</p>
        </div>
      </div>
    </div>
  );
}
