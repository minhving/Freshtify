# Captone_AI

# Freshtify — AI-Powered Stock Level Estimation System

**Freshtify** is an AI-driven system that automatically estimates supermarket shelf stock levels from images.  
It integrates a React + Tailwind frontend with a FastAPI backend and a hybrid AI pipeline (GroundingDino, SAM2, Depth-Anything-v2, and Gemini).

## Objectives
- Automate shelf monitoring using computer vision and AI.
- Provide real-time stock visualization and low-stock alerts.
- Store results as JSON for analytics.

## Main System Architecture
- **Frontend:** React + Vite + TailwindCSS for the web dashboard.
- **Backend:** FastAPI for API routing, AI inference, and data exchange.
- **AI Layer:** GroundingDino (Detection), SAM2 (Segmentation), Depth-Anything-v2 (Depth Estimation), and Gemini (Refinement).
- **Deployment:** Dockerized services running on TensorDock / AWS / GCP.
