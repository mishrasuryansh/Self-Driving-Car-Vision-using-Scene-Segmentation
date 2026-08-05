# Dataset Access & Licensing Documentation

**Project**: Self-Driving Car Vision using Scene Segmentation
**Task**: T010 — Dataset Access & Verification

## 1. Overview
This document specifies the dataset access procedures, licensing compliance, and local sample storage paths for the **Cityscapes** and **BDD100K** urban driving scene segmentation datasets.

## 2. Dataset License Terms & Registration

### Cityscapes Dataset
- **Official Portal**: [https://www.cityscapes-dataset.com/](https://www.cityscapes-dataset.com/)
- **Licensing**: Academic/Non-Commercial Research License.
- **Registration Process**:
  1. Register an academic user account using an official institutional email address.
  2. Accept the Cityscapes End User License Agreement (EULA).
  3. Obtain access to download `gtFine_trainvaltest.zip` and `leftImg8bit_trainvaltest.zip`.

### BDD100K Dataset
- **Official Portal**: [https://bdd-data.berkeley.edu/](https://bdd-data.berkeley.edu/)
- **Licensing**: Berkeley DeepDrive License Agreement for academic research.
- **Registration Process**:
  1. Create an account on the Berkeley DeepDrive portal.
  2. Accept license terms for the 100K video / image segmentation split.

## 3. Local Sample Dataset Path Configuration

Per the repository constitution, raw dataset files are **never** committed to version control. Local sample subsets are stored in a git-ignored directory configured via the environment variable `DATASET_SAMPLE_PATH`.

- **Environment Variable**: `DATASET_SAMPLE_PATH`
- **Default Path**: `./storage/sample_dataset` (or `/app/storage/sample_dataset`)
- **Expected Directory Structure**:
  ```text
  storage/sample_dataset/
  ├── images/
  │   ├── sample_001.png
  │   └── sample_002.png
  └── masks/
      ├── sample_001.png
      └── sample_002.png
  ```

## 4. Verification Script
To verify that a locally downloaded sample subset opens correctly without corruptions, run the verification script:

```bash
python scripts/verify_dataset_sample.py
```
