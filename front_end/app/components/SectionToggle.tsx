import React, { useRef } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

type Props = {
  sections: string[];
  selected: string | null;
  onChange: (section: string) => void;
};

export default function SectionToggle({ sections, selected, onChange }: Props) {
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const scrollBy = (delta: number) => {
    try {
      scrollRef.current?.scrollBy({ left: delta, behavior: "smooth" });
    } catch {}
  };

  return (
    <div
      className="flex items-center gap-2 mt-2 mb-5"
      aria-label="Section selection"
    >
      <span className="text-sm">Section:</span>
      <button
        aria-label="Scroll sections left"
        onClick={() => scrollBy(-240)}
        className="p-1 rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300"
      >
        <ChevronLeft className="w-4 h-4" />
      </button>
      <div
        ref={scrollRef}
        className="flex gap-2 overflow-x-auto no-scrollbar"
        style={{ scrollbarWidth: "none" }}
        role="tablist"
      >
        {sections.map((s) => {
          const sel = selected === s;
          return (
            <button
              key={s}
              role="tab"
              aria-selected={sel}
              tabIndex={sel ? 0 : -1}
              onClick={() => onChange(s)}
              className={`px-3 py-1 rounded-full text-sm border whitespace-nowrap border-gray-300 ${
                sel
                  ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white "
                  : "bg-gray-200 text-gray-800 hover:bg-gray-300"
              }`}
            >
              {s}
            </button>
          );
        })}
      </div>
      <button
        aria-label="Scroll sections right"
        onClick={() => scrollBy(240)}
        className="p-1 rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300"
      >
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
}
