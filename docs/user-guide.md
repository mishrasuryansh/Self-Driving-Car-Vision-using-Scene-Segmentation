# Self-Driving Car Vision Platform - End-User Guide (T108)

Welcome to the **Self-Driving Car Vision Scene Segmentation Platform**. This non-technical user guide walks evaluators and first-time users through operating the application.

---

## Step 1: User Account Registration & Login
1. Open your web browser and navigate to `http://localhost:5173`.
2. Click **"Register"** in the top navigation bar.
3. Enter your **Full Name**, **Email Address**, and a secure **Password** (min 8 characters).
4. Click **"Register Account"**. You will automatically be logged in and redirected to the Perception Dashboard.

---

## Step 2: Running Real-Time Image Scene Segmentation
1. Click **"Upload Image"** in the navigation bar.
2. Drag and drop or browse to select a road scene photo (`.jpg`, `.png`, or `.webp`).
3. Select your preferred model architecture (e.g., `DeepLabV3+ (ResNet-101 ASPP)`).
4. Click **"Run Scene Segmentation"**.
5. **Interpreting Results**:
   - Use the **Mask Opacity Slider** to blend the segmentation color overlay over the original scene.
   - Toggle **Side-by-Side** mode to view original and segmented output side by side.
   - Inspect the **Class Distribution Legend** showing road %, vehicle %, sky %, and vegetation % breakdown.
   - Click **"Download Result"** to save the processed image.

---

## Step 3: Asynchronous Dashcam Video Processing
1. Click **"Upload Video"** in the navigation bar.
2. Select a dashcam video stream file (`.mp4`, `.avi`, or `.mov`).
3. Click **"Start Async Video Segmentation"**.
4. Watch the interactive **Job Status Stepper** transition from `Queued` -> `Processing` -> `Completed`.
5. Play the segmented output MP4 video directly in the HTML5 player and review aggregate throughput FPS.

---

## Step 4: Inspecting History & Perception Analytics
1. Click **"History"** to view a filterable log of all past segmentation jobs. Click **"Inspect Details"** on any row to open the full metrics modal.
2. Click **"Analytics"** to view time-series job volume charts, average latency indicators, and export summary data to a CSV file by clicking **"Export CSV"**.
