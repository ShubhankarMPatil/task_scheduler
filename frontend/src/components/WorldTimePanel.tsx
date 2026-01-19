"use client";

import { useEffect, useState } from "react";

import { getWorldTime } from "@/lib/api";

type WorldTime = {
  timezone?: string;
  datetime?: string;
  utc_offset?: string;
};

export default function WorldTimePanel() {
  const [time, setTime] = useState<WorldTime | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = () => {
    getWorldTime()
      .then(data => {
        setError(null);
        setTime(data);
      })
      .catch(() => setError("Failed to load world time"));
  };

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="bg-white rounded-xl shadow p-5">
      <div className="flex items-center justify-between gap-4">
        <h2 className="font-medium">World Time</h2>
        <button className="text-sm underline" onClick={refresh}>
          Refresh
        </button>
      </div>

      {error ? <p className="text-sm text-red-600 mt-2">{error}</p> : null}

      {!time ? (
        <p className="mt-2">Loading…</p>
      ) : (
        <div className="mt-2">
          <p className="text-sm text-gray-600">{time.timezone ?? "—"}</p>
          <p className="text-xl font-semibold">
            {time.datetime ? new Date(time.datetime).toLocaleTimeString() : "—"}
          </p>
        </div>
      )}
    </div>
  );
}
