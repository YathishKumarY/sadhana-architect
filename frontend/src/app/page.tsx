import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <h1 className="text-4xl font-serif text-sage-800 mb-4">
        Sadhana Architect
      </h1>
      <p className="text-lg text-warm-700 max-w-lg mb-8">
        Personalized yoga practices grounded in classical texts. Describe your
        current state, and receive a tailored sadhana with authentic citations.
      </p>
      <Link href="/practice" className="btn-primary text-lg">
        Begin Your Practice
      </Link>
      <div className="mt-12 grid grid-cols-3 gap-8 text-center max-w-2xl">
        <div>
          <div className="text-2xl font-serif text-sage-600 mb-1">Grounded</div>
          <p className="text-sm text-warm-600">
            Every recommendation traces back to classical source texts
          </p>
        </div>
        <div>
          <div className="text-2xl font-serif text-sage-600 mb-1">Personal</div>
          <p className="text-sm text-warm-600">
            Tailored to your body, mind, and available time
          </p>
        </div>
        <div>
          <div className="text-2xl font-serif text-sage-600 mb-1">Private</div>
          <p className="text-sm text-warm-600">
            Runs entirely on your machine - your data stays yours
          </p>
        </div>
      </div>
    </div>
  );
}
