import cv2, mediapipe as mp, math, time
from PIL import Image
import numpy as np
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

stable_status = "GOOD POSTURE"
statuschange_delay = 2
statuschange_starttime = None
# Calibration variables
ref_nose_shoulder_dist = None
calibrated = False

# GIF Setup
class GIFObject:
    def __init__(self, path):
        self.gif = Image.open(path)
        self.frames = []
        self.durations = []
        try:
            while True:
                frame = cv2.cvtColor(np.array(self.gif.convert("RGBA")), cv2.COLOR_RGBA2BGRA)
                self.frames.append(frame)
                self.durations.append(self.gif.info.get('duration', 100))
                self.gif.seek(self.gif.tell() + 1)
        except EOFError:
            pass
        self.index = 0
    def overlay_next_frame(self, target_frame, size_multiplier=0.65, padding=10):
            """
            Overlay the next GIF frame onto the target frame with alpha blending.

            Args:
                target_frame: The main OpenCV frame to overlay onto (BGR).
                position: "upper-right", "upper-left", etc. (currently only upper-right implemented)
                size_multiplier: Scale factor for GIF size.
                padding: Padding from the window edge.
            """
            # Get next frame
            gif_frame = self.frames[self.index]
            self.index = (self.index + 1) % len(self.frames)

            # Resize frame
            width = int(gif_frame.shape[1] * size_multiplier)
            height = int(gif_frame.shape[0] * size_multiplier)
            gif_frame = cv2.resize(gif_frame, (width, height))

            # Determine overlay position
            h_gif, w_gif = gif_frame.shape[:2]
            y1, y2 = padding, padding + h_gif
            x1, x2 = target_frame.shape[1] - w_gif - padding, target_frame.shape[1] - padding

            # Alpha blending
            alpha_gif = gif_frame[:, :, 3] / 255.0
            alpha_frame = 1.0 - alpha_gif
            for c in range(0, 3):
                target_frame[y1:y2, x1:x2, c] = alpha_gif * gif_frame[:, :, c] + alpha_frame * target_frame[y1:y2, x1:x2, c]

intro_gif = GIFObject("./assets/cropped_ergonomics.gif")

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
            dist_diff = abs(nose_shoulder_dist - ref_nose_shoulder_dist)
            good_posture = dist_diff < 0.02  # threshold for good posture
            current_status = "GOOD POSTURE" if good_posture else "BAD POSTURE"

            if current_status != stable_status:
                if statuschange_starttime is None:
                    statuschange_starttime = time.time()
                elif time.time() - statuschange_starttime > statuschange_delay:
                    stable_status = current_status
                    statuschange_starttime = None
            else:
                statuschange_starttime = None
            status = stable_status
        else:
            status = "PRESS 'C' TO CALIBRATE"
        
        color = (0,255,0) if (calibrated and status == "GOOD POSTURE") else (0,0,255) if (calibrated and status == "BAD POSTURE") else (255,255,0)
        
        # Draw visual feedback
        cv2.line(frame, L_px, R_px, color, 3)  # shoulder line
        cv2.line(frame, neck_px, nose_px, color, 2)  # neck line
        cv2.circle(frame, nose_px, 8, color, -1)  # nose point
        cv2.putText(frame, status, (20,50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, f"Nose-Shoulder Dist: {nose_shoulder_dist:.3f}", (20,90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
        if calibrated:
            cv2.putText(frame, "Press 'R' to recalibrate", (20,130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

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
            shoulder_y = (L.y + R.y) / 2
            ref_nose_shoulder_dist = abs(nose.y - shoulder_y)
            calibrated = True
            print("Calibrated! Current posture set as reference.")
cap.release(); cv2.destroyAllWindows()