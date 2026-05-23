"use client";

export function Header() {
  return (
    <header className="border-b border-warm-100 bg-white/80 backdrop-blur-sm px-6 py-4">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        <h1 className="text-xl font-serif text-sage-800">Sadhana Architect</h1>
        <span className="text-xs text-warm-400 bg-warm-100 px-2 py-1 rounded">
          Local AI
        </span>
      </div>
    </header>
  );
}
