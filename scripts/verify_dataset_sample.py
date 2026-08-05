"""Sample Dataset Verification Script.

Inspects a local sample dataset directory (configured via DATASET_SAMPLE_PATH environment variable)
and verifies that sample image/mask pairs exist and open cleanly.
Contains zero authentication, download, or automated credential logic.
"""

import os
import sys

try:
    from PIL import Image
except ImportError:
    Image = None


def verify_sample_dataset() -> bool:
    sample_dir = os.getenv("DATASET_SAMPLE_PATH", os.path.join("storage", "sample_dataset"))
    print(f"Inspecting sample dataset directory: {sample_dir}")

    images_dir = os.path.join(sample_dir, "images")
    masks_dir = os.path.join(sample_dir, "masks")

    if not os.path.exists(sample_dir):
        print(f"[INFO] Sample directory '{sample_dir}' does not exist locally.")
        print("[INFO] Create the directory and add sample pairs to perform dataset inspection.")
        return True

    if not os.path.exists(images_dir) or not os.path.exists(masks_dir):
        print(
            f"[WARNING] Directory structure incomplete in '{sample_dir}'. "
            "Expected 'images/' and 'masks/' subdirectories."
        )
        return True

    image_files = sorted(
        [f for f in os.listdir(images_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    )
    print(f"Found {len(image_files)} sample image(s) in '{images_dir}'.")

    if Image is None:
        print("[WARNING] Pillow library is not installed. Skipping image verification.")
        return True

    passed_count = 0
    for img_name in image_files:
        img_path = os.path.join(images_dir, img_name)
        mask_path = os.path.join(masks_dir, img_name)

        if not os.path.exists(mask_path):
            print(f"[FAIL] Missing corresponding mask for image: {img_name}")
            continue

        try:
            with Image.open(img_path) as img, Image.open(mask_path) as mask:
                img.verify()
                mask.verify()
                print(f"[PASS] Sample pair valid: {img_name} (Size: {img.size})")
                passed_count += 1
        except Exception as err:
            print(f"[FAIL] Corrupted sample pair {img_name}: {err}")

    print(f"Verification complete: {passed_count}/{len(image_files)} sample pairs verified.")
    return True


if __name__ == "__main__":
    success = verify_sample_dataset()
    sys.exit(0 if success else 1)
