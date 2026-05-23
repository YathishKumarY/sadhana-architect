export interface PracticeRequest {
  physical_state: string;
  mental_state: string;
  emotional_state: string;
  time_available_minutes: number;
  experience_level: "beginner" | "intermediate" | "advanced";
  tradition_preference: string | null;
  focus_areas: string[];
  exclude: string[];
}

export interface Citation {
  id: string;
  book: string;
  chapter: string | number | null;
  verse: string | number | null;
  quote: string;
  relevance: string;
}

export interface PranayamaStep {
  name: string;
  sanskrit_name: string | null;
  duration_minutes: number;
  instructions: string;
  contraindications: string | null;
  source_citation_id: string | null;
}

export interface AsanaStep {
  name: string;
  sanskrit_name: string | null;
  duration_minutes: number;
  instructions: string;
  contraindications: string | null;
  source_citation_id: string | null;
}

export interface MeditationStep {
  name: string;
  technique: string;
  duration_minutes: number;
  instructions: string;
  source_citation_id: string | null;
}

export interface GeneratedPractice {
  title: string;
  duration_minutes: number;
  intention: string;
  pranayama: PranayamaStep[];
  asana: AsanaStep[];
  meditation: MeditationStep | null;
  closing_reflection: string | null;
  citations: Citation[];
}

export interface PracticeResponse {
  id: string;
  created_at: string;
  practice: GeneratedPractice;
}

export interface PracticeHistoryItem {
  id: string;
  created_at: string;
  title: string;
  duration_minutes: number;
  tradition: string | null;
  experience_level: string;
  rating: number | null;
  physical_state: string;
  mental_state: string;
  emotional_state: string;
}

export interface LibraryText {
  id: string;
  title: string;
  author: string | null;
  tradition: string | null;
  status: string;
  total_chunks: number;
  ingested_at: string | null;
}
