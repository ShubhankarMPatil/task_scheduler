import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <Link
        href="/tasks"
        className="bg-black text-white px-6 py-3 rounded-lg text-lg"
      >
        Go to Dashboard →
      </Link>
    </main>
  );
}
