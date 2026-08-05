import argparse
from segmentation_model import load_segmentation_model
from video_processor import process_video


def main():
    parser = argparse.ArgumentParser(description="Real-Time AI Scene Segmentation on Video")
    parser.add_argument('--video', type=str, required=True, help='Path to input video file')
    args = parser.parse_args()

    model, class_names = load_segmentation_model()
    process_video(args.video, model, class_names)


if __name__ == "__main__":
    main()
