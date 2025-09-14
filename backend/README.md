# AI-Powered Stock Level Estimation API

A FastAPI-based backend service for automatically estimating supermarket stock levels using AI and computer vision techniques. This system supports multiple AI models including Vision-Language Models (Qwen-VL, PaliGemma, Florence-2), image segmentation (SAM), and basic computer vision approaches.

## Features

- **Multiple AI Models**: Support for various AI models including Qwen-VL, PaliGemma, Florence-2, and SAM
- **Image & Video Processing**: Handle both image and video uploads for stock estimation
- **Product Detection**: Focus on fresh produce (bananas, broccoli, avocado, tomato, onion)
- **Stock Level Classification**: Categorize stock levels as low, normal, or overstocked
- **Batch Processing**: Process multiple files simultaneously
- **RESTful API**: Clean, documented API endpoints with automatic OpenAPI documentation
- **GPU Support**: Optimized for GPU acceleration when available
- **Modular Architecture**: Extensible design for adding new AI models and features

## Project Structure

```
app/
├── api/
│   └── routes/
│       ├── health.py          # Health check endpoints
│       └── stock_estimation.py # Main stock estimation endpoints
├── core/
│   ├── config.py             # Configuration management
│   └── logging_config.py     # Logging setup
├── models/
│   └── schemas.py            # Pydantic models for API schemas
├── services/
│   ├── ai_engine.py          # AI model integration and processing
│   └── file_processor.py     # File upload and processing
├── utils/
│   └── helpers.py            # Utility functions
└── main.py                   # FastAPI application entry point
```

## Installation

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (recommended for AI models)
- 8GB+ RAM (16GB+ recommended for large models)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-stock-estimation-api
   ```

2. **Create virtual environment**:
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
   # Edit .env with your configuration
   ```

5. **Create necessary directories**:
   ```bash
   mkdir -p uploads outputs model_cache logs
   ```

## Configuration

The application uses environment variables for configuration. Copy `env.example` to `.env` and modify as needed:

### Key Configuration Options

- **API Settings**: Host, port, debug mode
- **File Upload**: Maximum file size, allowed extensions
- **AI Models**: Model paths and settings
- **Stock Thresholds**: Low/normal/overstock thresholds
- **GPU Settings**: Enable/disable GPU acceleration

### AI Model Configuration

The system supports multiple AI models:

1. **Vision-Language Models**:
   - Qwen-VL: `Qwen/Qwen-VL-Chat`
   - PaliGemma: `google/paligemma-3b-pt-448`
   - Florence-2: `microsoft/Florence-2-base`

2. **Segmentation Models**:
   - SAM: Segment Anything Model

3. **Fallback**: Basic computer vision techniques

## Usage

### Starting the Server

```bash
# Development mode
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
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

#### 3. Estimate Stock Levels
```bash
curl -X POST "http://localhost:8000/api/v1/estimate-stock" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@supermarket_shelf.jpg" \
  -F "model_type=qwen-vl" \
  -F "products=banana,broccoli" \
  -F "confidence_threshold=0.7"
```

#### 4. Batch Processing
```bash
curl -X POST "http://localhost:8000/api/v1/estimate-stock-batch" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "model_type=sam"
```

## API Endpoints

### Health Endpoints
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system information

### Stock Estimation Endpoints
- `POST /api/v1/estimate-stock` - Estimate stock levels from single file
- `POST /api/v1/estimate-stock-batch` - Batch processing for multiple files
- `GET /api/v1/models` - Get available AI models
- `GET /api/v1/products` - Get supported product types

## Response Format

### Successful Stock Estimation Response
```json
{
  "success": true,
  "message": "Stock estimation completed successfully",
  "processing_time": 2.34,
  "timestamp": "2024-01-15T10:30:00Z",
  "results": [
    {
      "product": "banana",
      "stock_percentage": 0.65,
      "stock_status": "normal",
      "confidence": 0.87,
      "reasoning": "Qwen-VL detected banana with 65% stock level"
    }
  ],
  "model_used": "qwen-vl",
  "image_metadata": {
    "height": 1080,
    "width": 1920,
    "channels": 3
  }
}
```

## Supported File Formats

### Images
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

### Videos
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)

## Supported Products

The system currently supports estimation for:
- Banana
- Broccoli
- Avocado
- Tomato
- Onion

## Stock Level Classification

- **Low Stock**: < 30% of shelf capacity
- **Normal Stock**: 30% - 90% of shelf capacity
- **Overstocked**: > 90% of shelf capacity

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/
flake8 app/
```

### Adding New AI Models

1. Add model configuration to `app/core/config.py`
2. Implement model loading in `app/services/ai_engine.py`
3. Add estimation logic for the new model
4. Update model information in `get_available_models()`

### Adding New Products

1. Add product type to `ProductType` enum in `app/models/schemas.py`
2. Update `SUPPORTED_PRODUCTS` in `app/core/config.py`
3. Update model training/prompts if needed

## Performance Considerations

- **GPU Memory**: Large models require significant GPU memory (8GB+ recommended)
- **Processing Time**: Vision-language models typically take 1-3 seconds per image
- **Batch Size**: Adjust `BATCH_SIZE` in configuration based on available resources
- **Model Caching**: Models are cached in memory after first load

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**: Reduce batch size or use CPU-only mode
2. **Model Loading Failures**: Check internet connection and model availability
3. **File Upload Errors**: Verify file format and size limits
4. **Slow Processing**: Ensure GPU is available and properly configured

### Logs

Application logs are stored in the `logs/` directory:
- `app.log` - Application logs with rotation
- Console output for development

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the AI Stock Level Estimation research project at La Trobe University.

## Contact

- **Project Owner**: Dr. Phu Lai
- **Affiliation**: Cisco-La Trobe Centre for AI and IoT
- **Email**: P.Lai@latrobe.edu.au
