import { TrendingUp, AlertTriangle } from "lucide-react";
import { useState, useEffect } from "react";
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

function Dashboard() {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [products, setProducts] = useState(mockProducts);
  const [summaryStats, setSummaryStats] = useState({
    total: 48,
    low: 5,
    medium: 12,
    high: 33,
  });
  const [lowItems, setLowItems] = useState<AnalysisResult[]>([]);
  const [showLowAlert, setShowLowAlert] = useState<boolean>(false);

  useEffect(() => {
    // Get the latest analysis data from localStorage
    const latestAnalysis = localStorage.getItem("latestAnalysis");
    if (latestAnalysis) {
      try {
        const data = JSON.parse(latestAnalysis);
        console.log("Dashboard received analysis data:", data);
        setAnalysisData(data);

        // Convert API response to dashboard format
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

  // Create chart data from real products
  const BarChartData = products.map((product) => ({
    name: product.product,
    stock: parseInt(product.stock.replace("%", "")),
  }));

  // Create dynamic line chart data based on current products
  const createLineChartData = () => {
    if (products.length === 0) return []; // Return empty array if no products

    const productNames = products.map((p) => p.product);
    const currentTime = new Date().toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });

    // Create a data point with current stock levels
    const currentData: any = { time: currentTime };
    productNames.forEach((name) => {
      const product = products.find((p) => p.product === name);
      if (product) {
        currentData[name] = parseInt(product.stock.replace("%", ""));
      }
    });

    return [currentData];
  };

  const dynamicLineChartData = createLineChartData();

  return (
    <body className="">
      <div className="bg-primary rounded-4xl max-w-7xl mx-5 xl:mx-auto mt-5 px-4 sm:px-6 lg:px-8 py-5">
        <h1 className="text-xl font-bold">Produce Section</h1>
        {/* // Placeholder for last analyzed  time */}
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
          </div>
        </div>
      </div>

      <div className="bg-primary rounded-4xl max-w-7xl mx-5 xl:mx-auto mt-5 mb-5 px-4 sm:px-6 lg:px-8 py-5">
        <h1 className="text-xl font-bold">Product Overview</h1>
        {/* Chart Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Bar Chart for latest record */}
          <Card>
            <CardHeader>
              <CardTitle>Bar Chart of Latest TimeStamp</CardTitle>
              <CardDescription>{BarDescription}</CardDescription>
            </CardHeader>
            <CardContent>
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
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-500">
                  No data available. Upload an image to see stock levels.
                </div>
              )}
            </CardContent>
          </Card>

          {/* Line Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Line Chart - Multiple TimeStamp</CardTitle>
              <CardDescription>{LineDescription}</CardDescription>
            </CardHeader>
            <CardContent>
              {dynamicLineChartData.length > 0 ? (
                <ChartContainer config={chartConfig}>
                  <LineChart
                    accessibilityLayer
                    data={dynamicLineChartData}
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
                    {getSeriesKeys(dynamicLineChartData).map((key, i) => {
                      return (
                        <Line
                          key={key}
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
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-500">
                  No data available. Upload an image to see stock levels.
                </div>
              )}
            </CardContent>
          </Card>
        </div>
        {/* Table Section */}
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
        </div>
      </div>
    </body>
  );
}

export default Dashboard;

export const mockProducts = [
  {
    id: 1,
    product: "Banana",
    stock: "80%",
    status: "High",
    confidence: "92%",
    updatedAt: "Today, 2:45 PM",
  },
  {
    id: 2,
    product: "Broccoli",
    stock: "20%",
    status: "Low",
    confidence: "88%",
    updatedAt: "Today, 2:42 PM",
  },
  {
    id: 3,
    product: "Avocado",
    stock: "60%",
    status: "Medium",
    confidence: "85%",
    updatedAt: "Today, 2:40 PM",
  },
  {
    id: 4,
    product: "Tomato",
    stock: "95%",
    status: "High",
    confidence: "94%",
    updatedAt: "Today, 2:38 PM",
  },
  {
    id: 5,
    product: "Onion",
    stock: "45%",
    status: "Medium",
    confidence: "90%",
    updatedAt: "Today, 2:35 PM",
  },
  {
    id: 6,
    product: "Apple",
    stock: "10%",
    status: "Low",
    confidence: "87%",
    updatedAt: "Today, 2:30 PM",
  },
  {
    id: 7,
    product: "Carrot",
    stock: "85%",
    status: "High",
    confidence: "91%",
    updatedAt: "Today, 2:25 PM",
  },
];
