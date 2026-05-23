"use client";

import { useState } from "react";
import { CitationBlock } from "./CitationBlock";
import type { GeneratedPractice } from "@/lib/types";

interface Props {
  practice: GeneratedPractice;
  practiceId: string | null;
}

export function PracticeCard({ practice, practiceId }: Props) {
  const [showCitations, setShowCitations] = useState(false);

  return (
    <div className="card space-y-8">
      {/* Header */}
      <div className="text-center border-b border-warm-100 pb-6">
        <h3 className="text-2xl font-serif text-sage-800">{practice.title}</h3>
        <p className="text-warm-600 mt-2 italic font-serif">
          {practice.intention}
        </p>
        <p className="text-sm text-warm-500 mt-2">
          {practice.duration_minutes} minutes
        </p>
      </div>

      {/* Pranayama Section */}
      {practice.pranayama.length > 0 && (
        <section>
          <h4 className="text-lg font-medium text-sage-700 mb-4 flex items-center gap-2">
            <span className="text-sage-400">I.</span> Pranayama
          </h4>
          <div className="space-y-4">
            {practice.pranayama.map((step, i) => (
              <div key={i} className="bg-sage-50 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h5 className="font-medium text-sage-800">{step.name}</h5>
                    {step.sanskrit_name && (
                      <span className="text-sm italic text-sage-600">
                        {step.sanskrit_name}
                      </span>
                    )}
                  </div>
                  <span className="text-xs bg-sage-100 text-sage-600 px-2 py-1 rounded">
                    {step.duration_minutes} min
                  </span>
                </div>
                <p className="text-sm text-gray-700 whitespace-pre-line">
                  {step.instructions}
                </p>
                {step.contraindications && (
                  <p className="text-xs text-amber-700 bg-amber-50 rounded px-2 py-1 mt-2">
                    Note: {step.contraindications}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Asana Section */}
      {practice.asana.length > 0 && (
        <section>
          <h4 className="text-lg font-medium text-sage-700 mb-4 flex items-center gap-2">
            <span className="text-sage-400">II.</span> Asana
          </h4>
          <div className="space-y-4">
            {practice.asana.map((step, i) => (
              <div key={i} className="bg-warm-50 rounded-lg p-4 border border-warm-100">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h5 className="font-medium text-warm-800">{step.name}</h5>
                    {step.sanskrit_name && (
                      <span className="text-sm italic text-warm-600">
                        {step.sanskrit_name}
                      </span>
                    )}
                  </div>
                  <span className="text-xs bg-warm-100 text-warm-600 px-2 py-1 rounded">
                    {step.duration_minutes} min
                  </span>
                </div>
                <p className="text-sm text-gray-700 whitespace-pre-line">
                  {step.instructions}
                </p>
                {step.contraindications && (
                  <p className="text-xs text-amber-700 bg-amber-50 rounded px-2 py-1 mt-2">
                    Note: {step.contraindications}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Meditation Section */}
      {practice.meditation && (
        <section>
          <h4 className="text-lg font-medium text-sage-700 mb-4 flex items-center gap-2">
            <span className="text-sage-400">III.</span> Meditation
          </h4>
          <div className="bg-gradient-to-br from-sage-50 to-warm-50 rounded-lg p-6 border border-sage-100">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h5 className="font-medium text-sage-800">
                  {practice.meditation.name}
                </h5>
                <span className="text-sm text-sage-600">
                  {practice.meditation.technique}
                </span>
              </div>
              <span className="text-xs bg-sage-100 text-sage-600 px-2 py-1 rounded">
                {practice.meditation.duration_minutes} min
              </span>
            </div>
            <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
              {practice.meditation.instructions}
            </p>
          </div>
        </section>
      )}

      {/* Closing Reflection */}
      {practice.closing_reflection && (
        <div className="text-center py-4 border-t border-warm-100">
          <p className="font-serif italic text-warm-700">
            {practice.closing_reflection}
          </p>
        </div>
      )}

      {/* Citations Toggle */}
      {practice.citations.length > 0 && (
        <div className="border-t border-warm-100 pt-4">
          <button
            className="text-sm text-sage-600 hover:text-sage-800 font-medium"
            onClick={() => setShowCitations(!showCitations)}
          >
            {showCitations ? "Hide" : "Show"} Sources ({practice.citations.length})
          </button>
          {showCitations && (
            <div className="mt-4 space-y-3">
              {practice.citations.map((citation) => (
                <CitationBlock key={citation.id} citation={citation} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
