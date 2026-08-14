"""Frames Per Second (FPS) Counter Utility.

Provides wall-clock FPS tracking and calculation across video frames.
"""

import time


class FPSCounter:
    """Utility class to calculate and track frames per second (FPS)."""

    def __init__(self) -> None:
        """Initialize FPS counter with current wall-clock timestamp and zeroed counters."""
        self.last_time: float = time.time()
        self.frame_count: int = 0
        self.fps: float = 0.0

    def update(self) -> None:
        """Increment frame count and update calculated FPS if 1 second has elapsed."""
        self.frame_count += 1
        now = time.time()
        if now - self.last_time >= 1.0:
            self.fps = self.frame_count / (now - self.last_time)
            self.frame_count = 0
            self.last_time = now

    def get_fps(self) -> float:
        """Return the most recently calculated frames per second value.

        Returns:
            float: Calculated FPS value.
        """
        return self.fps
