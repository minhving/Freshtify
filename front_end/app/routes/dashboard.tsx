<<<<<<< HEAD
import { TrendingUp } from "lucide-react";
=======
import {
  TrendingUp,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { Link } from "react-router";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogAction,
  AlertDialogCancel,
} from "../components/ui/alert-dialog";
>>>>>>> 16000a83873aac5a7b357209a359371a5485bce8
import {
  Bar,
  BarChart,
  CartesianGrid,
  XAxis,
  Cell,
  CartesianAxis,
  Line,
  LineChart,
} from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import type { ChartConfig } from "../components/ui/chart";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "../components/ui/chart";
<<<<<<< HEAD
const BarDescription = "A bar chart";
const LineDescription = "A line chart";

const LineChartData = [
  { time: "T1", Banana: 85, Broccoli: 50, Avocado: 90, Onion: 100, Tomato: 65 },
  {
    time: "T2",
    Banana: 70,
    Broccoli: 60,
    Avocado: null,
    Onion: 95,
    Tomato: 80,
  },
  { time: "T3", Banana: 90, Broccoli: 55, Avocado: 88, Onion: 100, Tomato: 75 },
  { time: "T4", Banana: 80, Broccoli: 48, Avocado: 92, Onion: 97, Tomato: 85 },
];
// Dynamically get the keys for the series (excluding 'time')
const seriesKeys = Object.keys(LineChartData[0]).filter((k) => k !== "time");
// Get the latest snapshot (last entry in the array)
const { time, ...latestSnapShot } = LineChartData[LineChartData.length - 1];

const BarChartData = seriesKeys.map((key) => ({
  name: key,
  stock: latestSnapShot[key as keyof typeof latestSnapShot],
}));
console.log("BarChartData:", BarChartData);
=======
import TimeToggle from "../components/TimeToggle";

// Type definitions
interface AnalysisResult {
  product: string;
  stock_percentage: number;
  stock_status: string;
  confidence: number;
  bounding_box: any;
  reasoning: string;
}

interface AnalysisData {
  success: boolean;
  message: string;
  processing_time: number;
  timestamp: string;
  results: AnalysisResult[];
  model_used: string;
  image_metadata: {
    filename: string;
    size: number;
  };
}

const BarDescription = "A bar chart";
const LineDescription = "A line chart";

// Dynamic series keys will be created based on current products
const getSeriesKeys = (data: any[]) => {
  if (data.length === 0) return [];
  return Object.keys(data[0]).filter((k) => k !== "time");
};
>>>>>>> 16000a83873aac5a7b357209a359371a5485bce8

const chartConfig = {
  stock: {
    label: "Stock Level",
    color: "var(--chart-1)",
  },
} satisfies ChartConfig;

const chartcolors = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--chart-6)",
];

<<<<<<< HEAD
function Dashboard() {
=======
// Normalize a label into a base product key (strip time and index)
const getBaseProduct = (label: string): string => {
  let s = (label || "").toLowerCase();
  // remove trailing time e.g. (T0)
  s = s.replace(/\s*\([^)]*\)$/, "");
  // remove trailing section index e.g. " 12"
  s = s.replace(/\s+\d+$/, "");
  return s.trim();
};

// Deterministic color generator for any (unknown) product
const colorCache = new Map<string, string>();
const colorForBase = (base: string): string => {
  const key = base || "unknown";
  const cached = colorCache.get(key);
  if (cached) return cached;
  // djb2 hash
  let hash = 5381;
  for (let i = 0; i < key.length; i++)
    hash = (hash << 5) + hash + key.charCodeAt(i);
  // Map to hue wheel and pleasant saturation/lightness
  const hue = (hash >>> 0) % 360;
  const color = `hsl(${hue}, 65%, 50%)`;
  colorCache.set(key, color);
  return color;
};

function Dashboard() {
  console.log("🔍 DEBUG: Dashboard component is rendering");
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [groupedResults, setGroupedResults] = useState<Record<
    string,
    AnalysisResult[]
  > | null>(null);
  const [availableTimes, setAvailableTimes] = useState<string[]>([]);
  const [selectedTime, setSelectedTime] = useState<string | null>(null);
  const [products, setProducts] = useState<any[]>([]);
  const [summaryStats, setSummaryStats] = useState({
    total: 0,
    low: 0,
    medium: 0,
    high: 0,
  });
  const [lowItems, setLowItems] = useState<AnalysisResult[]>([]);
  const [showLowAlert, setShowLowAlert] = useState<boolean>(false);
  const [lineData, setLineData] = useState<any[]>([]);
  const [availableSections, setAvailableSections] = useState<string[]>([]);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const sectionScrollRef = useRef<HTMLDivElement | null>(null);
  const scrollSectionBy = (delta: number) => {
    try {
      sectionScrollRef.current?.scrollBy({ left: delta, behavior: "smooth" });
    } catch {}
  };
  useEffect(() => {
    console.log("🔍 DEBUG: Dashboard useEffect triggered");
    // Get the latest analysis data from localStorage
    const latestAnalysis = localStorage.getItem("latestAnalysis");

    console.log("🔍 DEBUG: latestAnalysis from localStorage:", latestAnalysis);
    if (latestAnalysis) {
      try {
        const data = JSON.parse(latestAnalysis);
        console.log("🔍 DEBUG: Dashboard received analysis data:", data);
        setAnalysisData(data);

        // Handle grouped results (T0, T1, ...) without averaging
        if (
          data.results &&
          !Array.isArray(data.results) &&
          typeof data.results === "object"
        ) {
          const grouped = data.results as Record<string, AnalysisResult[]>;
          setGroupedResults(grouped);
          const times = Object.keys(grouped);
          const sortedTimes = [...times].sort((a, b) => {
            const na = parseInt(String(a).replace(/\D/g, "")) || 0;
            const nb = parseInt(String(b).replace(/\D/g, "")) || 0;
            return na - nb;
          });
          setAvailableTimes(sortedTimes);
          const saved =
            typeof window !== "undefined"
              ? localStorage.getItem("selectedTimeKey")
              : null;
          const initialTime =
            saved && grouped[saved] ? saved : sortedTimes[0] || null;
          setSelectedTime(initialTime);

          const selectedArray = initialTime ? grouped[initialTime] || [] : [];
          const realProducts = selectedArray.map(
            (result: AnalysisResult, index: number) => ({
              id: index + 1,
              product:
                result.product.charAt(0).toUpperCase() +
                result.product.slice(1),
              stock: `${Math.round((result.stock_percentage ?? 0) * 100)}%`,
              status:
                result.stock_status === "low"
                  ? "Low"
                  : result.stock_status === "normal"
                    ? "Medium"
                    : result.stock_status === "overstocked"
                      ? "High"
                      : "Medium",
              confidence: `${Math.round((result.confidence ?? 0) * 100)}%`,
              reasoning: result.reasoning || "AI analysis completed",
              updatedAt: new Date().toLocaleString("en-US", {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              }),
            })
          );
          setProducts(realProducts);

          // Build section list across all times
          const sectionSet = new Set<string>();
          Object.values(grouped).forEach((arr: any) => {
            (arr || []).forEach((item: any) => {
              const base = String(item.product || "").replace(
                /\s*\([^)]*\)$/,
                ""
              );
              if (base) sectionSet.add(base);
            });
          });
          const sections = Array.from(sectionSet).sort((a, b) =>
            a.localeCompare(b, undefined, {
              numeric: true,
              sensitivity: "base",
            })
          );
          setAvailableSections(sections);
          const savedSection =
            typeof window !== "undefined"
              ? localStorage.getItem("selectedSectionKey")
              : null;
          const initialSection =
            savedSection && sections.includes(savedSection)
              ? savedSection
              : sections[0] || null;
          setSelectedSection(initialSection);

          // Update low items alert for the initially selected time
          const lowsInitial = selectedArray.filter((r: AnalysisResult) =>
            r.stock_status
              ? r.stock_status === "low"
              : (r.stock_percentage ?? 1) < 0.3
          );
          setLowItems(lowsInitial);
          setShowLowAlert(lowsInitial.length > 0);

          const lowCount = realProducts.filter(
            (p: any) => p.status === "Low"
          ).length;
          const mediumCount = realProducts.filter(
            (p: any) => p.status === "Medium"
          ).length;
          const highCount = realProducts.filter(
            (p: any) => p.status === "High"
          ).length;
          setSummaryStats({
            total: realProducts.length,
            low: lowCount,
            medium: mediumCount,
            high: highCount,
          });

          // Store historical entry (optional)
          const historicalData = JSON.parse(
            localStorage.getItem("historicalData") || "[]"
          );
          const newEntry = {
            timestamp: new Date().toISOString(),
            groupedResults: grouped,
          };
          historicalData.push(newEntry);
          if (historicalData.length > 10)
            historicalData.splice(0, historicalData.length - 10);
          localStorage.setItem(
            "historicalData",
            JSON.stringify(historicalData)
          );

          if (data.model_used) {
            setAnalysisData((prev: any) => ({
              ...prev,
              modelUsed: data.model_used,
              processingTime: data.processing_time,
              timestamp: data.timestamp,
            }));
          }
          return; // prevent falling through to array-based logic
        }

        // Convert API response to dashboard format (array results)
        if (data.results && data.results.length > 0) {
          // Compute low stock items for inline alert
          const lows = data.results.filter((r: AnalysisResult) =>
            r.stock_status
              ? r.stock_status === "low"
              : (r.stock_percentage ?? 1) < 0.3
          );
          setLowItems(lows);
          setShowLowAlert(lows.length > 0);

          const realProducts = data.results.map(
            (result: AnalysisResult, index: number) => ({
              id: index + 1,
              product:
                result.product.charAt(0).toUpperCase() +
                result.product.slice(1),
              stock: `${Math.round(result.stock_percentage * 100)}%`,
              status:
                result.stock_status === "low"
                  ? "Low"
                  : result.stock_status === "normal"
                    ? "Medium"
                    : result.stock_status === "overstocked"
                      ? "High"
                      : "Medium",
              confidence: `${Math.round(result.confidence * 100)}%`,
              reasoning: result.reasoning || "AI analysis completed",
              updatedAt: new Date().toLocaleString("en-US", {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              }),
            })
          );

          setProducts(realProducts);

          // Store historical data for line chart
          const historicalData = JSON.parse(
            localStorage.getItem("historicalData") || "[]"
          );
          const newEntry = {
            timestamp: new Date().toISOString(),
            results: data.results,
            imageCount: data.image_metadata?.image_count || 1,
          };
          console.log("🔍 DEBUG: Storing new entry:", newEntry);
          historicalData.push(newEntry);

          // Keep only last 10 analyses to prevent localStorage from getting too large
          if (historicalData.length > 10) {
            historicalData.splice(0, historicalData.length - 10);
          }

          localStorage.setItem(
            "historicalData",
            JSON.stringify(historicalData)
          );
          console.log("🔍 DEBUG: Updated historicalData:", historicalData);

          // Calculate summary stats
          const lowCount = realProducts.filter(
            (p: any) => p.status === "Low"
          ).length;
          const mediumCount = realProducts.filter(
            (p: any) => p.status === "Medium"
          ).length;
          const highCount = realProducts.filter(
            (p: any) => p.status === "High"
          ).length;

          setSummaryStats({
            total: realProducts.length,
            low: lowCount,
            medium: mediumCount,
            high: highCount,
          });

          // Set model and processing information
          if (data.model_used) {
            setAnalysisData((prev: any) => ({
              ...prev,
              modelUsed: data.model_used,
              processingTime: data.processing_time,
              timestamp: data.timestamp,
            }));
          }
        }
      } catch (error) {
        console.error("Error parsing analysis data:", error);
      }
    }
  }, []);

  // Persist selected time
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (selectedTime) localStorage.setItem("selectedTimeKey", selectedTime);
  }, [selectedTime]);

  // When user toggles a different time, recompute products from groupedResults
  useEffect(() => {
    if (!groupedResults || !selectedTime) return;
    console.log("🔍 DEBUG: groupedResults:", groupedResults);
    console.log("🔍 DEBUG: selectedTime:", selectedTime);
    console.log("🔍 DEBUG: groupedResults[selectedTime]:", groupedResults[selectedTime]);
    const selectedArray = groupedResults[selectedTime] || [];
    const realProducts = selectedArray.map(
      (result: AnalysisResult, index: number) => ({
        id: index + 1,
        product:
          result.product.charAt(0).toUpperCase() + result.product.slice(1),
        stock: `${Math.round((result.stock_percentage ?? 0) * 100)}%`,
        status:
          result.stock_status === "low"
            ? "Low"
            : result.stock_status === "normal"
              ? "Medium"
              : result.stock_status === "overstocked"
                ? "High"
                : "Medium",
        confidence: `${Math.round((result.confidence ?? 0) * 100)}%`,
        reasoning: result.reasoning || "AI analysis completed",
        updatedAt: new Date().toLocaleString("en-US", {
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        }),
      })
    );
    setProducts(realProducts);

    // Update low items alert for current time selection
    const lows = selectedArray.filter((r: AnalysisResult) =>
      r.stock_status
        ? r.stock_status === "low"
        : (r.stock_percentage ?? 1) < 0.3
    );
    setLowItems(lows);
    setShowLowAlert(lows.length > 0);

    const lowCount = realProducts.filter((p: any) => p.status === "Low").length;
    const mediumCount = realProducts.filter(
      (p: any) => p.status === "Medium"
    ).length;
    const highCount = realProducts.filter(
      (p: any) => p.status === "High"
    ).length;
    setSummaryStats({
      total: realProducts.length,
      low: lowCount,
      medium: mediumCount,
      high: highCount,
    });
  }, [groupedResults, selectedTime]);

  // Recompute available sections based on the currently selected time only
  useEffect(() => {
    if (!groupedResults || !selectedTime) {
      setAvailableSections([]);
      setSelectedSection(null);
      return;
    }
    const arr = groupedResults[selectedTime] || [];
    const sectionSet = new Set<string>();
    (arr || []).forEach((item: any) => {
      const base = String(item.product || "").replace(/\s*\([^)]*\)$/, "");
      if (base) sectionSet.add(base);
    });
    const sections = Array.from(sectionSet).sort((a, b) =>
      a.localeCompare(b, undefined, { numeric: true, sensitivity: "base" })
    );
    setAvailableSections(sections);
    if (!sections.includes(selectedSection || "")) {
      setSelectedSection(sections[0] || null);
    }
  }, [groupedResults, selectedTime]);

  // Persist selected time and section
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (selectedTime) localStorage.setItem("selectedTimeKey", selectedTime);
  }, [selectedTime]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (selectedSection)
      localStorage.setItem("selectedSectionKey", selectedSection);
  }, [selectedSection]);

  // Create chart data from real products
  const BarChartData = products.map((product) => ({
    name: product.product,
    stock: parseInt(product.stock.replace("%", "")),
  }));

  // Precompute counts for time toggle
  const timeCounts: Record<string, number> = Object.fromEntries(
    availableTimes.map((t) => [t, groupedResults?.[t]?.length ?? 0])
  );

  // Create line chart data from historical data - each image as separate data point
  const createLineChartData = () => {
    // Guard against SSR where window/localStorage are not available
    if (typeof window === "undefined" || typeof localStorage === "undefined") {
      return [] as any[];
    }
    const historicalData = JSON.parse(
      localStorage.getItem("historicalData") || "[]"
    );
    console.log("🔍 DEBUG: Retrieved historicalData:", historicalData);

    if (historicalData.length === 0) {
      // If no historical data, create a single data point from current products
      if (products.length === 0) return [];

      const productNames = products.map((p) => p.product);
      const currentTime = new Date().toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      });

      const currentData: any = { time: currentTime };
      productNames.forEach((name) => {
        const product = products.find((p) => p.product === name);
        if (product) {
          currentData[name] = parseInt(product.stock.replace("%", ""));
        }
      });

      return [currentData];
    }

    // Process historical data to create line chart data - each individual image result
    const lineData: any[] = [];
    let globalDataPointIndex = 0;

    historicalData.forEach((entry: any, analysisIndex: number) => {
      console.log(`🔍 DEBUG: Processing entry ${analysisIndex}:`, entry);
      const baseTime = new Date(entry.timestamp);

      // Group results by image (T0, T1, T2, etc.)
      const imageGroups: { [key: string]: any[] } = {};

      // Support both legacy array results and new groupedResults shape
      if (
        entry &&
        entry.groupedResults &&
        typeof entry.groupedResults === "object"
      ) {
        Object.entries(entry.groupedResults).forEach(([timeKey, arr]: any) => {
          imageGroups[timeKey] = Array.isArray(arr) ? arr : [];
        });
      } else if (Array.isArray(entry?.results)) {
        entry.results.forEach((result: any) => {
          // Extract image identifier (T0, T1, T2, etc.)
          const imageMatch = result.product?.match(/\(([^)]+)\)$/);
          const imageId = imageMatch ? imageMatch[1] : "T0";
          console.log(
            `🔍 DEBUG: Product "${result.product}" -> ImageId "${imageId}"`
          );

          if (!imageGroups[imageId]) {
            imageGroups[imageId] = [];
          }
          imageGroups[imageId].push(result);
        });
      } else {
        // Unknown entry shape; skip
        return;
      }

      console.log(
        `🔍 DEBUG: Image groups for entry ${analysisIndex}:`,
        imageGroups
      );

      // Create a data point for each individual image
      Object.keys(imageGroups).forEach((imageId, imageIndex) => {
        const time = new Date(
          baseTime.getTime() + imageIndex * 60000
        ).toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
        });

        const dataPoint: any = {
          time: time,
          imageId: imageId,
          analysisIndex: globalDataPointIndex + 1, // Each image gets its own unique index
        };

        // Add stock levels for each product in this image
        imageGroups[imageId].forEach((result: any) => {
          const baseProduct = result.product.replace(/\s*\([^)]*\)$/, "");
          dataPoint[baseProduct] = Math.round(result.stock_percentage * 100);
        });

        lineData.push(dataPoint);
        globalDataPointIndex++;
        console.log(`🔍 DEBUG: Created data point for ${imageId}:`, dataPoint);
      });
    });

    console.log("🔍 DEBUG: Final line chart data:", lineData);
    return lineData;
  };

  // Compute line chart data on client after state changes
  useEffect(() => {
    try {
      // If section selected and grouped data available, build per-section across times (T0, T1, ...)
      if (groupedResults && selectedSection && availableTimes.length > 0) {
        const series: any[] = [];
        // Use availableTimes order
        availableTimes.forEach((t) => {
          const arr = groupedResults[t] || [];
          const match = arr.find(
            (item: any) =>
              String(item.product || "").replace(/\s*\([^)]*\)$/, "") ===
              selectedSection
          );
          const dp: any = { time: t };
          if (match) {
            dp[selectedSection] = Math.round(
              (match.stock_percentage ?? 0) * 100
            );
          }
          series.push(dp);
        });
        setLineData(series);
        return;
      }

      const data = createLineChartData();
      setLineData(data);
      console.log("🔍 DEBUG: lineData updated:", data);
    } catch (e) {
      console.warn("line chart data build failed", e);
      setLineData([]);
    }
  }, [groupedResults, products, selectedTime, selectedSection, availableTimes]);

>>>>>>> 16000a83873aac5a7b357209a359371a5485bce8
  return (
    <body className="">
      <div className="bg-primary rounded-4xl max-w-7xl mx-5 xl:mx-auto mt-5 px-4 sm:px-6 lg:px-8 py-5">
        <h1 className="text-xl font-bold">Produce Section</h1>
        {/* // Placeholder for last analyzed  time */}
<<<<<<< HEAD
        <p>Last analyzed: Today, 2:45PM</p>
        {/* Grid for total products, low stock, medium stock, high stock */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mt-5">
          {/* Total Produts */}
          <div className="bg-secondary rounded-2xl px-4 py-4">
            <h4 className="text-primary font-medium">Total Products</h4>
            <p className="text-primary text-3xl font-semibold">48</p>
          </div>
          <div className="bg-lowStock-bg rounded-2xl px-4 py-4">
            <h4 className="text-lowStock-text font-medium">Low Stocks</h4>
            <p className="text-primary text-3xl font-semibold">5</p>
          </div>
          <div className="bg-mediumStock-bg rounded-2xl px-4 py-4">
            <h4 className="text-mediumStock-text font-medium">Medium Stock</h4>
            <p className="text-primary text-3xl font-semibold">12</p>
          </div>
          <div className="bg-highStock-bg rounded-2xl px-4 py-4">
            <h4 className="text-highStock-text font-medium">High Stock</h4>
            <p className="text-primary text-3xl font-semibold">33</p>
=======
        <p>
          Last analyzed:{" "}
          {analysisData && analysisData.timestamp
            ? new Date(analysisData.timestamp).toLocaleString()
            : "Today, 2:45PM"}
        </p>
        <AlertDialog
          open={showLowAlert && lowItems.length > 0}
          onOpenChange={setShowLowAlert}
        >
          <AlertDialogContent className="">
            <AlertDialogHeader>
              <AlertDialogTitle className="flex items-center gap-2 text-lowStock-text">
                <AlertTriangle className="w-5 h-5 text-lowStock-text" />
                Low stock detected
              </AlertDialogTitle>
              <AlertDialogDescription>
                {lowItems.length === 1
                  ? `${lowItems[0].product.charAt(0).toUpperCase()}${lowItems[0].product.slice(1)} is low on stock.`
                  : `${lowItems
                      .map(
                        (i) =>
                          i.product.charAt(0).toUpperCase() + i.product.slice(1)
                      )
                      .slice(0, 3)
                      .join(
                        ", "
                      )}${lowItems.length > 3 ? ` and ${lowItems.length - 3} more` : ""} are low on stock.`}
              </AlertDialogDescription>
            </AlertDialogHeader>
            <ul className="mt-2 space-y-1 text-sm">
              {lowItems.map((i, idx) => (
                <li key={idx} className="flex justify-between">
                  <span className="text-lowStock-text">
                    {i.product.charAt(0).toUpperCase() + i.product.slice(1)}
                  </span>
                  <span className="text-lowStock-text">
                    {Math.round(i.stock_percentage * 100)}%
                  </span>
                </li>
              ))}
            </ul>
            <AlertDialogFooter>
              <AlertDialogCancel onClick={() => setShowLowAlert(false)}>
                Dismiss
              </AlertDialogCancel>
              <AlertDialogAction asChild>
                <Link to="/alert">View details</Link>
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
        {/* Grid for total products, low stock, medium stock, high stock */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mt-5">
          {/* Total Products */}
          <div className="bg-secondary rounded-2xl px-4 py-4">
            <h4 className="text-primary font-medium">Total Products</h4>
            <p className="text-primary text-3xl font-semibold">
              {summaryStats.total}
            </p>
          </div>
          <div className="bg-lowStock-bg rounded-2xl px-4 py-4">
            <h4 className="text-lowStock-text font-medium">Low Stocks</h4>
            <p className="text-primary text-3xl font-semibold">
              {summaryStats.low}
            </p>
          </div>
          <div className="bg-mediumStock-bg rounded-2xl px-4 py-4">
            <h4 className="text-mediumStock-text font-medium">Medium Stock</h4>
            <p className="text-primary text-3xl font-semibold">
              {summaryStats.medium}
            </p>
          </div>
          <div className="bg-highStock-bg rounded-2xl px-4 py-4">
            <h4 className="text-highStock-text font-medium">High Stock</h4>
            <p className="text-primary text-3xl font-semibold">
              {summaryStats.high}
            </p>
>>>>>>> 16000a83873aac5a7b357209a359371a5485bce8
          </div>
        </div>
      </div>

      <div className="bg-primary rounded-4xl max-w-7xl mx-5 xl:mx-auto mt-5 mb-5 px-4 sm:px-6 lg:px-8 py-5">
        <h1 className="text-xl font-bold">Product Overview</h1>
<<<<<<< HEAD
=======
        {availableTimes.length > 0 && (
          <TimeToggle
            times={availableTimes}
            selected={selectedTime}
            onChange={setSelectedTime}
            counts={timeCounts}
          />
        )}

        {/* Section toggle */}
        {availableSections.length > 0 && (
          <div
            className="flex items-center gap-2 mt-2 mb-5"
            aria-label="Section selection"
          >
            <span className="text-sm">Section:</span>
            <button
              aria-label="Scroll sections left"
              onClick={() => scrollSectionBy(-240)}
              className="p-1 rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <div
              ref={sectionScrollRef}
              className="flex gap-2 overflow-x-auto no-scrollbar"
              style={{ scrollbarWidth: "none" }}
              role="tablist"
            >
              {availableSections.map((s) => {
                const sel = selectedSection === s;
                return (
                  <button
                    key={s}
                    role="tab"
                    aria-selected={sel}
                    tabIndex={sel ? 0 : -1}
                    onClick={() => setSelectedSection(s)}
                    className={`px-3 py-1 rounded-full text-sm border whitespace-nowrap border-gray-300 ${sel ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white " : "bg-gray-200 text-gray-800 hover:bg-gray-300"}`}
                  >
                    {s}
                  </button>
                );
              })}
            </div>
            <button
              aria-label="Scroll sections right"
              onClick={() => scrollSectionBy(240)}
              className="p-1 rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}
>>>>>>> 16000a83873aac5a7b357209a359371a5485bce8
        {/* Chart Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Bar Chart for latest record */}
          <Card>
            <CardHeader>
              <CardTitle>Bar Chart of Latest TimeStamp</CardTitle>
              <CardDescription>{BarDescription}</CardDescription>
            </CardHeader>
            <CardContent>
<<<<<<< HEAD
              <ChartContainer config={chartConfig}>
                <BarChart accessibilityLayer data={BarChartData}>
                  <CartesianGrid vertical={false} />
                  <XAxis
                    dataKey="name"
                    tickLine={false}
                    tickMargin={10}
                    axisLine={false}
                    // tickFormatter={(value) => value.slice(0, 3)}
                  />
                  <ChartTooltip
                    cursor={false}
                    content={<ChartTooltipContent hideLabel />}
                  />
                  <Bar dataKey="stock" radius={8}>
                    {BarChartData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={chartcolors[index % chartcolors.length]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ChartContainer>
=======
              {BarChartData.length > 0 ? (
                <ChartContainer config={chartConfig}>
                  <BarChart accessibilityLayer data={BarChartData}>
                    <CartesianGrid vertical={false} />
                    <XAxis
                      dataKey="name"
                      tickLine={false}
                      tickMargin={10}
                      axisLine={false}
                    />
                    <ChartTooltip
                      cursor={false}
                      content={<ChartTooltipContent />}
                    />
                    <Bar dataKey="stock" radius={8}>
                      {BarChartData.map((entry, index) => {
                        const base = getBaseProduct(entry.name);
                        const fill = colorForBase(base);
                        return <Cell key={`cell-${index}`} fill={fill} />;
                      })}
                    </Bar>
                  </BarChart>
                </ChartContainer>
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-500">
                  No data available. Upload an image to see stock levels.
                </div>
              )}
>>>>>>> 16000a83873aac5a7b357209a359371a5485bce8
            </CardContent>
          </Card>

          {/* Line Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Line Chart - Multiple TimeStamp</CardTitle>
              <CardDescription>{LineDescription}</CardDescription>
            </CardHeader>
            <CardContent>
<<<<<<< HEAD
              <ChartContainer config={chartConfig}>
                <LineChart
                  accessibilityLayer
                  data={LineChartData}
                  margin={{
                    left: 12,
                    right: 12,
                  }}
                >
                  <CartesianGrid vertical={false} />
                  <XAxis
                    dataKey="time"
                    tickLine={false}
                    axisLine={false}
                    tickMargin={8}
                    tickFormatter={(value) => value.slice(0, 3)}
                  />
                  <ChartTooltip
                    cursor={false}
                    content={<ChartTooltipContent />}
                  />
                  {seriesKeys.map((key, i) => {
                    return (
                      <Line
                        dataKey={key}
                        type="monotone"
                        stroke={chartcolors[i % chartcolors.length]}
                        strokeWidth={2}
                        dot={true}
                      />
                    );
                  })}
                </LineChart>
              </ChartContainer>
=======
              {lineData.length > 0 ? (
                <ChartContainer config={chartConfig}>
                  <LineChart
                    accessibilityLayer
                    data={lineData}
                    margin={{
                      left: 12,
                      right: 12,
                    }}
                  >
                    <CartesianGrid vertical={false} />
                    <XAxis
                      dataKey="time"
                      tickLine={false}
                      axisLine={false}
                      tickMargin={8}
                      tickFormatter={(value) => value.slice(0, 3)}
                    />
                    <ChartTooltip
                      cursor={false}
                      content={<ChartTooltipContent />}
                    />
                    {getSeriesKeys(lineData).map((key, i) => {
                      return (
                        <Line
                          key={key}
                          dataKey={key}
                          type="monotone"
                          stroke={chartcolors[i % chartcolors.length]}
                          strokeWidth={2}
                          dot={{
                            fill: chartcolors[i % chartcolors.length],
                            strokeWidth: 2,
                            r: 4,
                          }}
                        />
                      );
                    })}
                  </LineChart>
                </ChartContainer>
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-500">
                  No data available. Upload an image to see stock levels.
                </div>
              )}
>>>>>>> 16000a83873aac5a7b357209a359371a5485bce8
            </CardContent>
          </Card>
        </div>
        {/* Table Section */}
<<<<<<< HEAD
        <div className="rounded-2xl mt-5 p-4 ">
          <table className="table-auto ">
            <thead className="">
              <tr className="bg-secondary text-primary rounded-2xl">
                <th>Product</th>
                <th>Category</th>
                <th>Current Stock</th>
                <th>Status</th>
                <th>Last updated</th>
              </tr>
              {mockProducts.map((product) => (
                <tr key={product.id} className="text-center">
                  <td>{product.product}</td>
                  <td>{product.category}</td>
                  <td>{product.stock}</td>
                  <td>{product.status}</td>
                  <td>{product.updatedAt}</td>
                </tr>
              ))}
            </thead>
          </table>
=======
        <div className="rounded-2xl mt-5 bg-white shadow-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              Stock Inventory
            </h2>
            <p className="text-sm text-gray-600">
              Current stock levels for all products
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Stock Level
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Updated
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {products.map((product, index) => (
                  <tr
                    key={product.id}
                    className={index % 2 === 0 ? "bg-white" : "bg-gray-50"}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                            <span className="text-white font-semibold text-sm">
                              {product.product.charAt(0)}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {product.product}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-1">
                          <div className="text-sm font-medium text-gray-900">
                            {product.stock}
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                            <div
                              className={`h-2 rounded-full ${
                                product.status === "Low"
                                  ? "bg-red-500"
                                  : product.status === "High"
                                    ? "bg-green-500"
                                    : "bg-yellow-500"
                              }`}
                              style={{
                                width: product.stock.replace("%", "") + "%",
                              }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          product.status === "Low"
                            ? "bg-red-100 text-red-800"
                            : product.status === "High"
                              ? "bg-green-100 text-green-800"
                              : "bg-yellow-100 text-yellow-800"
                        }`}
                      >
                        {product.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {product.confidence || "N/A"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {product.updatedAt}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {products.length === 0 && (
            <div className="text-center py-12">
              <div className="mx-auto h-12 w-12 text-gray-400">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                  />
                </svg>
              </div>
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                No products found
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Upload an image to analyze stock levels.
              </p>
            </div>
          )}
>>>>>>> 16000a83873aac5a7b357209a359371a5485bce8
        </div>
      </div>
    </body>
  );
}

export default Dashboard;

<<<<<<< HEAD
{
  /* shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)] */
}

export const mockProducts = [
  {
    id: 1,
    product: "Banana",
    category: "Fruit",
    stock: "80%",
    status: "High",
    updatedAt: "Today, 2:45 PM",
  },
  {
    id: 2,
    product: "Broccoli",
    category: "Vegetable",
    stock: "20%",
    status: "Low",
    updatedAt: "Today, 2:42 PM",
  },
  {
    id: 3,
    product: "Avocado",
    category: "Fruit",
    stock: "60%",
    status: "Medium",
    updatedAt: "Today, 2:40 PM",
  },
  {
    id: 4,
    product: "Tomato",
    category: "Vegetable",
    stock: "95%",
    status: "High",
    updatedAt: "Today, 2:38 PM",
  },
  {
    id: 5,
    product: "Onion",
    category: "Vegetable",
    stock: "45%",
    status: "Medium",
    updatedAt: "Today, 2:35 PM",
  },
  {
    id: 6,
    product: "Apple",
    category: "Fruit",
    stock: "10%",
    status: "Low",
    updatedAt: "Today, 2:30 PM",
  },
  {
    id: 7,
    product: "Carrot",
    category: "Vegetable",
    stock: "85%",
    status: "High",
    updatedAt: "Today, 2:25 PM",
  },
];
=======
// Removed mock products. Empty state is the default now.
>>>>>>> 16000a83873aac5a7b357209a359371a5485bce8
