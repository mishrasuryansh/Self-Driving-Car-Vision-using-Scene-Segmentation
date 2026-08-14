# Self-Driving Car Vision using Scene Segmentation

[![CI Pipeline](https://github.com/mishrasuryansh/Self-Driving-Car-Vision-using-Scene-Segmentation/workflows/CI/badge.svg)](https://github.com/mishrasuryansh/Self-Driving-Car-Vision-using-Scene-Segmentation/actions)
[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![React Version](https://img.shields.io/badge/react-18.0-cyan.svg)](https://react.dev/)
[![PyTorch Version](https://img.shields.io/badge/pytorch-2.x-orange.svg)](https://pytorch.org/)

A full-stack, real-time **Deep Learning Scene Segmentation Platform** for autonomous vehicle navigation. Powered by DeepLabV3+ with ResNet-101 ASPP, FastAPI async REST backend, Celery distributed worker queue, Redis cache, MongoDB storage, and a React SPA dashboard.

---

## Key Features & Capabilities
- **DeepLabV3+ ASPP Architecture**: Multi-scale receptive fields classifying roads, vehicles, pedestrians, sky, and obstacles.
- **Synchronous & Asynchronous Pipelines**: Real-time sub-50ms image inference and background video stream processing.
- **Interactive Before/After Slider**: Overlay opacity control, side-by-side comparison, and class distribution legend.
- **Perception Analytics Dashboard**: Time-series job volume trends, mean frame latency, FPS throughput gauges, and CSV export.
- **Enterprise Security Hardening**: IP sliding window rate limiting (HTTP 429), path traversal guards (HTTP 400), user resource ownership checks (HTTP 403), and security HTTP headers.

---

## Architecture Overview
```text
  [ React 18 SPA Frontend ]
            │ (Axios JWT REST / JSON)
            ▼
  [ FastAPI Gateway Service ]
            │ ── (Redis Queue / Celery) ──► [ PyTorch Inference Worker ]
            ▼                                         │
  [ MongoDB / Redis Store ] ◄─────────────────────────┘
```

---

## Quickstart Guide with Docker Compose

### Prerequisites
- [Docker Engine](https://docs.docker.com/get-docker/) & [Docker Compose v2](https://docs.docker.com/compose/)
- Git

### 1. Clone Repository
```bash
git clone https://github.com/mishrasuryansh/Self-Driving-Car-Vision-using-Scene-Segmentation.git
cd Self-Driving-Car-Vision-using-Scene-Segmentation
```

### 2. Launch Stack
```bash
docker-compose up --build -d
```

### 3. Access Application Services
- **Frontend SPA Web UI**: `http://localhost:5173`
- **FastAPI OpenAPI Docs**: `http://localhost:8000/api/v1/docs`
- **Health Check Endpoint**: `http://localhost:8000/api/v1/health`

---

## Academic Team Credits & Supervision
- **Development Team**: Anshika Tiwari, Uday Kumar Shukla, Swastik Shukla, Suryansh Mishra, Akansha Rajpoot, Akansha Yadav
- **Supervisor**: Dr. Milli Dhar
- **Institution**: Pranveer Singh Institute of Technology (PSIT), Kanpur
