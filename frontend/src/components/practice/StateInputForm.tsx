"use client";

import { useState } from "react";
import { clsx } from "clsx";
import type { PracticeRequest } from "@/lib/types";

interface Props {
  onSubmit: (request: PracticeRequest) => void;
  isLoading: boolean;
}

const TRADITIONS = [
  { value: "", label: "Any" },
  { value: "hatha", label: "Hatha" },
  { value: "raja", label: "Raja" },
  { value: "tantra", label: "Tantra" },
  { value: "vedanta", label: "Vedanta" },
  { value: "bhakti", label: "Bhakti" },
];

const FOCUS_AREAS = ["pranayama", "asana", "meditation", "mantra"];

const QUICK_STATES = {
  physical: ["stiff", "low energy", "restless", "pain-free", "fatigued", "energetic"],
  mental: ["scattered", "dull", "anxious", "calm", "overwhelmed", "focused"],
  emotional: ["anxious", "sad", "irritable", "peaceful", "seeking grounding", "joyful"],
};

export function StateInputForm({ onSubmit, isLoading }: Props) {
  const [physicalState, setPhysicalState] = useState("");
  const [mentalState, setMentalState] = useState("");
  const [emotionalState, setEmotionalState] = useState("");
  const [timeMinutes, setTimeMinutes] = useState(30);
  const [experienceLevel, setExperienceLevel] = useState<"beginner" | "intermediate" | "advanced">("intermediate");
  const [tradition, setTradition] = useState("");
  const [focusAreas, setFocusAreas] = useState<string[]>(["pranayama", "asana", "meditation"]);
  const [exclude, setExclude] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({
      physical_state: physicalState,
      mental_state: mentalState,
      emotional_state: emotionalState,
      time_available_minutes: timeMinutes,
      experience_level: experienceLevel,
      tradition_preference: tradition || null,
      focus_areas: focusAreas,
      exclude: exclude ? exclude.split(",").map((s) => s.trim()) : [],
    });
  }

  function toggleFocus(area: string) {
    setFocusAreas((prev) =>
      prev.includes(area) ? prev.filter((a) => a !== area) : [...prev, area]
    );
  }

  function addQuickState(setter: (s: string) => void, current: string, word: string) {
    setter(current ? `${current}, ${word}` : word);
  }

  return (
    <form onSubmit={handleSubmit} className="card space-y-6">
      {/* Physical State */}
      <div>
        <label className="block text-sm font-medium text-sage-700 mb-2">
          Physical State
        </label>
        <textarea
          className="input-field resize-none"
          rows={2}
          placeholder="How does your body feel right now?"
          value={physicalState}
          onChange={(e) => setPhysicalState(e.target.value)}
          required
        />
        <div className="flex flex-wrap gap-1.5 mt-2">
          {QUICK_STATES.physical.map((word) => (
            <button
              key={word}
              type="button"
              className="chip chip-inactive text-xs"
              onClick={() => addQuickState(setPhysicalState, physicalState, word)}
            >
              {word}
            </button>
          ))}
        </div>
      </div>

      {/* Mental State */}
      <div>
        <label className="block text-sm font-medium text-sage-700 mb-2">
          Mental State
        </label>
        <textarea
          className="input-field resize-none"
          rows={2}
          placeholder="What is the quality of your mind?"
          value={mentalState}
          onChange={(e) => setMentalState(e.target.value)}
          required
        />
        <div className="flex flex-wrap gap-1.5 mt-2">
          {QUICK_STATES.mental.map((word) => (
            <button
              key={word}
              type="button"
              className="chip chip-inactive text-xs"
              onClick={() => addQuickState(setMentalState, mentalState, word)}
            >
              {word}
            </button>
          ))}
        </div>
      </div>

      {/* Emotional State */}
      <div>
        <label className="block text-sm font-medium text-sage-700 mb-2">
          Emotional State
        </label>
        <textarea
          className="input-field resize-none"
          rows={2}
          placeholder="What emotions are present?"
          value={emotionalState}
          onChange={(e) => setEmotionalState(e.target.value)}
          required
        />
        <div className="flex flex-wrap gap-1.5 mt-2">
          {QUICK_STATES.emotional.map((word) => (
            <button
              key={word}
              type="button"
              className="chip chip-inactive text-xs"
              onClick={() => addQuickState(setEmotionalState, emotionalState, word)}
            >
              {word}
            </button>
          ))}
        </div>
      </div>

      {/* Time + Experience + Tradition */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-sage-700 mb-2">
            Time Available: {timeMinutes} min
          </label>
          <input
            type="range"
            min={10}
            max={90}
            step={5}
            value={timeMinutes}
            onChange={(e) => setTimeMinutes(Number(e.target.value))}
            className="w-full accent-sage-600"
          />
          <div className="flex justify-between text-xs text-warm-500 mt-1">
            <span>10 min</span>
            <span>90 min</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-sage-700 mb-2">
            Experience Level
          </label>
          <select
            className="input-field"
            value={experienceLevel}
            onChange={(e) => setExperienceLevel(e.target.value as any)}
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-sage-700 mb-2">
            Tradition
          </label>
          <select
            className="input-field"
            value={tradition}
            onChange={(e) => setTradition(e.target.value)}
          >
            {TRADITIONS.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Focus Areas */}
      <div>
        <label className="block text-sm font-medium text-sage-700 mb-2">
          Focus Areas
        </label>
        <div className="flex flex-wrap gap-2">
          {FOCUS_AREAS.map((area) => (
            <button
              key={area}
              type="button"
              className={clsx(
                "chip",
                focusAreas.includes(area) ? "chip-active" : "chip-inactive"
              )}
              onClick={() => toggleFocus(area)}
            >
              {area}
            </button>
          ))}
        </div>
      </div>

      {/* Exclude */}
      <div>
        <label className="block text-sm font-medium text-sage-700 mb-2">
          Exclude (optional)
        </label>
        <input
          type="text"
          className="input-field"
          placeholder="e.g., inversions, intense breathwork"
          value={exclude}
          onChange={(e) => setExclude(e.target.value)}
        />
      </div>

      <button type="submit" disabled={isLoading} className="btn-primary w-full">
        {isLoading ? "Generating..." : "Generate Practice"}
      </button>
    </form>
  );
}
