import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import Button from "~/components/ui/buttonCustom";
import { AlertTriangle } from "lucide-react";

type AnalysisResult = {
  product: string;
  stock_percentage: number; // 0..1
  stock_status: "low" | "normal" | "overstocked" | string;
  confidence?: number; // 0..1
  reasoning?: string;
};

type AnalysisData = {
  results?: AnalysisResult[];
  timestamp?: string;
};

function Alert() {
  const navigate = useNavigate();
  const [lowStock, setLowStock] = useState<AnalysisResult[]>([]);
  const [timestamp, setTimestamp] = useState<string | null>(null);

  const seedSampleLowStock = () => {
    const sample: AnalysisData = {
      timestamp: new Date().toISOString(),
      results: [
        {
          product: "banana",
          stock_percentage: 0.12,
          stock_status: "low",
          confidence: 0.92,
        },
        {
          product: "broccoli",
          stock_percentage: 0.22,
          stock_status: "low",
          confidence: 0.88,
        },
        {
          product: "onion",
          stock_percentage: 0.28,
          stock_status: "low",
          confidence: 0.81,
        },
      ],
    };

    localStorage.setItem("latestAnalysis", JSON.stringify(sample));
    setTimestamp(sample.timestamp ?? null);
    const items = (sample.results ?? []).filter((r) => {
      if (r.stock_status) return r.stock_status === "low";
      return (r.stock_percentage ?? 1) < 0.3;
    });
    setLowStock(items);
  };

  useEffect(() => {
    try {
      const raw = localStorage.getItem("latestAnalysis");
      if (!raw) return;
      const data: AnalysisData = JSON.parse(raw);
      setTimestamp(data.timestamp ?? null);
      const items = (data.results ?? []).filter((r) => {
        // Prefer explicit status, fallback to percentage < 30%
        if (r.stock_status) return r.stock_status === "low";
        return (r.stock_percentage ?? 1) < 0.3;
      });
      setLowStock(items);
    } catch (e) {
      console.error("Failed to parse latestAnalysis:", e);
    }
  }, []);

  const renderEmpty = () => (
    <div className="bg-white rounded-2xl p-8 text-center shadow">
      <div className="mx-auto w-12 h-12 rounded-full bg-yellow-100 flex items-center justify-center mb-4">
        <AlertTriangle className="text-yellow-600" />
      </div>
      <h2 className="text-xl font-semibold mb-2">No low-stock alerts</h2>
      <p className="text-gray-600 mb-6">
        Upload a new image to analyze stock levels and generate alerts.
      </p>
      <Button onClick={() => navigate("/upload")} variant="secondary">
        Analyze Shelf Image
      </Button>
    </div>
  );

  return (
    <body>
      <div className="bg-primary rounded-4xl max-w-7xl mx-5 xl:mx-auto mt-5 px-4 sm:px-6 lg:px-8 py-5">
        {" "}
        <h1 className="text-xl font-bold">Alert</h1>
      </div>
      <div className="bg-primary rounded-4xl max-w-7xl mx-5 xl:mx-auto mt-5 mb-5 px-4 sm:px-6 lg:px-8 py-5">
        <div className="mb-4">
          <p>
            {timestamp
              ? `Last analyzed: ${new Date(timestamp).toLocaleString()}`
              : "Run an analysis to see alerts"}
          </p>
          <div className="mt-3">
            <Button onClick={seedSampleLowStock} variant="secondary">
              Load sample low-stock data
            </Button>
          </div>
        </div>

        {lowStock.length === 0 ? (
          renderEmpty()
        ) : (
          <div className="space-y-4 text-primary">
            {lowStock.map((item, idx) => {
              const productName = item.product
                ? item.product.charAt(0).toUpperCase() + item.product.slice(1)
                : `Product ${idx + 1}`;
              const pct = Math.round((item.stock_percentage ?? 0) * 100);
              const conf =
                item.confidence != null
                  ? Math.round(item.confidence * 100)
                  : null;
              return (
                <div
                  key={idx}
                  className="bg-lowStock-bg rounded-2xl p-5 shadow flex items-center gap-4"
                >
                  <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
                    <AlertTriangle className="text-red-600" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-semibold">{productName}</h2>
                      <span className="inline-flex px-2 py-0.5 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                        Low Stock
                      </span>
                    </div>
                    <p className="text-gray-700 mt-1">
                      Stock level: <span className="font-medium">{pct}%</span>
                      {conf !== null && (
                        <span className="text-gray-500">
                          {" "}
                          · Confidence: {conf}%
                        </span>
                      )}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </body>
  );
}

export default Alert;
