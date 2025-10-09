import { Upload as UploadIcon } from "lucide-react";
import Button from "../components/ui/Button";
import { useState, useRef } from "react";
import { useNavigate } from "react-router";
import axios from "axios";
import { API_ENDPOINTS, API_CONFIG } from "../lib/api";

export default function Upload() {
  const navigate = useNavigate();

  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles(droppedFiles);
  };

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    setFiles(selectedFiles);
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = async () => {
    if (files.length > 0) {
      setIsLoading(true);
      setError(null);
      
      try {
        const formData = new FormData();
        formData.append("file", files[0]);
        formData.append("products", "banana,broccoli,avocado,tomato,onion");
        formData.append("confidence_threshold", "0.7");

        console.log("Uploading to integrated AI endpoint...");
        const response = await axios.post(
          API_ENDPOINTS.ESTIMATE_STOCK_INTEGRATED,
          formData,
          {
            headers: API_CONFIG.HEADERS,
            timeout: API_CONFIG.TIMEOUT,
          }
        );
        
        console.log("AI Analysis Response:", response.data);
        
        // Store the analysis results in localStorage for the dashboard
        localStorage.setItem('latestAnalysis', JSON.stringify(response.data));
        
        navigate("/dashboard");
      } catch (error) {
        console.error("Upload failed:", error);
        setError("Upload failed. Please try again.");
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="flex items-center justify-center px-4 sm:px-10 py-10">
      <div className="flex flex-col items-center justify-center bg-primary rounded-4xl p-6 sm:p-10 border-5 border-indigo-400 shadow-2xl w-full max-w-4xl">
        <h1 className="text-2xl sm:text-4xl font-bold mb-4 text-center">
          Upload Shelf Images
        </h1>
        <p className="text-lg sm:text-xl font-regular mb-6 text-center px-4">
          Drag and drop image/video here or browse files to upload. Supported
          format: JPG, PNG.
        </p>
        {/* drag and drop area */}
        <div
          className={`flex flex-col items-center justify-center border-4 border-dashed border-secondary rounded-4xl p-8 sm:p-16 mb-6 w-full min-h-[300px] sm:min-h-[400px] transition-colors ${
            isDragging
              ? "bg-secondary/20 border-secondary/80"
              : "hover:bg-secondary/10"
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
        >
          <UploadIcon className="w-12 h-12 sm:w-16 sm:h-16 mb-4 text-secondary" />
          <h2 className="text-lg sm:text-2xl font-semibold mb-2 text-center">
            {isDragging ? "Drop files here" : "Drag and drop image/video here"}
          </h2>
          <p className="text-sm sm:text-base mb-4 text-secondary">or</p>
          <Button onClick={handleBrowseClick} variant="secondary" size="large">
            Browse files
          </Button>
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,.jpg,.jpeg,.png"
          onChange={handleFileInput}
          className="hidden"
        />

        {/* File list */}
        {files.length > 0 && (
          <div className="w-full mb-6">
            <h3 className="text-lg font-semibold mb-3">Selected Files:</h3>
            <div className="space-y-2">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between bg-secondary/10 rounded-lg p-3"
                >
                  <span className="text-sm">{file.name}</span>
                  <span className="text-xs text-secondary">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

         {/* Error Display */}
         {error && (
           <div className="w-full mb-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
             <p className="text-red-400 text-center">{error}</p>
           </div>
         )}

         <Button
           variant="secondary"
           size="large"
           onClick={handleUpload}
           disabled={files.length === 0 || isLoading}
         >
           {isLoading ? "Analyzing with AI..." : `Upload ${files.length > 0 ? `(${files.length} files)` : ""}`}
         </Button>
      </div>
    </div>
  );
}
