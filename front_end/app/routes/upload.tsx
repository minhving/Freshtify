import { Upload as UploadIcon, X, Image as ImageIcon } from "lucide-react";
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
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Sample images data
  const sampleImages = [
    {
      id: 1,
      src: "https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&h=200&fit=crop&crop=center",
      alt: "Broccoli on supermarket shelf",
      title: "Broccoli Shelf",
    },
    {
      id: 2,
      src: "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=300&h=200&fit=crop&crop=center",
      alt: "Bananas on supermarket shelf",
      title: "Banana Display",
    },
    {
      id: 3,
      src: "https://images.unsplash.com/photo-1567306301408-9b74779a11af?w=300&h=200&fit=crop&crop=center",
      alt: "Tomatoes on supermarket shelf",
      title: "Tomato Section",
    },
  ];

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    // Append dropped files to existing files instead of replacing
    setFiles((prevFiles) => {
      const newFiles = [...prevFiles, ...droppedFiles];
      // Create preview URLs for all files (old + new)
      createPreviewUrls(newFiles);
      return newFiles;
    });
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

  const handleBrowseClick = () => {
    // Trigger the hidden file input when browse button is clicked
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index);
    const newUrls = previewUrls.filter((_, i) => i !== index);

    // Clean up the removed URL
    URL.revokeObjectURL(previewUrls[index]);

    setFiles(newFiles);
    setPreviewUrls(newUrls);
  };

  const handleUpload = async () => {
    setIsLoading(true);
    if (files.length > 0) {
      try {
        const formData = new FormData();

        // Append all files to FormData
        files.forEach((file) => {
          formData.append("files", file);
        });

        formData.append("model_type", "qwen-vl");
        formData.append("products", "banana,broccoli");
        formData.append("confidence_threshold", "0.7");

        // Use batch endpoint for multiple files
        const response = await axios.post(
          "http://localhost:8000/api/v1/estimate-stock-batch",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        console.log("Response:", response.data);
        navigate("/dashboard");
      } catch (error) {
        console.error("Upload failed:", error);
        // Fallback to single file upload if batch fails
        if (files.length === 1) {
          try {
            const singleFormData = new FormData();
            singleFormData.append("file", files[0]);
            singleFormData.append("model_type", "qwen-vl");
            singleFormData.append("products", "banana,broccoli");
            singleFormData.append("confidence_threshold", "0.7");

            const singleResponse = await axios.post(
              "http://localhost:8000/api/v1/estimate-stock",
              singleFormData,
              {
                headers: {
                  "Content-Type": "multipart/form-data",
                },
              }
            );
            console.log("Single file response:", singleResponse.data);
            navigate("/dashboard");
          } catch (singleError) {
            console.error("Single file upload also failed:", singleError);
          }
        }
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center px-4 py-10">
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
          <div
            className={`border-4 border-dashed border-gray-400 rounded-2xl p-12 text-center transition-all duration-300 ${
              isDragging
                ? "border-blue-400 bg-blue-50/10"
                : "hover:border-gray-300 hover:bg-gray-700/50"
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
          >
            <UploadIcon className="w-16 h-16 mx-auto mb-6 text-gray-400" />
            <h2 className="text-2xl font-semibold text-white mb-4">
              {isDragging
                ? "Drop files here"
                : "Drag and drop image/video here"}
            </h2>
            <p className="text-gray-400 mb-6">or</p>
            <Button
              onClick={handleBrowseClick}
              variant="secondary"
              size="large"
            >
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
                  console.log(
                    `Rendering file ${index}:`,
                    file.name,
                    "Preview URL:",
                    previewUrls[index] ? "exists" : "missing"
                  );
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
      </div>
    </div>
  );
}
