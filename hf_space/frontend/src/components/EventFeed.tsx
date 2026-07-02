"use client";
import { useEffect, useState } from "react";

const EVENT_COLORS: Record<string, string> = {
  ORDER_PLACED: "bg-emerald-900 text-emerald-300",
  PAYMENT_CAPTURED: "bg-blue-900 text-blue-300",
  ORDER_SHIPPED: "bg-purple-900 text-purple-300",
  DELIVERY_CONFIRMED: "bg-amber-900 text-amber-300",
  RETURN_REQUESTED: "bg-red-900 text-red-300",
};

export function EventFeed() {
  const [events, setEvents] = useState<any[]>([]);
  useEffect(() => {
    const poll = () => fetch("/api/events?limit=20")
      .then(r => r.json()).then(setEvents).catch(console.error);
    poll();
    const interval = setInterval(poll, 2000);
    return () => clearInterval(interval);
  }, []);
  return (
    <div className="space-y-2">
      {events.map((e: any) => (
        <div key={e.id} className="flex items-center gap-3 bg-zinc-800 rounded-lg px-4 py-2 border border-zinc-700">
          <span className={`text-xs font-mono px-2 py-1 rounded ${EVENT_COLORS[e.event_type] ?? "bg-zinc-700 text-zinc-300"}`}>
            {e.event_type}
          </span>
          <span className="text-zinc-400 text-sm">{e.customer_id}</span>
          <span className="text-zinc-600 text-xs ml-auto">{e.published_at?.slice(0,19)}</span>
        </div>
      ))}
    </div>
  );
}