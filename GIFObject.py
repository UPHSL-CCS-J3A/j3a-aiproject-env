from PIL import Image
import time
import cv2
import numpy as np
class GIFObject:
    def __init__(self, path):
        self.gif = Image.open(path)
        self.frames = []
        self.durations = []
        self.index = 0
        self.last_update_time = time.time()
        self.accumulator = 0.0
        self._load_frames()
    
    def _load_frames(self, default_duration=100):
        try:
            while True:
                frame = cv2.cvtColor(np.array(self.gif.convert("RGBA")), cv2.COLOR_RGBA2BGRA)
                self.frames.append(frame)
                self.durations.append(self.gif.info.get('duration', default_duration))
                self.gif.seek(self.gif.tell() + 1)
        except EOFError:
            pass

    def overlay_next_frame(self, target_frame, padding=10, position = "upper-right", size = None, default_duration=100):
        if not self.frames:
            return
        
        current_time = time.time()
        delta_time = (current_time - self.last_update_time) * 1000
        self.accumulator += delta_time
        self.last_update_time = current_time

        while self.accumulator >= self.durations[self.index]:
            self.accumulator -= self.durations[self.index]
            self.index = (self.index + 1) % len(self.frames)

        gif_frame = self.frames[self.index].copy()

        max_w = min(200, target_frame.shape[1] - 2*padding)
        max_h = min(200, target_frame.shape[0] - 2*padding)

        scale_w = max_w / gif_frame.shape[1]
        scale_h = max_h / gif_frame.shape[0]
        scale = min(scale_w, scale_h, 1.0)

        new_w = max(1, int(gif_frame.shape[1] * scale))
        new_h = max(1, int(gif_frame.shape[0] * scale))
        gif_frame = cv2.resize(gif_frame, (new_w, new_h))

        if size is not None:
            gif_frame = cv2.resize(gif_frame, size)

        if position == "upper-right":
            h_gif, w_gif = gif_frame.shape[:2]
            y1, y2 = int(padding), int(padding + h_gif)
            x1, x2 = int(target_frame.shape[1] - w_gif - padding), int(target_frame.shape[1] - padding)
        elif position == "lower-right":
            h_gif, w_gif = gif_frame.shape[:2]
            y1 = int(target_frame.shape[0] - h_gif - padding)
            y2 = int(target_frame.shape[0] - padding)
            x1 = int(target_frame.shape[1] - w_gif - padding)
            x2 = int(target_frame.shape[1] - padding)

        alpha_gif = gif_frame[:, :, 3] / 255.0
        alpha_frame = 1.0 - alpha_gif
        for c in range(3):
            target_frame[y1:y2, x1:x2, c] = (
                alpha_gif * gif_frame[:, :, c] + alpha_frame * target_frame[y1:y2, x1:x2, c]
            )