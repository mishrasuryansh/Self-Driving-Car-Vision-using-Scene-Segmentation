# Self-Driving Car Vision Platform - Frontend End-to-End Smoke Test Document (T078)

## Milestone M5 Frontend MVP Manual Execution Checklist

This document provides a step-by-step verification script for validating the integrated web application (React SPA, FastAPI backend, Celery worker queue, Redis, MongoDB, and PyTorch inference engine).

---

### Test Step 1: Homepage & Value Proposition
- **Action**: Navigate to `http://localhost:5173/` (or app root URL).
- **Expected Result**: Dashboard loads smoothly, persistent Navigation Bar renders brand logo, quick upload widget, and statistics cards. No layout overflow on mobile (375px viewport).

---

### Test Step 2: User Account Registration
- **Action**: Click "Register" in navigation bar, fill in name, email (`tester@selfdriving.com`), password (`TestPass123!`), and click submit.
- **Expected Result**: Account is created via `POST /api/v1/auth/register`, auto-login occurs issuing JWT bearer token, and user is redirected to Dashboard with full name displayed in navbar.

---

### Test Step 3: Protected Route Enforcement
- **Action**: Click "Logout", then try to access `http://localhost:5173/upload/image` directly via browser address bar.
- **Expected Result**: ProtectedRoute guard intercepts request and redirects unauthenticated user to `/login`.

---

### Test Step 4: Synchronous Image Scene Segmentation
- **Action**: Log in, navigate to `/upload/image`, select a road scene sample JPEG/PNG, select `DeepLabV3+ (ResNet-101 ASPP)`, and click "Run Scene Segmentation".
- **Expected Result**: Image is uploaded to `POST /api/v1/inference/segment`, inference returns in <500ms, ResultViewer displays interactive opacity blending overlay slider, download button works, and metrics panel shows >30 FPS and per-class distribution breakdown.

---

### Test Step 5: Asynchronous Video Stream Segmentation
- **Action**: Navigate to `/upload/video`, select a dashcam MP4 video file, click "Start Async Video Segmentation".
- **Expected Result**: Video is enqueued via `POST /api/v1/jobs/video` returning HTTP 202 Accepted and "queued" status in <200ms. JobStatusStepper auto-polls status every 1000ms through `queued` -> `processing` -> `completed` with progress bar updates. Segmented output MP4 video plays smoothly with aggregate metrics.

---

### Test Step 6: Perception History & Inspection Modal
- **Action**: Navigate to `/history`.
- **Expected Result**: History table lists all previous image and video jobs. Filter dropdown allows filtering by `Completed`, `Processing`, or `Failed`. Clicking "Inspect Details" opens modal showing job metadata and performance statistics.

---

### Test Step 7: Perception Analytics Dashboard
- **Action**: Navigate to `/analytics`.
- **Expected Result**: Summary metrics cards display Average Throughput FPS, Mean Frame Latency (ms), Total Jobs Completed, and system health status.

---

### Test Step 8: User Settings & Preference Persistence
- **Action**: Navigate to `/settings`, change model preference to `DeepLabV3+ (MobileNetV3)`, click "Save Preference".
- **Expected Result**: Toast notification confirms "Preference Saved", and choice is persisted in `localStorage`.
