
# Self-Driving Vision Demo
<img width="1037" height="676" alt="image" src="https://github.com/user-attachments/assets/7f0b08e0-e94f-4a77-97d4-6cbbc376bd50" />

---

### Project Description
This project demonstrates real-time semantic scene segmentation on video, simulating how autonomous vehicles perceive their environment. It uses DeepLabV3 (ResNet101 backbone) to classify every pixel in each video frame and overlays colored segmentation masks for classes like road, sky, trees, people, cars, and buildings.

### Features
- Real-time video processing and display
- Per-pixel semantic segmentation (not bounding boxes)
- Colored overlays for each class (e.g., sky, road, trees, people, cars, buildings)
- Transparent mask overlay for AI perception effect
- Real-time FPS and inference time display
- Output video saved as `output_segmentation.mp4`
- Overlay panel shows detected classes and simulated car speed

---

### File Structure

```
project/
├── main.py                # Entry point, parses arguments and runs pipeline
├── segmentation_model.py   # Loads DeepLabV3 model and runs segmentation
├── video_processor.py      # Handles video reading, processing, overlays, and saving
├── utils/
│   ├── color_map.py        # Color mapping for segmentation classes
│   └── fps_counter.py      # FPS calculation utility
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

### How to Fork & Use
1. Click the **Fork** button on GitHub to copy the repo to your account.
2. Clone your fork:
	```bash
	git clone https://github.com/<your-username>/self-driving-vision-demo.git
	cd self-driving-vision-demo/project
	```
3. Install dependencies:
	```bash
	pip install -r requirements.txt
	```
4. Run the demo:
	```bash
	python main.py --video input_video.mp4
	```
5. The output video will be saved as `output_segmentation.mp4`.

---

### Relevance (Wikipedia-style)
Semantic scene segmentation is a core technology in computer vision, enabling machines to understand environments at the pixel level. In autonomous vehicles, this allows for precise detection of roads, obstacles, pedestrians, and other objects, improving safety and navigation. This project simulates how self-driving cars perceive their surroundings, providing a visual and technical demonstration of advanced AI perception.

---

### Example Command
```bash
python main.py --video input_video.mp4
```

---

### Notes
- Requires a CUDA-capable GPU for best real-time performance, but will run on CPU (slower).
- Uses DeepLabV3 pretrained on COCO/VOC via torchvision.
