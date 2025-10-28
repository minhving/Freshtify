# Use NVIDIA CUDA devel image with Python
FROM nvidia/cuda:12.8.1-devel-ubuntu24.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    CUDA_VISIBLE_DEVICES=0 \
    DISPLAY=:99 \
    QT_X11_NO_MITSHM=1 \
    OPENCV_IO_ENABLE_OPENEXR=1

# Install system dependencies with Python 3.12 (Ubuntu 22.04)
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    python3-pip \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libxrender1 \
    libgomp1 \
    libgoogle-perftools4 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    ffmpeg \
    libopencv-dev \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic links for python3.12
RUN ln -sf /usr/bin/python3.12 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.12 /usr/bin/python

# Verify Python 3.12 installation
RUN python --version && python3 --version && python3.12 -m pip --version

# Set working directory
WORKDIR /app

# Create and activate virtual environment
RUN python3.12 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements files
COPY backend/requirements.txt .
COPY backend/requirements-minimal.txt .
COPY backend_model/requirements.txt ./backend_model_requirements.txt

# Upgrade pip and install Python dependencies in virtual environment
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install PyTorch with CUDA support first (CUDA 12.1 compatible)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Create modified requirements without opencv-python
RUN sed 's/opencv-python>=4.8.0/opencv-python-headless>=4.8.0/' requirements.txt > requirements_headless.txt

# Install backend requirements with headless opencv
RUN pip install --no-cache-dir -r requirements_headless.txt

# Install backend_model requirements
RUN pip install --no-cache-dir -r backend_model_requirements.txt

# Copy the application code
COPY backend/ .

# Create necessary directories
RUN mkdir -p uploads outputs model_cache logs

# Set permissions
RUN chmod -R 755 /app

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Command to run the application (using virtual environment)
CMD ["/opt/venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
