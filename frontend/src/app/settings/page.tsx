"use client";

import { useState } from "react";

export default function SettingsPage() {
  const [name, setName] = useState("");
  const [tradition, setTradition] = useState("");
  const [level, setLevel] = useState("intermediate");
  const [duration, setDuration] = useState(30);
  const [saved, setSaved] = useState(false);

  async function handleSave() {
    try {
      const response = await fetch("/api/v1/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          default_tradition: tradition || null,
          default_experience_level: level,
          default_duration_minutes: duration,
          excluded_practices: [],
        }),
      });
      if (response.ok) {
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      }
    } catch (err) {
      console.error("Failed to save settings:", err);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-serif text-sage-800 mb-2">Settings</h2>
        <p className="text-warm-600">
          Configure your default preferences for practice generation.
        </p>
      </div>

      <div className="card space-y-6">
        <div>
          <label className="block text-sm font-medium text-sage-700 mb-2">
            Your Name
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="Practitioner"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-sage-700 mb-2">
              Default Tradition
            </label>
            <select
              className="input-field"
              value={tradition}
              onChange={(e) => setTradition(e.target.value)}
            >
              <option value="">Any</option>
              <option value="hatha">Hatha</option>
              <option value="raja">Raja</option>
              <option value="tantra">Tantra</option>
              <option value="vedanta">Vedanta</option>
              <option value="bhakti">Bhakti</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-sage-700 mb-2">
              Experience Level
            </label>
            <select
              className="input-field"
              value={level}
              onChange={(e) => setLevel(e.target.value)}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-sage-700 mb-2">
              Default Duration: {duration} min
            </label>
            <input
              type="range"
              min={10}
              max={90}
              step={5}
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className="w-full accent-sage-600 mt-2"
            />
          </div>
        </div>

        <button className="btn-primary" onClick={handleSave}>
          Save Preferences
        </button>

        {saved && (
          <p className="text-sm text-green-600">Preferences saved successfully.</p>
        )}
      </div>

      <div className="card">
        <h3 className="font-medium text-sage-800 mb-3">System Status</h3>
        <p className="text-sm text-warm-600">
          Check the health endpoint to verify Ollama is running and models are
          available.
        </p>
        <button
          className="btn-secondary mt-3"
          onClick={async () => {
            const resp = await fetch("/api/v1/health");
            const data = await resp.json();
            alert(JSON.stringify(data, null, 2));
          }}
        >
          Check Health
        </button>
      </div>
    </div>
  );
}
