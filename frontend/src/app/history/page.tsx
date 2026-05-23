"use client";

import { useQuery } from "@tanstack/react-query";
import { getHistory } from "@/lib/api";
import Link from "next/link";

export default function HistoryPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["history"],
    queryFn: () => getHistory(),
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-serif text-sage-800 mb-2">
          Practice History
        </h2>
        <p className="text-warm-600">
          Review your past practices and track your journey.
        </p>
      </div>

      {isLoading && (
        <div className="card text-center py-8 text-warm-500">Loading...</div>
      )}

      {error && (
        <div className="card border-red-200 bg-red-50 text-red-700">
          Failed to load history
        </div>
      )}

      {data && data.practices.length === 0 && (
        <div className="card text-center py-12">
          <p className="text-warm-600 mb-4">No practices yet.</p>
          <Link href="/practice" className="btn-primary">
            Generate Your First Practice
          </Link>
        </div>
      )}

      {data && data.practices.length > 0 && (
        <div className="space-y-3">
          {data.practices.map((practice) => (
            <Link
              key={practice.id}
              href={`/practice/${practice.id}`}
              className="card block hover:shadow-md transition-shadow cursor-pointer"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-medium text-sage-800">
                    {practice.title}
                  </h3>
                  <p className="text-sm text-warm-600 mt-1">
                    {practice.physical_state} - {practice.mental_state}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-sm text-warm-500">
                    {new Date(practice.created_at).toLocaleDateString()}
                  </span>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs bg-warm-100 text-warm-600 px-2 py-0.5 rounded">
                      {practice.duration_minutes} min
                    </span>
                    {practice.tradition && (
                      <span className="text-xs bg-sage-100 text-sage-600 px-2 py-0.5 rounded">
                        {practice.tradition}
                      </span>
                    )}
                    {practice.rating && (
                      <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded">
                        {"*".repeat(practice.rating)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
