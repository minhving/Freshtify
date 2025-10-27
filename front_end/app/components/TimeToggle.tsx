import React from "react";

type Props = {
  times: string[];
  selected: string | null;
  onChange: (time: string) => void;
  counts?: Record<string, number>;
};

export default function TimeToggle({
  times,
  selected,
  onChange,
  counts,
}: Props) {
  const handleKey = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (!times || times.length === 0 || !selected) return;
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    e.preventDefault();
    const current = times.indexOf(selected || "");
    const dir = e.key === "ArrowRight" ? 1 : -1;
    const next = (current + dir + times.length) % times.length;
    onChange(times[next]);
  };

  return (
    <div
      className="flex items-center gap-2 mt-2 mb-5"
      role="tablist"
      aria-label="Time selection"
      onKeyDown={handleKey}
    >
      <span className="text-sm">Time:</span>
      {times.map((t) => {
        const isSelected = selected === t;
        const count = counts?.[t] ?? undefined;
        return (
          <button
            key={t}
            role="tab"
            aria-selected={isSelected}
            tabIndex={isSelected ? 0 : -1}
            onClick={() => onChange(t)}
            className={`px-3 py-1 rounded-full text-sm border border-gray-300 ${
              isSelected
                ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white "
                : "bg-gray-200 text-gray-800 hover:bg-gray-300"
            }`}
            title={count != null ? `Sections: ${count}` : undefined}
          >
            <span className="align-middle">{t}</span>
            {count != null && (
              <span
                className={`ml-2 inline-flex items-center justify-center text-xs px-1.5 py-0.5 rounded-full ${isSelected ? "bg-white text-blue-700" : "bg-gray-300 text-gray-700"}`}
              >
                {count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
