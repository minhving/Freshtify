# Capstone_AI

# Freshtify — AI-Powered Stock Level Estimation System

**Freshtify** is an AI-driven system that automatically estimates supermarket shelf stock levels from images.  
It integrates a React + Tailwind frontend with a FastAPI backend and a hybrid AI pipeline (GroundingDino, SAM2, Depth-Anything-v2, and Gemini).

---

## 🎯 Objectives
- Automate shelf monitoring using computer vision and AI.
- Provide real-time stock visualization and low-stock alerts.
- Store results as JSON for analytics.

---

## ✨ Key Features
- Upload shelf images and get instant AI-based stock estimation.
- Interactive dashboard showing stock trends by category and time.
- Automatic low-stock alerts (below 30% threshold).
- Real-time backend–frontend synchronization.
- Multi-model AI pipeline: detection, segmentation, depth, and refinement.

---

## 🏗️ Main System Architecture
- **Frontend:** React + Vite + TailwindCSS for the web dashboard.  
- **Backend:** FastAPI for API routing, AI inference, and data exchange.  
- **AI Layer:** GroundingDino (Detection), SAM2 (Segmentation), Depth-Anything-v2 (Depth Estimation), and Gemini (Refinement).  
- **Deployment:** Dockerized services running on TensorDock / AWS / GCP.  

![System Architecture Diagram](./docs/architecture.png)

---

### **Installation & Setup**
## Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate
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

Freshtify/
├── backend/               # FastAPI backend
│   ├── README.md
├── backend_model/         # AI Pipeline models
├── dataset/               # Training / testing image data
├── docs/                  # Documentation, diagrams (e.g., architecture.png)
├── front_end/             # React + Vite frontend dashboard
│   └── README.md
├── result_images/         # Output visualization results from AI model
├── docker-compose.yml     # Multi-service deployment config
├── env_example            # Example environment variables
├── main.py                # Main AI entry point
└── README.md              # Root documentation file

---

### 4. **Results & Future Work**
```markdown
## Results
- Reliable accuracy between AI estimation and actual shelf stock.
- Average processing time: 30–40 seconds per image for local machine and 15-20 seconds when we deploy publicly.
- Fully documented API and modular FastAPI service.

## Future Work
- Integrate cloud database (PostgreSQL / Firebase).
- Support multi-camera live tracking.
- Deploy full system on AWS / GCP.
