import { useState } from "react";

interface ModelSelectorProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
  disabled?: boolean;
}

const models = [
  {
    id: "basic-cv",
    name: "Basic Computer Vision",
    description: "Fast, CPU-only processing",
    recommended: true,
  },
  {
    id: "qwen-vl",
    name: "Qwen-VL (Advanced)",
    description: "AI-powered analysis (requires GPU)",
    recommended: false,
  },
  {
    id: "sam",
    name: "SAM Segmentation",
    description: "Image segmentation model",
    recommended: false,
  },
];

export default function ModelSelector({ selectedModel, onModelChange, disabled }: ModelSelectorProps) {
  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold text-white mb-4">Select AI Model</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {models.map((model) => (
          <div
            key={model.id}
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
              selectedModel === model.id
                ? "border-blue-400 bg-blue-500/10"
                : "border-gray-600 bg-gray-700/50 hover:border-gray-500"
            } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
            onClick={() => !disabled && onModelChange(model.id)}
          >
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-white font-medium">{model.name}</h4>
              {model.recommended && (
                <span className="text-xs bg-green-500 text-white px-2 py-1 rounded">
                  Recommended
                </span>
              )}
            </div>
            <p className="text-gray-400 text-sm">{model.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
