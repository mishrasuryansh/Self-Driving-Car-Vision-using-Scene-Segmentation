# Self-Driving Car Vision using Cityscapes Scene Segmentation

[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![React Version](https://img.shields.io/badge/react-19.1-cyan.svg)](https://react.dev/)
[![PyTorch Version](https://img.shields.io/badge/pytorch-2.x-orange.svg)](https://pytorch.org/)
[![Cityscapes Model](https://img.shields.io/badge/model-SegFormer--B0--Cityscapes-green.svg)](https://huggingface.co/nvidia/segformer-b0-finetuned-cityscapes-512-1024)

A full-stack, real-time **Autonomous Driving Semantic Scene Segmentation Platform** for urban vehicle navigation. Powered by PyTorch & SegFormer B0 trained on Cityscapes 19 urban road classes, a FastAPI async REST backend, JWT authentication, and a React 19 SPA dashboard with Three.js 3D perception visualizations.

---

## 🚘 Real Machine Learning Model & Taxonomy

- **Model Architecture**: SegFormer B0 (`nvidia/segformer-b0-finetuned-cityscapes-512-1024`).
- **Pretrained Weights**: Hugging Face Hub official repository (cached locally in `~/.cache/huggingface/hub`).
- **Dataset**: Cityscapes 19 urban road-scene semantic classes:
  1. `road`
  2. `sidewalk`
  3. `building`
  4. `wall`
  5. `fence`
  6. `pole`
  7. `traffic light`
  8. `traffic sign`
  9. `vegetation`
  10. `terrain`
  11. `sky`
  12. `person`
  13. `rider`
  14. `car`
  15. `truck`
  16. `bus`
  17. `train`
  18. `motorcycle`
  19. `bicycle`
- **Execution**: Hardware portable (sub-100ms CPU execution).
- **No Synthetic Fallbacks**: Production pipeline executes real model inference on every uploaded frame, generating true alpha-blended color overlays and exact pixel percentage class distributions.

---

## 🏗 System Architecture Overview

```text
  ┌─────────────────────────────────────────────────────────────┐
  │                   React 19 SPA Frontend                      │
  │     (Three.js 3D Vehicle HUD / Before-After Overlay Slider)  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ HTTP REST API (JWT Bearer)
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                 FastAPI REST API Gateway                    │
  │        (/api/v1/auth, /api/v1/media, /api/v1/inference)   │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │            PyTorch / SegFormer Inference Engine             │
  │       (Cityscapes 19-Class Argmax & Alpha Overlay Blend)     │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │               Disk Storage & Output Serving                 │
  │       (storage/uploads/ & storage/outputs/ /storage/...)    │
  └─────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quickstart & Local Development

### 1. Backend Server Startup
From the repository root directory:
```bash
./.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```
- API Base URL: `http://127.0.0.1:8000/api/v1`
- Swagger Docs: `http://127.0.0.1:8000/api/v1/docs`

### 2. Frontend Development Server Startup
In a separate terminal window:
```bash
cd frontend
npm install
npm run dev
```
- Frontend Web App: `http://localhost:5173`

### 3. Automated End-to-End Test Verification
Run the comprehensive E2E automated test verifying registration, login, JWT auth, image upload, real SegFormer model inference, output image decoding, and class percentage calculation:
```bash
./.venv/Scripts/python.exe scripts/test_e2e_real_pipeline.py
```

---

## 🔑 Key API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new driver/developer account |
| `POST` | `/api/v1/auth/login` | Authenticate user and issue JWT bearer token |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile details |
| `POST` | `/api/v1/media/upload` | Upload raw road scene image/video file |
| `POST` | `/api/v1/inference/segment` | Trigger Cityscapes semantic scene segmentation |
| `GET` | `/api/v1/inference/tasks/{id}` | Query task status, output file path & metrics |
| `GET` | `/storage/outputs/{filename}` | Serve static colorized output overlay images |

---

## 🎓 Academic Team Credits & Supervision
- **Development Team**: Anshika Tiwari, Uday Kumar Shukla, Swastik Shukla, Suryansh Mishra, Akansha Rajpoot, Akansha Yadav
- **Supervisor**: Dr. Milli Dhar
- **Institution**: Pranveer Singh Institute of Technology (PSIT), Kanpur
