# Presentation Slide Deck Outline (12 Slides) - T110

## Slide 1: Title & Team
- **Title**: Self-Driving Car Vision using Scene Segmentation
- **Sub-Title**: Real-Time DeepLabV3+ Semantic Scene Classification Platform
- **Team**: Anshika Tiwari, Uday Kumar Shukla, Swastik Shukla, Suryansh Mishra, Akansha Rajpoot, Akansha Yadav
- **Supervisor**: Dr. Milli Dhar | PSIT Kanpur

## Slide 2: Problem Statement
- Autonomous driving requires high-precision real-time environmental perception.
- Traditional object detection bounds boxes but fails to outline complex road boundaries, drivable lanes, and background context.

## Slide 3: Proposed Solution Overview
- Full-stack semantic scene segmentation web platform.
- Classifies every pixel into canonical environmental categories (road, vehicle, sky, pedestrian, vegetation).

## Slide 4: Deep Learning Model Architecture
- **DeepLabV3+ Architecture**: ResNet-101 backbone.
- **Atrous Spatial Pyramid Pooling (ASPP)**: Captures multi-scale receptive fields.

## Slide 5: System Architecture & Stack
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Backend API**: FastAPI, JWT Authentication, Pydantic v2
- **Worker Queue**: Celery Distributed Task Queue, Redis Broker & Cache
- **Database**: MongoDB 7.0 Document Database

## Slide 6: Real-Time Image Segmentation UI
- Interactive before/after overlay slider with opacity controls.
- Side-by-side comparison mode and per-class distribution legend.

## Slide 7: Asynchronous Video Stream Processing UI
- HTML5 video playback with interactive status stepper (`Queued` -> `Processing` -> `Completed`).
- Aggregate throughput FPS and frame latency performance panel.

## Slide 8: Perception Analytics & CSV Export
- Time-series job volume trends, mean frame latency indicators.
- One-click CSV export of summary analytics.

## Slide 9: System Security & Hardening (EP10)
- IP sliding window rate limiting (HTTP 429).
- Path traversal filename sanitization (HTTP 400).
- User resource ownership authorization checks (HTTP 403).

## Slide 10: Quantitative Performance Metrics
- **Mean IoU**: 84.5%
- **Pixel Accuracy**: 94.2%
- **Frame Latency**: 42.1 ms
- **Throughput**: >30 FPS

## Slide 11: Deployment & Containerization (EP11)
- Docker & Docker Compose container orchestration.
- Verified staging health check scripts.

## Slide 12: Conclusion & Q&A
- Full 112-task roadmap completed and verified.
- Open floor for Questions & Answers.
