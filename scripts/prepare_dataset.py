"""Dataset Loader and Preprocessing Pipeline Script.

Provides a reusable PyTorch Dataset subclass (`SemanticSegmentationDataset`) for loading and
preprocessing driving-scene image/mask pairs compatible with DeepLabV3. Reuses the centralized
preprocessing transform factory (`get_default_transform`) and configuration settings (`DEFAULT_IMAGE_SIZE`).
"""

import argparse
import logging
import os
import shutil
import sys
import tempfile
from typing import Any, List, Optional, Tuple

try:
    from PIL import Image
    import numpy as np
    import torch
    from torch.utils.data import DataLoader, Dataset, random_split
    from torchvision import transforms
except ImportError as err:
    raise ImportError(
        "PyTorch, torchvision, NumPy, and Pillow are mandatory dependencies for prepare_dataset.py. "
        "Ensure torch, torchvision, numpy, and Pillow are installed."
    ) from err

# Import centralized configuration and preprocessing pipeline abstractions
try:
    from config import DEFAULT_IMAGE_SIZE
except (ImportError, ValueError):
    try:
        from inference_engine.config import DEFAULT_IMAGE_SIZE
    except (ImportError, ValueError):
        DEFAULT_IMAGE_SIZE = (520, 520)

try:
    from pipeline.processor import get_default_transform
except (ImportError, ValueError):
    try:
        from inference_engine.pipeline.processor import get_default_transform
    except (ImportError, ValueError):
        get_default_transform = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("prepare_dataset")


class SemanticSegmentationDataset(Dataset):
    """PyTorch Dataset for semantic segmentation image and mask pairs.

    Discovers, validates, and preprocesses image-mask pairs from a root directory containing
    image (`images/` or `imgs/`) and label mask (`masks/` or `labels/`) subdirectories.
    Safely skips corrupted or missing files without crashing.
    """

    def __init__(
        self,
        root_dir: str,
        image_size: Tuple[int, int] = DEFAULT_IMAGE_SIZE,
        image_transform: Optional[Any] = None,
        target_transform: Optional[Any] = None,
        image_folder_candidates: Tuple[str, ...] = ("images", "imgs"),
        mask_folder_candidates: Tuple[str, ...] = ("masks", "labels"),
    ) -> None:
        """Initialize the segmentation dataset.

        Args:
            root_dir (str): Root directory path containing image and mask subdirectories.
            image_size (Tuple[int, int]): Target image resolution (height, width).
            image_transform (Optional[Any]): Custom transform for images. If None, reuses `get_default_transform`.
            target_transform (Optional[Any]): Custom transform for label masks.
            image_folder_candidates (Tuple[str, ...]): Candidate subdirectory names for images.
            mask_folder_candidates (Tuple[str, ...]): Candidate subdirectory names for label masks.

        Raises:
            ValueError: If root_dir does not exist or missing required subdirectories.
        """
        if not root_dir or not os.path.exists(root_dir):
            raise ValueError(f"Dataset root directory '{root_dir}' does not exist.")

        self.root_dir = root_dir
        self.image_size = image_size

        self.images_dir = self._find_subdirectory(root_dir, image_folder_candidates)
        self.masks_dir = self._find_subdirectory(root_dir, mask_folder_candidates)

        if not self.images_dir or not self.masks_dir:
            raise ValueError(
                f"Directory '{root_dir}' must contain image ('images'/'imgs') and mask ('masks'/'labels') subdirectories."
            )

        # Reuse centralized transform factory abstraction
        if image_transform is None:
            if get_default_transform is not None:
                self.image_transform = get_default_transform(self.image_size)
            else:
                self.image_transform = transforms.Compose(
                    [
                        transforms.Resize(self.image_size),
                        transforms.ToTensor(),
                    ]
                )
        else:
            self.image_transform = image_transform

        self.target_transform = target_transform

        # Discover and validate sample pairs
        self.samples: List[Tuple[str, str]] = []
        self.skipped_files: List[str] = []
        self.raw_images_count: int = 0
        self.raw_masks_count: int = 0

        self._discover_and_validate_samples()

    @staticmethod
    def _find_subdirectory(root_dir: str, candidates: Tuple[str, ...]) -> Optional[str]:
        """Find the first existing subdirectory matching any candidate name."""
        for candidate in candidates:
            path = os.path.join(root_dir, candidate)
            if os.path.exists(path) and os.path.isdir(path):
                return path
        return None

    def _discover_and_validate_samples(self) -> None:
        """Scan directory and filter valid image-mask pairs, logging corrupt/missing files."""
        if not self.images_dir or not os.path.exists(self.images_dir):
            return

        all_image_files = sorted(
            [
                f
                for f in os.listdir(self.images_dir)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]
        )
        self.raw_images_count = len(all_image_files)

        if self.masks_dir and os.path.exists(self.masks_dir):
            all_mask_files = [
                f
                for f in os.listdir(self.masks_dir)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]
            self.raw_masks_count = len(all_mask_files)

        for img_name in all_image_files:
            img_path = os.path.join(self.images_dir, img_name)
            mask_path = os.path.join(self.masks_dir, img_name)

            if not os.path.exists(mask_path):
                logger.warning("Skipping sample '%s': Missing corresponding mask.", img_name)
                self.skipped_files.append(img_name)
                continue

            try:
                with Image.open(img_path) as img, Image.open(mask_path) as mask:
                    img.verify()
                    mask.verify()
                self.samples.append((img_path, mask_path))
            except Exception as err:
                logger.warning("Skipping corrupt sample '%s': %s", img_name, str(err))
                self.skipped_files.append(img_name)

    def print_integrity_summary(self, train_count: int = 0, val_count: int = 0) -> None:
        """Print a structured dataset integrity and discovery summary report."""
        summary = f"""
====================================================
DATASET DISCOVERY & INTEGRITY SUMMARY
====================================================
Root Path     : {self.root_dir}
Images Folder : {self.images_dir}
Masks Folder  : {self.masks_dir}
Target Size   : {self.image_size}
Images Found  : {self.raw_images_count}
Masks Found   : {self.raw_masks_count}
Valid Pairs   : {len(self.samples)}
Skipped Files : {len(self.skipped_files)}
Train Split   : {train_count}
Val Split     : {val_count}
====================================================
"""
        logger.info(summary)

    def __len__(self) -> int:
        """Return the number of valid samples in the dataset."""
        return len(self.samples)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Fetch preprocessed image and mask tensors at given index.

        Args:
            index (int): Sample index.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Preprocessed float image tensor `(3, H, W)`
                and LongTensor class mask `(H, W)`.
        """
        img_path, mask_path = self.samples[index]

        try:
            with Image.open(img_path) as img:
                rgb_img = img.convert("RGB")
            with Image.open(mask_path) as mask:
                mask_img = mask.copy()

            # Preprocess image using centralized transform pipeline abstraction
            image_tensor = self.image_transform(rgb_img)

            # Preprocess mask (nearest-neighbor resize and convert to LongTensor)
            if self.target_transform is not None:
                mask_tensor = self.target_transform(mask_img)
            else:
                resample_mode = getattr(Image, "Resampling", Image).NEAREST
                resized_mask = mask_img.resize(
                    (self.image_size[1], self.image_size[0]), resample=resample_mode
                )
                mask_np = np.array(resized_mask, dtype=np.int64)
                mask_tensor = torch.from_numpy(mask_np).long()

            return image_tensor, mask_tensor

        except Exception as err:
            logger.error("Error loading sample at index %d ('%s'): %s", index, img_path, str(err))
            raise RuntimeError(f"Failed to load sample at index {index}") from err


def create_train_val_splits(
    dataset: Dataset, val_ratio: float = 0.2, seed: int = 42
) -> Tuple[Dataset, Dataset]:
    """Perform deterministic train and validation splitting on a dataset.

    Args:
        dataset (Dataset): Dataset instance to split.
        val_ratio (float): Fraction of dataset allocated to validation (0.0 to 1.0).
        seed (int): Fixed random seed for reproducibility.

    Returns:
        Tuple[Dataset, Dataset]: (train_dataset, val_dataset) Subsets.
    """
    total_samples = len(dataset)
    if total_samples == 0:
        return dataset, dataset

    val_size = int(total_samples * val_ratio)
    train_size = total_samples - val_size

    generator = torch.Generator().manual_seed(seed)
    train_subset, val_subset = random_split(dataset, [train_size, val_size], generator=generator)
    return train_subset, val_subset


def run_synthetic_test() -> bool:
    """Execute synthetic dataset loading and DataLoader verification test."""
    logger.info("Executing synthetic dataset verification test...")

    temp_dir = tempfile.mkdtemp(prefix="seg_dataset_test_")
    try:
        images_dir = os.path.join(temp_dir, "images")
        masks_dir = os.path.join(temp_dir, "masks")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(masks_dir, exist_ok=True)

        # Create 5 valid sample image/mask pairs
        for i in range(5):
            img_arr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mask_arr = np.random.randint(0, 21, (100, 100), dtype=np.uint8)
            Image.fromarray(img_arr).save(os.path.join(images_dir, f"sample_{i:03d}.png"))
            Image.fromarray(mask_arr).save(os.path.join(masks_dir, f"sample_{i:03d}.png"))

        # Create 1 corrupt sample to verify graceful error skipping
        corrupt_path = os.path.join(images_dir, "sample_corrupt.png")
        with open(corrupt_path, "wb") as f:
            f.write(b"NOT_AN_IMAGE_FILE_HEADER_CORRUPT")
        with open(os.path.join(masks_dir, "sample_corrupt.png"), "wb") as f:
            f.write(b"NOT_A_MASK_FILE_HEADER_CORRUPT")

        dataset = SemanticSegmentationDataset(temp_dir, image_size=DEFAULT_IMAGE_SIZE)
        assert len(dataset) == 5, f"Expected 5 valid samples, found {len(dataset)}"
        assert len(dataset.skipped_files) == 1, "Expected 1 skipped corrupt file"

        train_ds, val_ds = create_train_val_splits(dataset, val_ratio=0.2, seed=42)
        assert len(train_ds) == 4
        assert len(val_ds) == 1

        dataset.print_integrity_summary(train_count=len(train_ds), val_count=len(val_ds))

        loader = DataLoader(train_ds, batch_size=2, shuffle=False)
        for images, masks in loader:
            logger.info(
                "[SYNTHETIC TEST PASS] Loaded batch: images shape %s, masks shape %s",
                list(images.shape),
                list(masks.shape),
            )
            assert list(images.shape) == [2, 3, DEFAULT_IMAGE_SIZE[0], DEFAULT_IMAGE_SIZE[1]]
            assert list(masks.shape) == [2, DEFAULT_IMAGE_SIZE[0], DEFAULT_IMAGE_SIZE[1]]
            break

        logger.info("[SUCCESS] Synthetic dataset verification test completed successfully!")
        return True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> None:
    """Script execution entry point."""
    parser = argparse.ArgumentParser(description="Dataset Loader & Preprocessing Script")
    parser.add_argument(
        "--data-dir",
        type=str,
        default=os.getenv("DATASET_SAMPLE_PATH", os.path.join("storage", "sample_dataset")),
        help="Root directory containing image and mask subdirectories.",
    )
    parser.add_argument(
        "--image-size",
        type=int,
        nargs="+",
        default=[DEFAULT_IMAGE_SIZE[0], DEFAULT_IMAGE_SIZE[1]],
        help="Target image size (e.g. --image-size 520).",
    )
    parser.add_argument("--val-ratio", type=float, default=0.2, help="Validation split ratio.")
    parser.add_argument("--batch-size", type=int, default=4, help="DataLoader batch size.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for split reproducibility.")
    parser.add_argument("--test-synthetic", action="store_true", help="Run synthetic self-test.")

    args = parser.parse_args()

    if len(args.image_size) == 1:
        img_size = (args.image_size[0], args.image_size[0])
    else:
        img_size = (args.image_size[0], args.image_size[1])

    if args.test_synthetic:
        success = run_synthetic_test()
        sys.exit(0 if success else 1)

    logger.info("Target dataset path: %s (image_size=%s)", args.data_dir, img_size)

    if not os.path.exists(args.data_dir):
        logger.info(
            "Dataset directory '%s' does not exist locally. "
            "Running synthetic self-test to verify pipeline integrity...",
            args.data_dir,
        )
        success = run_synthetic_test()
        sys.exit(0 if success else 1)

    try:
        dataset = SemanticSegmentationDataset(args.data_dir, image_size=img_size)
        train_ds, val_ds = create_train_val_splits(dataset, val_ratio=args.val_ratio, seed=args.seed)

        dataset.print_integrity_summary(train_count=len(train_ds), val_count=len(val_ds))

        train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)

        for images, masks in train_loader:
            logger.info(
                "Sample train batch — images shape: %s, masks shape: %s",
                list(images.shape),
                list(masks.shape),
            )
            break

        logger.info("Dataset loader preparation completed cleanly.")
    except Exception as err:
        logger.error("Dataset preparation failed: %s", str(err), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
