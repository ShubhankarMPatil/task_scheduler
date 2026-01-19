"use client";

import { useEffect, useState } from "react";
import { getTasks } from "@/lib/api";
import { Task } from "@/types/task";

export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTasks().then((data) => {
      setTasks(data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="bg-white rounded-xl shadow p-5">
      <h2 className="font-medium mb-3">Tasks</h2>

      {loading && <p>Loading…</p>}

      {!loading && tasks.length === 0 && (
        <p className="text-gray-500 text-sm">No tasks yet.</p>
      )}

      <ul className="space-y-2">
        {tasks.map((task) => (
          <li
            key={task.id}
            className="flex justify-between items-center border rounded-lg px-3 py-2"
          >
            <span>{task.title}</span>
            <span className="text-xs bg-gray-200 px-2 py-1 rounded">
              {task.completed ? "Done" : "Pending"}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
