import cv2, mediapipe as mp, math, time
from PIL import Image
import numpy as np
import pygame
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

stable_status = "GOOD POSTURE"
stable_action = "GOOD DISTANCE"
statuschange_delay = 2
statuschange_starttime = None
# Calibration variables
ref_nose_shoulder_dist = None
calibrated = False
action = "GOOD DISTANCE"
# GIF Setup
import time
import cv2
import numpy as np
from PIL import Image

class GIFObject:
    def __init__(self, path, default_duration=100):
        self.gif = Image.open(path)
        self.frames = []
        self.durations = []
        try:
            while True:
                frame = cv2.cvtColor(np.array(self.gif.convert("RGBA")), cv2.COLOR_RGBA2BGRA)
                self.frames.append(frame)
                # Use the GIF's duration if available, otherwise default
                self.durations.append(self.gif.info.get('duration', default_duration))
                self.gif.seek(self.gif.tell() + 1)
        except EOFError:
            pass
        self.index = 0
        self.last_update_time = time.time()  # timestamp of last frame update
        self.accumulator = 0.0  # accumulated time in milliseconds

    def overlay_next_frame(self, target_frame, padding=10):
        """
        Overlay the next GIF frame onto the target frame with alpha blending,
        using the GIF's own timing to control frame advancement.
        """
        # --- Handle delta time for GIF frame advancement ---
        current_time = time.time()
        delta_time = (current_time - self.last_update_time) * 1000  # ms
        self.accumulator += delta_time
        self.last_update_time = current_time

        # Advance frame if accumulated time exceeds current frame's duration
        while self.accumulator >= self.durations[self.index]:
            self.accumulator -= self.durations[self.index]
            self.index = (self.index + 1) % len(self.frames)

        gif_frame = self.frames[self.index]

        # Determine maximum allowed size
        max_w = min(200, target_frame.shape[1] - 2*padding)
        max_h = min(200, target_frame.shape[0] - 2*padding)

        # Compute scale factor
        scale_w = max_w / gif_frame.shape[1]
        scale_h = max_h / gif_frame.shape[0]
        scale = min(scale_w, scale_h, 1.0)

        # Resize GIF
        new_w = max(1, int(gif_frame.shape[1] * scale))
        new_h = max(1, int(gif_frame.shape[0] * scale))
        gif_frame = cv2.resize(gif_frame, (new_w, new_h))


        
        # --- Determine overlay position (upper-right) ---
        h_gif, w_gif = gif_frame.shape[:2]
        y1, y2 = int(padding), int(padding + h_gif)
        x1, x2 = int(target_frame.shape[1] - w_gif - padding), int(target_frame.shape[1] - padding)

        # --- Alpha blending ---
        alpha_gif = gif_frame[:, :, 3] / 255.0
        alpha_frame = 1.0 - alpha_gif
        for c in range(3):  # BGR channels only
            target_frame[y1:y2, x1:x2, c] = (
                alpha_gif * gif_frame[:, :, c] + alpha_frame * target_frame[y1:y2, x1:x2, c]
            )


intro_gif = GIFObject("./assets/cropped_ergonomics.gif")
bad_gif = GIFObject("./assets/car.gif")
good_gif = GIFObject("./assets/full-ergonomics.gif", 300)
# Sound Setup
pygame.mixer.init()
sounds = {
    "bad": pygame.mixer.Sound("./assets/laugh.mp3"),

}
prev_status = stable_status
while True:
    ret, frame = cap.read()
    if not ret: break
    h, w = frame.shape[:2]
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = pose.process(img)
    
    if res.pose_landmarks:
        # Draw pose landmarks | Identified Parts of the User From Webcam
        mp_draw.draw_landmarks(frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        lm = res.pose_landmarks.landmark
        
        # Get key points
        L = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
        R = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        nose = lm[mp_pose.PoseLandmark.NOSE]
        L_z = L.z
        R_z = R.z
        # Convert to pixel coordinates
        L_px = (int(L.x*w), int(L.y*h))
        R_px = (int(R.x*w), int(R.y*h))
        nose_px = (int(nose.x*w), int(nose.y*h))
        neck_px = ((L_px[0]+R_px[0])//2, (L_px[1]+R_px[1])//2)
        
        # Calculate current posture using nose to shoulder y-distance
        shoulder_y = (L.y + R.y) / 2  # average shoulder y position
        nose_shoulder_dist = abs(nose.y - shoulder_y)
        
        # Determine posture status
        if calibrated:
            # Adjusted Logic for Recommended Actions
            scale_factor = shoulder_y / ref_shoulder_y
            dist_diff = nose_shoulder_dist - ref_nose_shoulder_dist * scale_factor
            shoulder_depth_diff = ((L.z + R.z)/2) - ref_shoulder_z
            nose_depth_diff = nose.z - ref_nose_z
            good_posture = abs(dist_diff) < 0.02 * scale_factor # threshold for good posture
            current_status = "GOOD POSTURE" if good_posture else "BAD POSTURE"
            current_action = "MOVE FARTHER FROM CAMERA" if nose_depth_diff < -0.5 else "CHIN UP" if (dist_diff < 0.01 * scale_factor) else "CHIN DOWN" if (dist_diff > 0.03 * scale_factor) else "GOOD DISTANCE"
            if current_status != stable_status:
                if statuschange_starttime is None:
                    statuschange_starttime = time.time()
                elif time.time() - statuschange_starttime > statuschange_delay:
                    stable_status = current_status
                    statuschange_starttime = None
            else:
                statuschange_starttime = None
            status = stable_status
            action = current_action
        else:
            status = "PRESS 'C' TO CALIBRATE"
        
        color = (0,255,0) if (calibrated and status == "GOOD POSTURE") else (0,0,255) if (calibrated and status == "BAD POSTURE") else (255,255,0)
        if status == "BAD POSTURE":
            bad_gif.overlay_next_frame(frame)
            if prev_status != "BAD POSTURE":
                print("Plays Music")
                pygame.mixer.stop()
                sounds["bad"].play(loops=-1)
        elif status == "GOOD POSTURE":
            good_gif.overlay_next_frame(frame)
            if prev_status != "GOOD POSTURE":
                pygame.mixer.stop()
        prev_status = status
        # Draw visual feedback
        base_y = 50
        cv2.line(frame, L_px, R_px, color, 3)  # shoulder line
        cv2.line(frame, neck_px, nose_px, color, 2)  # neck line
        cv2.circle(frame, nose_px, 8, color, -1)  # nose point
        cv2.putText(frame, status, (20, base_y), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        cv2.putText(frame, f"Nose-Shoulder Dist: {nose_shoulder_dist:.3f}", (20,base_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
        
        if calibrated:
            cv2.putText(frame, f"Nose Depth: {nose_depth_diff:.3f}", (20, base_y+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, f"Shoulder Depth: {shoulder_depth_diff:.3f}", (20, base_y+60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, "Press 'R' to recalibrate", (20,base_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            cv2.putText(frame, action, (20, base_y + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        

        if not calibrated:
            intro_gif.overlay_next_frame(frame, 0.65)


    cv2.imshow('Posture Detection', frame)
    key = cv2.waitKey(1)&0xFF
    if key == ord('q'): break
    elif key == ord('c') or key == ord('r'):
        if res.pose_landmarks:
            lm = res.pose_landmarks.landmark
            L = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
            R = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            nose = lm[mp_pose.PoseLandmark.NOSE]
            ref_nose_z = nose.z
            ref_shoulder_z = (L.z + R.z) / 2
            shoulder_y = ref_shoulder_y = (L.y + R.y) / 2
            ref_nose_shoulder_dist = abs(nose.y - shoulder_y)
            calibrated = True
            print("Calibrated! Current posture set as reference.")
cap.release(); cv2.destroyAllWindows()