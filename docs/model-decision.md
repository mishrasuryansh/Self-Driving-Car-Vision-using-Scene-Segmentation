# Architectural Decision Record: AI Model Strategy & Selection

**Status**: APPROVED
**Epic**: EP1 (Project Foundation) | **Feature**: F1.5 (Model Strategy & Dataset Access Decision) | **Task**: T009
**Date**: August 2026
**Author**: AI Software Architect & Development Team

---

## 1. Objective

The objective of this Architecture Decision Record (ADR) is to evaluate candidate deep-learning semantic segmentation architectures and officially establish the primary model strategy for the **Self-Driving Car Vision using Scene Segmentation** platform.

This decision freezes the model interface architecture for **Epic 2 (Core AI Pipeline Upgrade)** and subsequent microservice development, ensuring strict adherence to Clean Architecture, SOLID design principles, CPU-fallback hardware constraints (Master Doc Section 4.8), and the AI Project Constitution.

---

## 2. Existing Legacy Model Analysis

The legacy repository prototype (`legacy/Self_Driving_Vision-main/segmentation_model.py`) contains a functional baseline model implementation:

- **Model Architecture**: `torchvision.models.segmentation.deeplabv3_resnet101` loaded via PyTorch/torchvision.
- **Dataset & Taxonomy**: Pretrained on Pascal VOC (21 classes: `background`, `aeroplane`, `bicycle`, `bird`, `boat`, `bottle`, `bus`, `car`, `cat`, `chair`, `cow`, `diningtable`, `dog`, `horse`, `motorbike`, `person`, `pottedplant`, `sheep`, `sofa`, `train`, `tvmonitor`).
- **Temporary Class Mapping**: To simulate autonomous driving perception, the legacy code maps a subset of VOC classes:
  - `aeroplane` (index 1) → temporary simulation as `sky`
  - `bicycle` (index 2) → temporary simulation as `road`
  - `bird` (index 3) → temporary simulation as `tree`
  - `diningtable` (index 11) → temporary simulation as `building`
  - `sheep` (index 17) → temporary simulation as `tree`
- **Strengths**:
  1. Already implemented, tested, and validated in the legacy codebase.
  2. Zero external model training required.
  3. Proven CPU execution compatibility.

---

## 3. Candidate Models Overview

Five prominent semantic segmentation model families were evaluated:

1. **DeepLabV3-ResNet101 (Pascal VOC Pretrained)**: Baseline torchvision model with 21 VOC classes and temporary class mapping.
2. **DeepLabV3-ResNet101 (Cityscapes / BDD100K Fine-Tuned)**: DeepLabV3 architecture fine-tuned specifically on urban driving scenes (Cityscapes / BDD100K 19-class standard).
3. **YOLOv8 Segmentation (YOLOv8s-seg / YOLOv8m-seg)**: Real-time instance segmentation architecture developed by Ultralytics.
4. **SegFormer (MiT-B0 / MiT-B2)**: Lightweight Transformer-based semantic segmentation architecture utilizing a hierarchical Mix Transformer encoder.
5. **Mask2Former (Swin-Base / ResNet-50)**: Universal segmentation architecture (panoptic/instance/semantic) using masked-attention Transformers.

---

## 4. Comprehensive Comparison Table

| Metric / Dimension | 1. DeepLabV3 (VOC Baseline) | 2. DeepLabV3 (Cityscapes) | 3. YOLOv8-Seg (Instance) | 4. SegFormer (MiT-B0) | 5. Mask2Former |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Segmentation Type**| Semantic Segmentation | Semantic Segmentation | Instance Segmentation | Semantic Segmentation | Panoptic/Universal |
| **Target Taxonomy** | Pascal VOC (21 cls) | Urban Driving (19 cls) | COCO / Custom (80+ cls)| Cityscapes (19 cls) | Universal / Panoptic |
| **Model Weight Size** | ~244 MB | ~244 MB | ~6 MB - ~22 MB | ~14 MB | ~200 MB+ |
| **CPU Latency (520x520)**| ~350 - 500 ms | ~350 - 500 ms | ~45 - 90 ms | ~250 - 400 ms | > 1200 ms |
| **Framework Dependency**| Native torchvision | Native torchvision | Ultralytics / ONNX | Hugging Face | Detectron2 |
| **Implementation Risk**| **Lowest (Existing)** | Low | Medium | Medium | High |
| **CPU Fallback Fit** | **Optimal** | Optimal | Good | Moderate | Unviable |
| **B.Tech Project Scope** | **Baseline Selected** | Future Upgrade | Future Integration | High Complexity | Over-engineered |

---

## 5. Evaluation Criteria

Candidates were evaluated across 5 weighted dimensions aligned with non-functional requirements (NFRs) and constraints:

1. **Implementation Risk & Readiness (30%)**: Leverages existing legacy code without requiring immediate model training or extra setup.
2. **CPU Fallback & Hardware Compatibility (25%)**: Runs reliably on CPU hardware without mandatory GPU dependencies (Master Doc Section 4.8).
3. **Clean Architecture & Interface Fit (20%)**: Direct compatibility with PyTorch/torchvision and a clean `ModelBackend` abstraction.
4. **B.Tech Project Scope & Maintainability (15%)**: Manageable complexity for a single-semester timeline.
5. **Future Upgradeability (10%)**: Ease of upgrading weights or inference engines later.

---

## 6. Selected Primary Architecture

**DeepLabV3-ResNet101 pretrained on Pascal VOC** will remain the official baseline implementation for EP2 because it already exists in the legacy codebase and fully complies with the project constitution, hardware constraints, and implementation roadmap.

The inference engine will be designed around an abstract `ModelBackend` interface so that future Cityscapes-fine-tuned weights or alternative backbones can replace the pretrained weights without requiring API or architectural changes.

---

## 7. Reasons for Selection

1. **Already Implemented & Validated**: Functional baseline existing in `legacy/Self_Driving_Vision-main/segmentation_model.py`.
2. **Native Torchvision Support**: Built directly into `torchvision.models.segmentation`, requiring no third-party framework overhead.
3. **Compatible with Current Inference Pipeline**: Directly fits into the single-image and video processing workflow.
4. **Reliable CPU Execution**: Operates efficiently on standard CPU hardware without GPU acceleration dependencies.
5. **No Training Required**: Eliminates immediate GPU training execution, dataset downloading, and compute risk.
6. **Suitable for B.Tech Major Project Scope**: Well-scoped for a single-semester academic timeline and portfolio presentation.
7. **Modular Weight Replacement**: Allows seamless weight updates via the `ModelBackend` abstraction.
8. **Lowest Implementation Risk**: Highest stability and predictability for the EP2 milestone.

---

## 8. Current Limitations of Pascal VOC Baseline

While selected as the EP2 baseline, the Pascal VOC pretrained model has known limitations that will be addressed in future upgrades:

1. **Limited to 21 VOC Classes**: Pretrained on general visual objects (`aeroplane`, `bird`, `dog`, etc.) rather than specialized driving environments.
2. **Requires Temporary Class Mapping**: Uses heuristic class mapping to simulate driving categories (`aeroplane` → `sky`, `bicycle` → `road`, etc.).
3. **Lower Semantic Richness**: Does not natively distinguish detailed urban categories like sidewalks, traffic signs, lane lines, or riders.
4. **Baseline Purpose**: Acts as a verified working baseline to prove end-to-end pipeline functionality before introducing fine-tuned weights.

---

## 9. Future Recommended Upgrade Strategy

Once officially trained or externally supplied Cityscapes/BDD100K weights become available, the project can seamlessly migrate to:

- **DeepLabV3-ResNet101 (Cityscapes Fine-Tuned)**: Full 19-class urban driving taxonomy (Road, Sidewalk, Vehicle, Pedestrian, Vegetation, Sky, Building, etc.).
- **DeepLabV3-ResNet101 (BDD100K Fine-Tuned)**: Enhanced robustness for diverse weather and lighting conditions.

Because all inference calls pass through the `ModelBackend` interface, upgrading to Cityscapes or BDD100K weights requires **zero changes** to backend FastAPI endpoints, Celery worker tasks, or React frontend components.

---

## 10. Future Integration of YOLOv8-Seg

YOLOv8-Seg will be evaluated for **future integration through the `ModelBackend` abstraction**.

> [!NOTE]
> **Architectural Distinction**: YOLOv8-Seg performs *instance segmentation* (detecting individual object bounding boxes and masks), whereas DeepLabV3 performs *semantic segmentation* (assigning a class label to every pixel). Because their outputs are not directly interchangeable, YOLOv8-Seg will be integrated via a dedicated backend adapter if real-time instance tracking is required in later phases.

---

## 11. Hardware & Deployment Considerations

- **CPU Execution**: DeepLabV3 Pascal VOC executes single-frame inference in ~350ms on CPU, suitable for synchronous REST API requests.
- **Asynchronous Video Pipeline**: Asynchronous video jobs will process frame batches via Redis queue workers in background tasks.
- **Memory Footprint**: State dict requires ~244 MB storage and ~1.2 GB RAM during inference execution, fitting comfortably within standard container limits.

---

## 12. Upgrade Path & Roadmap

The architecture provides a clean modular progression path:

```
Legacy DeepLabV3 (Pascal VOC)
        │
        ▼
EP2 Implementation Baseline
        │
        ▼
Modular ModelBackend Interface
        │
        ├──────────────► DeepLabV3 Cityscapes (Fine-Tuned Weights)
        │
        ├──────────────► DeepLabV3 BDD100K (Fine-Tuned Weights)
        │
        ├──────────────► ONNX Runtime Acceleration
        │
        └──────────────► YOLOv8-Seg (Future Instance Segmentation)
```

---

## 13. Risk Analysis & Mitigation Matrix

| Identified Risk | Severity | Mitigation Strategy |
| :--- | :---: | :--- |
| **Deprecated PyTorch API (`pretrained=True`)** | Low | Update to `weights=DeepLabV3_ResNet101_Weights.DEFAULT` in EP2. |
| **Class Mapping Ambiguity** | Low | Explicitly document temporary VOC-to-driving mapping dictionary in `inference-engine/`. |
| **High CPU Video Processing Latency** | Medium | Implement frame skipping (process every N-th frame) during video worker processing. |

---

## 14. Future Migration Strategy

When transitioning beyond the baseline:
1. Replace torchvision default weights with fine-tuned Cityscapes weights via configuration.
2. Export DeepLabV3 model to **ONNX Runtime** for 2x-3x CPU inference acceleration.
3. Enable optional CUDA GPU acceleration flag (`MODEL_DEVICE=cuda`) when deployed on GPU-enabled infrastructure.

---

## 15. Final Architecture Decision

The project will implement **DeepLabV3-ResNet101 with Pascal VOC pretrained weights** as the baseline semantic segmentation engine for EP2. This decision leverages the existing legacy implementation, minimizes project risk, and satisfies CPU-only deployment constraints. The inference engine will be designed with a modular `ModelBackend` abstraction to enable future migration to Cityscapes/BDD100K fine-tuned weights, ONNX Runtime, or other segmentation models without affecting higher application layers.
