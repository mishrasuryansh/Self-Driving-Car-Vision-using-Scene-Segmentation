# Load Testing Results & Container Resource Allocations (T105)

## Overview
This document records load test results for synchronous image segmentation (`/api/v1/inference/segment`) and asynchronous video stream processing (`/api/v1/jobs/video`), along with container resource allocation tuning.

---

## 1. Image Endpoint Load Test Results (T103)
- **Target URL**: `http://localhost:8000/api/v1/inference/segment`
- **Total Requests**: 10
- **Concurrency Workers**: 2
- **Mean Latency**: ~33.5 ms
- **P95 Latency**: ~42.1 ms
- **NFR1 Target Check (<10,000 ms CPU SLA)**: **PASSED**

---

## 2. Video Stream Load Test Results (T104)
- **Target URL**: `http://localhost:8000/api/v1/jobs/video`
- **Total Video Jobs**: 5
- **Concurrency Workers**: 2
- **Completed Jobs**: 5 / 5 (100%)
- **Lost / Timeout Jobs**: 0 (0%)
- **Total Batch Wall-Clock Time**: 1.25 s
- **Async Queue Reliability Check**: **PASSED**

---

## 3. Docker Container Resource Allocations (`infra/docker-compose.yml`)
- **Backend API**: 1.0 CPU, 1GB RAM
- **Celery Worker**: 2.0 CPU, 4GB RAM (PyTorch inference worker)
- **Redis Cache**: 0.5 CPU, 512MB RAM
- **MongoDB**: 1.0 CPU, 2GB RAM
