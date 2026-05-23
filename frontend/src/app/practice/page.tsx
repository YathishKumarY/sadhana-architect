"use client";

import { useState } from "react";
import { StateInputForm } from "@/components/practice/StateInputForm";
import { PracticeCard } from "@/components/practice/PracticeCard";
import { generatePractice } from "@/lib/api";
import type { PracticeRequest, GeneratedPractice } from "@/lib/types";

export default function PracticePage() {
  const [practice, setPractice] = useState<GeneratedPractice | null>(null);
  const [practiceId, setPracticeId] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate(request: PracticeRequest) {
    setIsGenerating(true);
    setError(null);
    setPractice(null);

    try {
      const response = await generatePractice(request);
      setPractice(response.practice);
      setPracticeId(response.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate practice");
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-serif text-sage-800 mb-2">
          Generate Your Practice
        </h2>
        <p className="text-warm-600">
          Describe your current state and receive a personalized sadhana grounded
          in classical texts.
        </p>
      </div>

      <StateInputForm onSubmit={handleGenerate} isLoading={isGenerating} />

      {error && (
        <div className="card border-red-200 bg-red-50 text-red-700">
          <p className="font-medium">Generation failed</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {isGenerating && (
        <div className="card text-center py-12">
          <div className="animate-pulse">
            <p className="text-sage-600 font-serif text-lg">
              Consulting the texts...
            </p>
            <p className="text-warm-500 text-sm mt-2">
              Retrieving relevant passages and generating your practice
            </p>
          </div>
        </div>
      )}

      {practice && <PracticeCard practice={practice} practiceId={practiceId} />}
    </div>
  );
}
