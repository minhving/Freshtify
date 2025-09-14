import { Upload as UploadIcon } from "lucide-react";
import Button from "../components/ui/Button";
import { useState, useRef } from "react";
import { useNavigate } from "react-router";
import axios from "axios";

// curl -X POST "http://localhost:8000/api/v1/estimate-stock" \
//   -H "Content-Type: multipart/form-data" \
//   -F "file=@supermarket_shelf.jpg" \
//   -F "model_type=qwen-vl" \
//   -F "products=banana,broccoli" \
//   -F "confidence_threshold=0.7"

export default function Upload() {
  const navigate = useNavigate();

  const [isloading, setIsLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
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
    setIsLoading(true);
    if (files.length > 0) {
      console.log("Uploading files:", files);
      // Add upload logic here
      console.log(files);

      //post request to api
      try {
        const formData = new FormData();
        formData.append("file", files[0]); // nếu chỉ gửi 1 file, nếu nhiều file thì lặp
        formData.append("model_type", "qwen-vl");
        formData.append("products", "banana,broccoli");
        formData.append("confidence_threshold", "0.7");
        console.log(formData);
        const response = await axios.post(
          "http://localhost:8000/api/v1/estimate-stock",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        console.log("Response:", response.data); //
        // Ví dụ: navigate("/dashboard");
      } catch (error) {
        console.error("Upload failed:", error);
      } finally {
        setIsLoading(false);
      }
      // navigate("/dashboard");
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

        <Button
          variant="secondary"
          size="large"
          onClick={handleUpload}
          disabled={files.length === 0}
        >
          {isloading ? "uploading" : "upload"}
        </Button>
      </div>
    </div>
  );
}
