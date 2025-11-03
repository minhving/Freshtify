# **AI Stock App Container Deployment Guide**

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
