# AI-Powered Stock Level Estimation API

A FastAPI-based backend service for automatically estimating supermarket stock levels using integrated AI models. This system combines detection, segmentation, depth estimation, and Gemini refinement for accurate stock level analysis.

## Features

- **Integrated AI Pipeline**: Detection → Segmentation → Depth Estimation → Gemini Refinement
- **Multiple Image Processing**: Process multiple images with T0, T1, T2... grouping
- **Section-Based Analysis**: Detect individual sections for each product type
- **Real-Time Processing**: Fast processing with detailed logging
- **RESTful API**: Clean, documented API endpoints with automatic OpenAPI documentation
- **Frontend Integration**: Seamless integration with React frontend
- **GPU Support**: Optimized for GPU acceleration when available
- **Modular Architecture**: Extensible design for adding new features

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── health.py          # Health check endpoints
│   │       └── stock_estimation.py # Main stock estimation endpoints
│   ├── core/
│   │   ├── config.py             # Configuration management
│   │   └── logging_config.py     # Logging setup
│   ├── models/
│   │   └── schemas.py            # Pydantic models for API schemas
│   ├── services/
│   │   ├── ai_engine.py          # AI model integration
│   │   └── file_processor.py     # File upload and processing
│   ├── utils/
│   │   └── helpers.py            # Utility functions
│   └── main.py                   # FastAPI application entry point
├── logs/                          # Application logs
├── model_cache/                   # AI model cache directory
├── outputs/                       # Output files
├── uploads/                       # Uploaded files
└── requirements.txt               # Python dependencies
```

## Installation

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (recommended for AI models)
- 8GB+ RAM (16GB+ recommended)
- Backend model files in `backend_model/` folder

### Setup

1. **Navigate to backend folder**:
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration if needed
   ```

5. **Create necessary directories** (if not exist):
   ```bash
   mkdir -p uploads outputs model_cache logs
   ```

6. **Set up API keys** (for Gemini model):
   ```bash
   # Edit backend_model/.env
   GEMINI_API_KEY=your_api_key_here
   ```

## Configuration

### Key Settings

- **PORT**: 8000 (default)
- **HOST**: 0.0.0.0 (accessible from all interfaces)
- **Allowed Origins**: 
  - http://localhost:3000
  - http://localhost:5173
  - http://localhost:8000

### Environment Variables

Copy `env.example` to `.env` and modify as needed. Default settings are:
- Port: 8000
- Debug mode: enabled
- File size limit: 50MB

## Usage

### Starting the Server

#### Option 1: Using start_server.py (Recommended)
```bash
python start_server.py
```

#### Option 2: Using uvicorn directly
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option 3: Simple server (bypasses .env issues)
```bash
python start_simple.py
```

### API Documentation

Once the server is running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example API Calls

#### 1. Health Check
```bash
curl http://localhost:8000/api/v1/health
```

#### 2. Get Available Models
```bash
curl http://localhost:8000/api/v1/models
```

#### 3. Get Supported Products
```bash
curl http://localhost:8000/api/v1/products
```

#### 4. Estimate Stock Levels (Single Image)
```bash
curl -X POST "http://localhost:8000/api/v1/estimate-stock-integrated" \
  -F "file=@supermarket_shelf.jpg" \
  -F "products=potato section,onion,eggplant section,tomato,cucumber" \
  -F "confidence_threshold=0.7"
```

#### 5. Estimate Stock Levels (Multiple Images)
```bash
curl -X POST "http://localhost:8000/api/v1/estimate-stock-multiple" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "products=potato section,onion,eggplant section,tomato,cucumber" \
  -F "confidence_threshold=0.7"
```

## API Endpoints

### Health Endpoints
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system information

### Stock Estimation Endpoints
- `POST /api/v1/estimate-stock` - Estimate stock levels from single file (legacy)
- `POST /api/v1/estimate-stock-integrated` - **Recommended** for single image with integrated AI pipeline
- `POST /api/v1/estimate-stock-multiple` - **Recommended** for multiple images with T0, T1 grouping
- `GET /api/v1/models` - Get available AI models
- `GET /api/v1/products` - Get supported product types

## Supported Products

The system currently supports estimation for:
- **Potato Section**: Potato display sections
- **Onion**: Individual onions
- **Eggplant Section**: Eggplant display sections
- **Tomato**: Individual tomatoes
- **Cucumber**: Individual cucumbers

## Stock Level Classification

- **Low Stock**: < 30% of shelf capacity (Low)
- **Normal Stock**: 30% - 80% of shelf capacity (Medium)
- **Overstocked**: > 80% of shelf capacity (High)

## Response Format

### Single Image Response
```json
{
  "success": true,
  "message": "Stock estimation completed successfully",
  "processing_time": 2.34,
  "timestamp": "2024-01-15T10:30:00Z",
  "results": [
    {
      "product": "potato section section 1",
      "stock_percentage": 0.65,
      "stock_status": "normal",
      "confidence": 0.87,
      "bounding_box": null,
      "reasoning": "AI model detected potato section section 1 with 65% stock level"
    }
  ],
  "model_used": "integrated-ai-pipeline",
  "image_metadata": {
    "filename": "supermarket_shelf.jpg"
  }
}
```

### Multiple Images Response
```json
{
  "success": true,
  "message": "Stock estimation completed successfully for 2 images",
  "processing_time": 4.56,
  "timestamp": "2024-01-15T10:30:00Z",
  "results": {
    "T0": [
      {
        "product": "potato section section 1",
        "stock_percentage": 0.65,
        "stock_status": "normal",
        "confidence": 0.87,
        "bounding_box": null,
        "reasoning": "AI model detected potato section section 1 with 65% stock level"
      }
    ],
    "T1": [
      {
        "product": "onion section 1",
        "stock_percentage": 0.45,
        "stock_status": "normal",
        "confidence": 0.82,
        "bounding_box": null,
        "reasoning": "AI model detected onion section 1 with 45% stock level"
      }
    ]
  },
  "model_used": "integrated-ai-multiple",
  "image_metadata": {
    "image_count": 2,
    "images_processed": ["T0", "T1"]
  }
}
```

## How It Works

### AI Pipeline

1. **Detection**: Object detection using YOLO
2. **Segmentation**: Segment detection using SAM2
3. **Depth Estimation**: Calculate depth for fullness estimation
4. **Stock Calculation**: Compute stock percentage for each section
5. **Gemini Refinement** (optional): Refine results using Gemini model

### Main.py Integration

The backend runs `main.py` directly without modification:
1. User uploads images (T0.jpg, T1.jpg, etc.)
2. Backend calls `main.py` via subprocess
3. `main.py` processes images using integrated AI pipeline
4. Backend parses output using regex pattern matching
5. Results are grouped by T0, T1, T2...

### Output Format

The `print_result()` method outputs:
```
potato section - section 1: 85.2%
potato section - section 2: 72.5%
onion - section 1: 45.8%
```

This output is parsed and grouped by image for frontend display.

## Frontend Integration

The backend is designed to work seamlessly with the React frontend:

1. **Upload Images**: Frontend sends images to `/estimate-stock-multiple`
2. **Backend Processing**: Main.py processes images with AI pipeline
3. **Results Grouping**: Results are grouped by T0, T1, T2...
4. **Frontend Display**: Frontend displays results in timeline view

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Change PORT in .env or use a different port
   python -m uvicorn app.main:app --reload --port 8001
   ```

2. **Module Not Found**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **CUDA Out of Memory**
   - Reduce batch size in configuration
   - Use CPU-only mode

4. **Gemini API Key Missing**
   - Add `GEMINI_API_KEY` to `backend_model/.env`
   - System will gracefully fallback without Gemini refinement

### Logs

Application logs are stored in the `logs/` directory:
- `app.log` - Application logs with rotation
- Console output for development

## Performance

- **Processing Time**: 
  - Single image: ~1-2 minutes
  - Multiple images (2): ~2-3 minutes
- **Model Loading**: Models are cached after first load
- **Memory Usage**: ~4-8GB depending on models

## Development

### Running Tests
```bash
python test_api.py
```

### Code Formatting
```bash
black app/
flake8 app/
```

## License

This project is part of the Freshtify Stock Level Estimation system.

## Quick Start

```bash
# 1. Navigate to backend folder
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
python start_server.py

# 4. Open browser
# http://localhost:8000/docs
```

## API Version

- **Current Version**: v1
- **Base Path**: `/api/v1`
- **Supported Formats**: JSON, Multipart Form Data
