# Capstone_AI

# Freshtify — AI-Powered Stock Level Estimation System

**Freshtify** is an AI-driven system that automatically estimates supermarket shelf stock levels from images.  
It integrates a React + Tailwind frontend with a FastAPI backend and a hybrid AI pipeline (GroundingDino, SAM2, Depth-Anything-v2, and Gemini).

---

## Objectives
- Automate shelf monitoring using computer vision and AI.
- Provide real-time stock visualization and low-stock alerts.
- Store results as JSON for analytics.

---

## Key Features
- Upload shelf images and get instant AI-based stock estimation.
- Interactive dashboard showing stock trends by category and time.
- Automatic low-stock alerts (below 30% threshold).
- Real-time backend–frontend synchronization.
- Multi-model AI pipeline: detection, segmentation, depth, and refinement.

---

## Main System Architecture
- **Frontend:** React + Vite + TailwindCSS for the web dashboard.  
- **Backend:** FastAPI for API routing, AI inference, and data exchange.  
- **AI Layer:** GroundingDino (Detection), SAM2 (Segmentation), Depth-Anything-v2 (Depth Estimation), and Gemini (Refinement).  
- **Deployment:** Dockerized services running on TensorDock / AWS / GCP.  

![System Architecture Diagram](./docs/System_Flow_Chart.png)

---

### **Installation & Setup**
## Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
python start_server.py
```
- API docs can be accessed through the link: http://localhost:8000/docs
## Frontend (React)
```bash
cd frontend
npm install
npm run dev
```
- Frontend runs at http://localhost:5173

## Folder Structure
```
Freshtify/
├── backend/               # FastAPI backend
│   ├── README.md          # Backend API file structure
├── backend_model/         # AI Pipeline models
├── dataset/               # Training / testing image data
├── docs/                  # Documentation, diagrams (e.g., architecture.png)
├── front_end/             # React + Vite frontend dashboard
│   └── README.md          # Frontend file structure
├── result_images/         # Output visualization results from AI model
├── docker-compose.yml     # Multi-service deployment config
├── env_example            # Example environment variables
├── main.py                # Main AI entry point
└── README.md              # Root documentation file
```
---

## 4. **Results & Future Work**
### Results
- Reliable accuracy between AI estimation and actual shelf stock.
- Average processing time: 30–40 seconds per image for local machine and 15-20 seconds when we deploy publicly.
- Fully documented API and modular FastAPI service.

### Future Work
- Integrate cloud database (PostgreSQL / Firebase).
- Support multi-camera live tracking.
- Deploy full system on AWS / GCP.


# **Freshtify - Frontend**

A modern web application for AI-powered stock estimation and freshness analysis of produce items. Built with React Router v7, TypeScript, and TailwindCSS.

## 🚀 Features

- **Image Upload & Analysis**: Upload images for AI-powered stock estimation
- **Real-time Dashboard**: Visualize stock levels and freshness data
- **Alert System**: Monitor and manage stock alerts
- **Model Selection**: Choose between different AI models for analysis
- **Responsive Design**: Modern UI with TailwindCSS and shadcn/ui components
- **Server-side Rendering**: Fast initial page loads with React Router SSR
- **Hot Module Replacement**: Lightning-fast development experience

## 🛠 Tech Stack

- **Framework**: React Router v7
- **Language**: TypeScript
- **Styling**: TailwindCSS v4
- **UI Components**: Radix UI & shadcn/ui
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Build Tool**: Vite

## 📁 Folder Structure

```
front_end/
├── app/                          # Application source code
│   ├── routes/                   # Route components
│   │   ├── _layout.tsx          # Layout wrapper for nested routes
│   │   ├── index.tsx            # Home page
│   │   ├── upload.tsx           # Image upload page
│   │   ├── dashboard.tsx        # Dashboard with analytics
│   │   └── alert.tsx            # Alerts management page
│   │
│   ├── components/              # Reusable React components
│   │   ├── Header.tsx           # Navigation header
│   │   ├── Footer.tsx           # Footer component
│   │   ├── ModelSelector.tsx   # AI model selection component
│   │   ├── SectionToggle.tsx   # Section toggle component
│   │   ├── StatusPill.tsx       # Status indicator component
│   │   ├── TimeToggle.tsx       # Time filter toggle
│   │   └── ui/                  # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── dialog.tsx
│   │       ├── dropdown-menu.tsx
│   │       ├── input.tsx
│   │       ├── label.tsx
│   │       ├── navigation-menu.tsx
│   │       ├── select.tsx
│   │       └── table.tsx
│   │
│   ├── lib/                     # Utility libraries
│   │   ├── api.ts              # API client functions
│   │   └── utils.ts            # Helper utilities
│   │
│   ├── assets/                  # Static assets
│   │   ├── avatars/            # Team member avatars
│   │   ├── sampleImages/       # Sample images for demo
│   │   └── teamlogo.png        # Team logo
│   │
│   ├── welcome/                 # Welcome page assets
│   │   ├── welcome.tsx
│   │   ├── logo-dark.svg
│   │   └── logo-light.svg
│   │
│   ├── root.tsx                 # Root application component
│   ├── routes.ts                # Route configuration
│   └── app.css                  # Global styles
│
├── public/                      # Public static files
│   └── favicon.ico
│
├── build/                       # Production build output
│   ├── client/                 # Client-side assets
│   └── server/                 # Server-side code
│
├── components.json              # shadcn/ui configuration
├── Dockerfile                   # Docker configuration
├── env.example                  # Environment variables template
├── package.json                 # Dependencies and scripts
├── react-router.config.ts       # React Router configuration
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite configuration
└── README.md                    # This file
```

## 📦 Installation

### Prerequisites

- Node.js 18+
- npm or pnpm or yarn

### Install Dependencies

```bash
npm install
```

## 🔧 Configuration

1. Copy the environment variables template:

```bash
cp env.example .env
```

2. Update the `.env` file with your configuration:

```env
VITE_API_URL=http://localhost:8000
# Add other environment variables as needed
```

## 💻 Development

Start the development server with Hot Module Replacement:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server (on port 12355)
- `npm run typecheck` - Run TypeScript type checking

## 🏗 Building for Production

Create an optimized production build:

```bash
npm run build
```

This generates:

- `build/client/` - Static assets (HTML, CSS, JS)
- `build/server/` - Server-side code

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t freshtify-frontend .
```

### Run Container

```bash
docker run -p 3000:3000 freshtify-frontend
```

### Docker Compose

If you have a `docker-compose.yml` in the root directory:

```bash
docker-compose up frontend
```

## 🚀 Deployment Options

The application can be deployed to any platform that supports Node.js or Docker:

- **Cloud Platforms**: AWS ECS, Google Cloud Run, Azure Container Apps
- **PaaS**: Heroku, Railway, Fly.io, Render
- **Edge**: Cloudflare Pages, Vercel, Netlify
- **VPS**: Digital Ocean, Linode, Vultr

### Production Server

To run the production build locally:

```bash
npm run start
```

The server will start on port 12355 (configurable via PORT environment variable).

## 🎨 Styling

This project uses:

- **TailwindCSS v4** for utility-first styling
- **shadcn/ui** for pre-built accessible components
- **Radix UI** for unstyled, accessible component primitives
- **class-variance-authority** for component variants
- **clsx** & **tailwind-merge** for conditional class composition

### Adding New UI Components

Use the shadcn/ui CLI to add new components:

```bash
npx shadcn@latest add [component-name]
```

## 📱 Pages & Routes

- `/` - Home page with overview
- `/upload` - Upload images for analysis
- `/dashboard` - View analytics and stock data
- `/alert` - Manage alerts and notifications

## 🔌 API Integration

The frontend communicates with the backend API defined in `app/lib/api.ts`. Update the base URL in your environment variables:

```typescript
// app/lib/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

## 👥 Team

This project is built by the Chill guys team. Team member information and avatars are located in `app/assets/avatars/`.

---

Built with ❤️ using React Router v7 and modern web technologies.

# **Freshtify - Backend API**

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

# **Freshtify - AI Stock App Container Deployment Guide**

# 

## **Table of Contents**

1. [Pre-requisites](#pre-requisites)  
2. [Step 1: Install Docker](#step-1-install-docker)  
3. [Step 2: Install NVIDIA Container Toolkit](#step-2-install-nvidia-container-toolkit)  
4. [Step 3: Configure Docker for NVIDIA Runtime](#step-3-configure-docker-for-nvidia-runtime)  
5. [Step 4: Verify Installation](#step-4-verify-installation)  
6. [Step 5: Build and Run Docker Containers](#step-5-build-and-run-docker-containers)  
7. [Step 6: Set Up Domain and Nginx](#step-6-set-up-domain-and-nginx)  

***

## **Pre-requisites**

Before you start, make sure you have:

- A VPS or host running **Ubuntu 22.04** or **Debian 12**
- An **NVIDIA GPU** (for CUDA support)
- **Docker** (rootless or with root privileges)

***

## **Step 1: Install Docker**

Run the following commands to install Docker:

```
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

If you want to use Docker as a non-root user, install **rootless Docker**:

```
dockerd-rootless-setuptool.sh install
```

***

## **Step 2: Install NVIDIA Container Toolkit**

Follow the NVIDIA Container Toolkit installation guide for your system:  
https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

### Install prerequisites
```
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
   curl \
   gnupg2
```

### Configure NVIDIA repository
```
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
 && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
   sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
   sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

### Optional: Use experimental packages
```
sudo sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

### Update repository and install toolkit
```
sudo apt-get update
export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.18.0-1
sudo apt-get install -y \
    nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}
```

***

## **Step 3: Configure Docker for NVIDIA Runtime**

### Configure runtime
```
sudo nvidia-ctk runtime configure --runtime=docker
```

This updates `/etc/docker/daemon.json` to include the NVIDIA runtime.

### Restart Docker
```
sudo systemctl restart docker
```

### Rootless Docker setup
If you are using **rootless Docker**:

```
nvidia-ctk runtime configure --runtime=docker --config=$HOME/.config/docker/daemon.json
systemctl --user restart docker
sudo nvidia-ctk config --set nvidia-container-cli.no-cgroups --in-place
```

***

## **Step 4: Verify Installation**

Test if the NVIDIA runtime works correctly:

```
docker run --rm --gpus all nvidia/cuda:12.8.1-devel-ubuntu24.04 nvidia-smi
```

If successful, you’ll see your GPU details displayed.

***

## **Step 5: Build and Run Docker Containers**

### Build frontend image
From your frontend folder:
```
cd front_end
docker build -t fe:latest-sv .
```

### Build backend image
From your project root:
```
docker build -t backend:latest-sv -f backend/Dockerfile .
```

### Docker Compose configuration
Create `docker-compose.yml` at your project root:

```yaml
services:
  backend:
    image: backend:latest-sv
    container_name: ai-stock-backend
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - DEBUG=true
      - ENABLE_GPU=true
      - CUDA_VISIBLE_DEVICES=0
    env_file:
      - .env
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/outputs:/app/outputs
      - ./backend/model_cache:/app/model_cache
      - ./backend/logs:/app/logs
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - ai-stock-network

  frontend:
    image: fe:latest-sv
    container_name: ai-stock-frontend
    ports:
      - "12355:12355"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - ai-stock-network

networks:
  ai-stock-network:
    driver: bridge

volumes:
  model_cache:
    driver: local
  uploads:
    driver: local
  outputs:
    driver: local
```

### Start application
```
docker-compose up -d
```

Check container status:
```
docker ps
```

Access your app at:  
`http://<your-server-ip>:12355`

***

## **Step 6: Set Up Domain and Nginx**

### Point domain to server
Update your DNS A record to point your domain (e.g., `example.com`) to your server’s public IP.

### Install Nginx
```
sudo apt update
sudo apt install nginx
```

### Create Nginx config
```
sudo nano /etc/nginx/sites-available/your-domain.com
```

Add this configuration:

```
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://localhost:12355;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable and restart Nginx
```
sudo ln -s /etc/nginx/sites-available/your-domain.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Your application is now accessible via your domain.

***

## **Optional: SSL Setup with Cloudflare**

Use **Cloudflare** to enable free SSL:
1. Point your domain’s nameservers to Cloudflare.
2. Enable SSL in Cloudflare’s dashboard.

If you cannot open ports (no root access), use **Cloudflare Tunnel**:  
https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/get-started/create-remote-tunnel/

This method exposes your application securely to the internet.
