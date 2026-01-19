"use client";

import { useState } from "react";
import { createTask } from "@/lib/api";

export default function TaskForm() {
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!title.trim()) return;
    setLoading(true);
    await createTask({ title });
    setTitle("");
    setLoading(false);
    window.location.reload();
  };

  return (
    <div className="bg-white rounded-xl shadow p-5">
      <h2 className="font-medium mb-3">Add Task</h2>
      <div className="flex gap-3">
        <input
          className="flex-1 border rounded-lg px-3 py-2"
          placeholder="Task title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <button
          onClick={submit}
          className="bg-black text-white px-4 py-2 rounded-lg"
        >
          {loading ? "Saving…" : "Add"}
        </button>
      </div>
    </div>
  );
}
