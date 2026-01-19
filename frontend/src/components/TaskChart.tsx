"use client";

import { Pie, PieChart, Tooltip } from "recharts";

type Datum = { name: string; value: number };

export default function TaskChart({ completed, pending }: { completed: number; pending: number }) {
  const data: Datum[] = [
    { name: "Completed", value: completed },
    { name: "Pending", value: pending },
  ];

  return (
    <div className="bg-white rounded-xl shadow p-5">
      <h2 className="font-medium mb-3">Status</h2>
      <PieChart width={240} height={210}>
        <Pie data={data} dataKey="value" nameKey="name" outerRadius={80} />
        <Tooltip />
      </PieChart>
    </div>
  );
}
