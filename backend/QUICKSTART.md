# Quick Start Guide

## 🚀 Getting Started with AI Stock Level Estimation API

### Prerequisites
- Python 3.8 or higher
- 8GB+ RAM (16GB+ recommended for AI models)
- CUDA-compatible GPU (optional but recommended)

### 1. Install Dependencies

#### Option A: Automated Installation (Recommended)
```bash
# Run the automated installer
python install_dependencies.py
```

#### Option B: Manual Installation
```bash
# Install core dependencies first
pip install -r requirements-minimal.txt

# Then install full requirements
pip install -r requirements.txt
```

#### Option C: Step-by-step Installation
```bash
# Install core API dependencies
pip install fastapi uvicorn python-multipart pydantic python-dotenv

# Install AI/ML dependencies
pip install torch torchvision transformers opencv-python Pillow numpy

# Install additional utilities
pip install httpx aiofiles loguru psutil
```

**Note**: PyTorch and other AI/ML libraries are large and may take several minutes to install.

### 2. Configure Environment (Optional)

```bash
# Copy example configuration
cp env.example .env

# Edit .env file with your settings (optional)
# The default settings will work for basic testing
```

### 3. Start the Server

#### Option A: Using the startup script (Recommended)
```bash
python start_server.py
```

#### Option B: Direct command
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option C: Using the run script
```bash
python run.py
```

### 4. Access the API

Once the server is running, you can access:

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

### 5. Test the API

#### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

#### Get Available Models
```bash
curl http://localhost:8000/api/v1/models
```

#### Estimate Stock Levels (Example)
```bash
curl -X POST "http://localhost:8000/api/v1/estimate-stock" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_image.jpg" \
  -F "model_type=basic-cv" \
  -F "products=banana,broccoli"
```

### 6. Using the Interactive Documentation

1. Open http://localhost:8000/docs in your browser
2. Click on any endpoint to expand it
3. Click "Try it out" to test the API
4. Upload an image and see the results

## 🔧 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# If you get import errors, reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**2. CUDA/GPU Issues**
```bash
# Check if CUDA is available
python -c "import torch; print(torch.cuda.is_available())"

# If CUDA is not available, the system will use CPU (slower but functional)
```

**3. Port Already in Use**
```bash
# Change the port in .env file or use a different port
python -m uvicorn app.main:app --reload --port 8000
```

**4. Memory Issues**
- Reduce batch size in configuration
- Use smaller models
- Close other applications

### File Upload Limits

- **Maximum file size**: 50MB
- **Supported formats**: JPG, PNG, MP4, AVI, MOV
- **Recommended image size**: 1920x1080 or smaller

## 📊 Supported Products

The system can estimate stock levels for:
- 🍌 Banana
- 🥦 Broccoli  
- 🥑 Avocado
- 🍅 Tomato
- 🧅 Onion

## 🤖 Available AI Models

1. **qwen-vl** - Vision-Language Model (requires GPU)
2. **paligemma** - Google's PaliGemma (requires GPU)
3. **florence** - Microsoft Florence-2 (requires GPU)
4. **sam** - Segment Anything Model (requires GPU)
5. **basic-cv** - Basic Computer Vision (CPU only)

## 📈 Stock Level Classification

- **Low Stock**: < 30% of shelf capacity
- **Normal Stock**: 30% - 90% of shelf capacity  
- **Overstocked**: > 90% of shelf capacity

## 🎯 Next Steps

1. **Test with your own images**: Upload supermarket shelf photos
2. **Try different models**: Compare results across AI models
3. **Batch processing**: Upload multiple images at once
4. **Integration**: Connect to your frontend application

## 📞 Support

If you encounter issues:
1. Check the logs in the `logs/` directory
2. Verify all dependencies are installed
3. Ensure you have sufficient system resources
4. Contact: P.Lai@latrobe.edu.au

---

**Happy coding! 🚀**
