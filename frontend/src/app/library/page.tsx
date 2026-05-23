"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getLibrary, uploadText, processText } from "@/lib/api";

export default function LibraryPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["library"],
    queryFn: getLibrary,
  });

  const [showUpload, setShowUpload] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [tradition, setTradition] = useState("");

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error("No file selected");
      const result = await uploadText(file, title, author || undefined, tradition || undefined);
      await processText(result.id);
      return result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["library"] });
      setShowUpload(false);
      setFile(null);
      setTitle("");
      setAuthor("");
      setTradition("");
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-serif text-sage-800 mb-2">
            Text Library
          </h2>
          <p className="text-warm-600">
            Your indexed spiritual texts that power practice generation.
          </p>
        </div>
        <button
          className="btn-primary"
          onClick={() => setShowUpload(!showUpload)}
        >
          Upload Text
        </button>
      </div>

      {/* Stats */}
      {data?.stats && (
        <div className="grid grid-cols-2 gap-4">
          <div className="card text-center">
            <p className="text-2xl font-serif text-sage-700">
              {data.stats.chunks_count}
            </p>
            <p className="text-sm text-warm-600">Total Chunks</p>
          </div>
          <div className="card text-center">
            <p className="text-2xl font-serif text-sage-700">
              {data.stats.techniques_count}
            </p>
            <p className="text-sm text-warm-600">Practice Techniques</p>
          </div>
        </div>
      )}

      {/* Upload Form */}
      {showUpload && (
        <div className="card space-y-4">
          <h3 className="font-medium text-sage-800">Upload New Text</h3>
          <div>
            <input
              type="file"
              accept=".pdf,.epub"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="input-field"
            />
          </div>
          <input
            type="text"
            placeholder="Title (e.g., Hatha Yoga Pradipika)"
            className="input-field"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <div className="grid grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Author (optional)"
              className="input-field"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
            />
            <select
              className="input-field"
              value={tradition}
              onChange={(e) => setTradition(e.target.value)}
            >
              <option value="">Tradition (optional)</option>
              <option value="hatha">Hatha</option>
              <option value="raja">Raja</option>
              <option value="tantra">Tantra</option>
              <option value="vedanta">Vedanta</option>
              <option value="bhakti">Bhakti</option>
            </select>
          </div>
          <button
            className="btn-primary"
            disabled={!file || !title || uploadMutation.isPending}
            onClick={() => uploadMutation.mutate()}
          >
            {uploadMutation.isPending ? "Processing..." : "Upload & Process"}
          </button>
          {uploadMutation.error && (
            <p className="text-sm text-red-600">
              {uploadMutation.error.message}
            </p>
          )}
        </div>
      )}

      {/* Library List */}
      {isLoading && (
        <div className="card text-center py-8 text-warm-500">Loading...</div>
      )}

      {data && data.texts.length === 0 && !showUpload && (
        <div className="card text-center py-12">
          <p className="text-warm-600 mb-2">No texts indexed yet.</p>
          <p className="text-sm text-warm-500">
            Upload your spiritual texts (PDF or EPUB) to get started.
          </p>
        </div>
      )}

      {data && data.texts.length > 0 && (
        <div className="grid gap-3">
          {data.texts.map((text) => (
            <div key={text.id} className="card flex justify-between items-center">
              <div>
                <h3 className="font-medium text-sage-800">{text.title}</h3>
                <p className="text-sm text-warm-600">
                  {text.author || "Unknown author"}
                  {text.tradition && (
                    <span className="ml-2 text-xs bg-sage-100 text-sage-600 px-2 py-0.5 rounded">
                      {text.tradition}
                    </span>
                  )}
                </p>
              </div>
              <div className="text-right">
                <span
                  className={`text-xs px-2 py-1 rounded ${
                    text.status === "ready"
                      ? "bg-green-100 text-green-700"
                      : text.status === "processing"
                      ? "bg-amber-100 text-amber-700"
                      : text.status === "error"
                      ? "bg-red-100 text-red-700"
                      : "bg-warm-100 text-warm-600"
                  }`}
                >
                  {text.status}
                </span>
                {text.total_chunks > 0 && (
                  <p className="text-xs text-warm-500 mt-1">
                    {text.total_chunks} chunks
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
