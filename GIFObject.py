"""GIF animation handler for overlay on video frames."""

from PIL import Image
import time
import cv2
import numpy as np


class GIFObject:
    """Handles GIF loading and frame-by-frame overlay on video frames."""
    
    def __init__(self, path):
        """Initialize GIF object and load all frames.
        
        Args:
            path: File path to the GIF image
        """
        self.gif = Image.open(path)
        self.frames = []
        self.durations = []
        self.index = 0
        self.last_update_time = time.time()
        self.accumulator = 0.0
        self._load_frames()
    
    def _load_frames(self, default_duration=100):
        """Load all frames from the GIF into memory.
        
        Args:
            default_duration: Default frame duration in ms if not specified in GIF
        """
        try:
            while True:
                frame = cv2.cvtColor(np.array(self.gif.convert("RGBA")), cv2.COLOR_RGBA2BGRA)
                self.frames.append(frame)
                self.durations.append(self.gif.info.get('duration', default_duration))
                self.gif.seek(self.gif.tell() + 1)
        except EOFError:
            pass

    def overlay_next_frame(self, target_frame, padding=10, position="upper-right", size=None, default_duration=100):
        """Overlay the current GIF frame onto the target frame with alpha blending.
        
        Args:
            target_frame: The video frame to overlay the GIF on
            padding: Padding from edges in pixels
            position: Position of overlay ("upper-right" or "lower-right")
            size: Optional tuple (width, height) to resize GIF to
            default_duration: Default frame duration if not specified
        """
        if not self.frames:
            return
        
        # Update frame timing
        current_time = time.time()
        delta_time = (current_time - self.last_update_time) * 1000
        self.accumulator += delta_time
        self.last_update_time = current_time

        # Advance to next frame if duration exceeded
        while self.accumulator >= self.durations[self.index]:
            self.accumulator -= self.durations[self.index]
            self.index = (self.index + 1) % len(self.frames)

        gif_frame = self.frames[self.index].copy()

        # Calculate scaling to fit within max dimensions
        max_w = min(200, target_frame.shape[1] - 2*padding)
        max_h = min(200, target_frame.shape[0] - 2*padding)
        scale = min(max_w / gif_frame.shape[1], max_h / gif_frame.shape[0], 1.0)
        
        new_w = max(1, int(gif_frame.shape[1] * scale))
        new_h = max(1, int(gif_frame.shape[0] * scale))
        gif_frame = cv2.resize(gif_frame, (new_w, new_h))

        # Apply custom size if specified
        if size is not None:
            gif_frame = cv2.resize(gif_frame, size)

        # Calculate overlay position
        h_gif, w_gif = gif_frame.shape[:2]
        if position == "upper-right":
            y1, y2 = int(padding), int(padding + h_gif)
            x1, x2 = int(target_frame.shape[1] - w_gif - padding), int(target_frame.shape[1] - padding)
        elif position == "lower-right":
            y1 = int(target_frame.shape[0] - h_gif - padding)
            y2 = int(target_frame.shape[0] - padding)
            x1 = int(target_frame.shape[1] - w_gif - padding)
            x2 = int(target_frame.shape[1] - padding)

        # Alpha blend the GIF onto the target frame
        alpha_gif = gif_frame[:, :, 3] / 255.0
        alpha_frame = 1.0 - alpha_gif
        for c in range(3):  # BGR channels
            target_frame[y1:y2, x1:x2, c] = (
                alpha_gif * gif_frame[:, :, c] + alpha_frame * target_frame[y1:y2, x1:x2, c]
            )