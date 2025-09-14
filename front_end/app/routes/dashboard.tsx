import { TrendingUp } from "lucide-react";
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
import { StatusPill } from "../components/StatusPill";
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
  return (
    <body className="">
      <div className="bg-primary rounded-4xl max-w-7xl mx-5 xl:mx-auto mt-5 px-4 sm:px-6 lg:px-8 py-5">
        <h1 className="text-xl font-bold">Produce Section</h1>
        {/* // Placeholder for last analyzed  time */}
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
            </CardContent>
          </Card>

          {/* Line Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Line Chart - Multiple TimeStamp</CardTitle>
              <CardDescription>{LineDescription}</CardDescription>
            </CardHeader>
            <CardContent>
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
            </CardContent>
          </Card>
        </div>
        {/* Table Section */}
        <div className="rounded-2xl mt-5 p-4 bg-secondary shadow-sm">
          <h2 className="text-lg font-semibold mb-4 text-primary">
            Product Inventory
          </h2>
          {/* table */}
          <div className="overflow-x-auto rounded-2xl">
            <table className="w-full table-auto border-collapse bg-primary rounded-2xl overflow-hidden">
              <thead>
                <tr className="bg-gray-800 text-white rounded-t-2xl">
                  <th className="px-4 py-3 text-left font-medium">Product</th>
                  <th className="px-4 py-3 text-left font-medium">Category</th>
                  <th className="px-4 py-3 text-center font-medium">
                    Current Stock
                  </th>
                  <th className="px-4 py-3 text-center font-medium">Status</th>
                  <th className="px-4 py-3 text-left font-medium">
                    Last updated
                  </th>
                </tr>
              </thead>
              <tbody>
                {mockProducts.map((product, index) => (
                  <tr
                    key={product.id}
                    className={`text-center border-b border-gray-600 hover:bg-gray-700 text-white ${
                      index === mockProducts.length - 1 ? "rounded-b-2xl" : ""
                    }`}
                  >
                    <td className="px-4 py-3 text-left font-medium text-white">
                      {product.product}
                    </td>
                    <td className="px-4 py-3 text-left text-gray-300">
                      {product.category}
                    </td>
                    <td className="px-4 py-3 text-center font-semibold text-white">
                      {product.stock}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <StatusPill status={product.status} />
                    </td>
                    <td className="px-4 py-3 text-left text-gray-300">
                      {product.updatedAt}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </body>
  );
}

export default Dashboard;

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
