import { Spinner } from "../ui/Spinner/index";

interface AnalyzingOverlayProps {
  isVisible: boolean;
  progress: number;
  fileCount: number;
}

export default function AnalyzingOverlay({
  isVisible,
  progress,
  fileCount,
}: AnalyzingOverlayProps) {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-primary flex items-center justify-center z-50">
      <div className="bg-background rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl">
        <div className="text-center">
          {/* Loading Spinner */}
          <div className="mb-6 flex justify-center">
            <Spinner variant="bars" className="h-16 w-16 text-primary" />
          </div>
          {/* Analyzing Text */}
          <h3 className="text-2xl font-bold text-primary mb-2">
            Analyzing Images
          </h3>
          <p className="text-secondary-foreground mb-6">
            Processing {fileCount} image{fileCount > 1 ? "s" : ""}...
          </p>
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
            <div
              className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${Math.min(progress, 100)}%` }}
            ></div>
          </div>
          {/* Progress Percentage */}
          <p className="text-sm text-gray-500">
            {Math.round(Math.min(progress, 100))}% Complete
          </p>
          {/* Analysis Steps */}
          <div className="mt-6 text-left">
            <div className="flex items-center mb-2">
              <div
                className={`w-3 h-3 rounded-full mr-3 ${
                  progress > 20 ? "bg-green-500" : "bg-gray-300"
                }`}
              ></div>
              <span
                className={`text-sm ${
                  progress > 20 ? "text-green-600" : "text-gray-500"
                }`}
              >
                Uploading images
              </span>
            </div>
            <div className="flex items-center mb-2">
              <div
                className={`w-3 h-3 rounded-full mr-3 ${
                  progress > 50 ? "bg-green-500" : "bg-gray-300"
                }`}
              ></div>
              <span
                className={`text-sm ${
                  progress > 50 ? "text-green-600" : "text-gray-500"
                }`}
              >
                Running AI analysis
              </span>
            </div>
            <div className="flex items-center">
              <div
                className={`w-3 h-3 rounded-full mr-3 ${
                  progress > 80 ? "bg-green-500" : "bg-gray-300"
                }`}
              ></div>
              <span
                className={`text-sm ${
                  progress > 80 ? "text-green-600" : "text-gray-500"
                }`}
              >
                Generating results
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
