import { Link } from "react-router";
import Header from "../components/Header";
import Button from "../components/ui/Button";
import { Camera, BadgeInfo, ChartLine } from "lucide-react";
import { useNavigate } from "react-router";

const features = [
  {
    icon: <Camera />,
    title: "Stock Level Detection",
    description: "Use any camera to capture images of your shelves.",
  },
  {
    icon: <ChartLine />,
    title: "Capture Shelf Images",
    description:
      "Track shelf performance over time with detailed reports and analytics.",
  },
  {
    icon: <BadgeInfo />,
    title: "Out-of-Stock Alerts",
    description:
      "Receive instant alerts when products are out of stock or running low.",
  },
];

export default function Home() {
  const navigate = useNavigate();
  return (
    <div className="flex items-center justify-center px-10 py-10">
      <div className="flex flex-col lg:flex-row items-center justify-center">
        {/* hero section */}
        <div className="lg:mr-10">
          <h1 className="justify-start text-primary text-5xl/15 font-bold mb-4">
            Transform your Shelf Management with Freshtify
          </h1>
          <p className="self-stretch justify-start text-primary text-2xl font-regular mb-4">
            Our platform uses advanced AI to analyze shelf images and provide
            actionable insights
          </p>
          <Button
            size="large"
            className="mb-5"
            onClick={() => navigate("/upload")}
          >
            Get Started
          </Button>
        </div>

        {/* features section */}
        <div className="flex flex-col items-center justify-center bg-primary rounded-4xl p-10 border-5 border-indigo-400 shadow-2xl">
          <h1 className="justify-start self-start text-4xl font-bold mb-4">
            Key Features
          </h1>
          <p className="justify-start text-2xl font-regular mb-4">
            ShelfSight offers a range of features to help you manage your
            shelves effectively.
          </p>
          {/* feature cards */}
          <div className="flex flex-col md:flex-row items-stretch justify-center gap-5 w-full">
            {features.map((feature, index) => (
              // cards
              <div
                key={index}
                className="bg-featureCard rounded-4xl p-10 flex-1 flex flex-col items-start border-2 border-blue-200 shadow-lg hover:translate-y-[-10px] transition-all duration-300"
              >
                <div className="mb-4">{feature.icon}</div>
                <h1 className="text-2xl font-bold mb-4">{feature.title}</h1>
                <p className="text-xl flex-1 font-regular">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
