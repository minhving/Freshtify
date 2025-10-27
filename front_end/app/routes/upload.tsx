import { Upload as UploadIcon, X, Image as ImageIcon } from "lucide-react";
import Button from "../components/ui/buttonCustom";
import { useState, useRef } from "react";
import Dropzone from "../components/ui/Dropzone";
import { useNavigate } from "react-router";
import axios from "axios";
import AnalyzingOverlay from "~/components/ui/AnalyzingOverlay";
import { API_ENDPOINTS, API_CONFIG } from "../lib/api";
import sample1 from "../assets/sampleImages/sample1.jpg";
import sample2 from "../assets/sampleImages/sample2.jpg";
import sample3 from "../assets/sampleImages/sample3.jpg";

export default function Upload() {
  const navigate = useNavigate();

  const [isloading, setIsLoading] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  const [progress, setProgress] = useState(0); // tracking progress percentage
  const [showAnalyzing, setShowAnalyzing] = useState(false); // show analyzing overlay
  const [error, setError] = useState<string | null>(null); // error state
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Sample images data
  const sampleImages = [
    {
      id: 1,
      src: sample1,
      alt: "Sample camera image 1",
      title: "Sample 1",
    },
    {
      id: 2,
      src: sample2,
      alt: "Sample camera image 2",
      title: "Sample 2",
    },
    {
      id: 3,
      src: sample3,
      alt: "Sample camera image 3",
      title: "Sample 3",
    },
  ];

  const handleIncomingFiles = (incoming: File[]) => {
    setFiles((prevFiles) => {
      const newFiles = [...prevFiles, ...incoming];
      createPreviewUrls(newFiles);
      return newFiles;
    });
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    // Append new files to existing files instead of replacing
    setFiles((prevFiles) => {
      const newFiles = [...prevFiles, ...selectedFiles];
      // Create preview URLs for all files (old + new)
      createPreviewUrls(newFiles);
      return newFiles;
    });
    // Reset the input so the same files can be selected again
    e.target.value = "";
  };

  const createPreviewUrls = (fileList: File[]) => {
    // Clean up old URLs to prevent memory leaks
    previewUrls.forEach((url) => URL.revokeObjectURL(url));

    const urls = fileList.map((file) => URL.createObjectURL(file));
    setPreviewUrls(urls);
  };

  const handleBrowseClick = () => fileInputRef.current?.click();

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index);
    const newUrls = previewUrls.filter((_, i) => i !== index);

    // Clean up the removed URL
    URL.revokeObjectURL(previewUrls[index]);

    setFiles(newFiles);
    setPreviewUrls(newUrls);
  };

  const handleUpload = async () => {
    console.log("handleupload");
    console.log("Uploading files:", files);
    if (files.length > 0) {
      setIsLoading(true);
      setShowAnalyzing(true);
      setProgress(0);
      setError(null);

      try {
        const formData = new FormData();
        // Always use the multiple endpoint (even for a single image)
        files.forEach((file) => {
          formData.append("files", file);
        });
        formData.append(
          "products",
          "potato section,onion,eggplant section,tomato,cucumber"
        );
        formData.append("confidence_threshold", "0.7");

        console.log(
          `Uploading ${files.length} image(s) to multiple AI endpoint...`
        );

        // Simulate progress updates
        const step = files.length > 1 ? 5 : 10;
        const intervalMs = files.length > 1 ? 3000 : 2000;
        const progressInterval = setInterval(() => {
          setProgress((prev) => Math.min(prev + step, 90));
        }, intervalMs);

        const response = await axios.post(
          API_ENDPOINTS.ESTIMATE_STOCK_MULTIPLE,
          formData,
          {
            headers: API_CONFIG.HEADERS,
            timeout:
              files.length > 1 ? API_CONFIG.TIMEOUT * 2 : API_CONFIG.TIMEOUT,
          }
        );

        clearInterval(progressInterval);
        setProgress(100);

        console.log("AI Analysis Response:", response.data);

        // Store the analysis results in localStorage for the dashboard
        localStorage.setItem("latestAnalysis", JSON.stringify(response.data));

        // Navigate to dashboard
        navigate("/dashboard");
      } catch (error: any) {
        console.error("Upload failed:", error);

        if (error.code === "ECONNABORTED") {
          setError(
            "AI analysis is taking longer than expected. Please try again with a smaller image or wait a bit longer."
          );
        } else if (error.response?.status === 500) {
          setError("Server error during analysis. Please try again.");
        } else {
          setError("Upload failed. Please try again.");
        }
      } finally {
        setIsLoading(false);
        setShowAnalyzing(false);
        setProgress(0);
      }
    }
  };

  return (
    <div className="flex items-center justify-center px-4 sm:px-10 py-10">
      <div className="w-full max-w-6xl">
        {/* Page Title */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Upload Images
          </h1>
          <p className="text-lg text-gray-600">
            Drag and drop image/video here or browse files to upload. Supported
            format: JPG, PNG.
          </p>
        </div>

        {/* Main Upload Card */}
        <div className="bg-gray-800 rounded-3xl p-8 shadow-2xl">
          {/* Upload Area */}
          <Dropzone
            onFiles={handleIncomingFiles}
            accept="image/*,.jpg,.jpeg,.png"
            multiple
            className="border-4 border-dashed border-gray-400 rounded-2xl p-12 text-center transition-all duration-300 hover:border-gray-300 hover:bg-gray-700/50"
          >
            {({ isDragging, openFileDialog }) => (
              <div>
                <UploadIcon className="w-16 h-16 mx-auto mb-6 text-gray-400" />
                <h2 className="text-2xl font-semibold text-white mb-4">
                  {isDragging
                    ? "Drop files here"
                    : "Drag and drop image/video here"}
                </h2>
                <p className="text-gray-400 mb-6">or</p>
                <Button
                  onClick={openFileDialog}
                  variant="secondary"
                  size="large"
                >
                  Browse files
                </Button>
              </div>
            )}
          </Dropzone>

          {/* Hidden file input for external browse triggers (optional) */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,.jpg,.jpeg,.png"
            onChange={handleFileInput}
            className="hidden"
          />

          {/* Sample Images Section */}
          <div className="mt-8">
            <h3 className="text-xl font-semibold text-white mb-6 text-center">
              Sample Images
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {sampleImages.map((image) => (
                <div
                  key={image.id}
                  className="bg-gray-700 rounded-xl overflow-hidden shadow-lg"
                >
                  <img
                    src={image.src}
                    alt={image.alt}
                    className="w-full h-48 object-cover"
                  />
                  <div className="p-4">
                    <h4 className="text-white font-medium">{image.title}</h4>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Uploaded Files Preview */}
          {files.length > 0 && (
            <div className="mt-8">
              <h3 className="text-xl font-semibold text-white mb-4">
                Selected Files ({files.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {files.map((file, index) => {
                  return (
                    <div
                      key={index}
                      className="bg-gray-700 rounded-xl overflow-hidden shadow-lg relative"
                    >
                      {previewUrls[index] ? (
                        <img
                          src={previewUrls[index]}
                          alt={file.name}
                          className="w-full h-48 object-cover"
                        />
                      ) : (
                        <div className="w-full h-48 bg-gray-600 flex items-center justify-center">
                          <ImageIcon className="w-12 h-12 text-gray-400" />
                        </div>
                      )}
                      <div className="p-4">
                        <h4 className="text-white font-medium truncate">
                          {file.name}
                        </h4>
                        <p className="text-gray-400 text-sm">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      <button
                        onClick={() => removeFile(index)}
                        className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-1 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
              <p className="text-red-400 text-center">{error}</p>
            </div>
          )}

          {/* Analyze Button */}
          <div className="mt-8 text-center">
            <Button
              variant="secondary"
              size="large"
              onClick={handleUpload}
              disabled={files.length === 0 || isloading}
              className="px-12 py-4 text-lg font-semibold"
            >
              {isloading ? "Analyzing..." : "Analyse"}
            </Button>
          </div>
        </div>

        {/* Analyzing/Loading Overlay */}
        <AnalyzingOverlay
          isVisible={showAnalyzing}
          progress={progress}
          fileCount={files.length}
        />
      </div>
    </div>
  );
}
