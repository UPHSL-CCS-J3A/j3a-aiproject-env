import cv2, mediapipe as mp, time
import pygame
from GIFObject import GIFObject
from config import *


class PostureDetector:
    def __init__(self, ref_values, settings, sounds, gif_holder, app):
        self.gif_holder = {
            key: GIFObject(path) for key, path in gif_holder.items()
        }
        self.sounds = {
            key: pygame.mixer.Sound(path) for key, path in sounds.items()
        }
        self.ref_values = ref_values
        self.settings = settings
        self.app = app
        self.running = True

        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.cap = cv2.VideoCapture(0)
        self.params = {"button_rect": [0,0,0,0]}
        
        self.stable_status = "GOOD POSTURE"
        self.stable_action = "GOOD DISTANCE"
        self.statuschange_delay = 2
        self.statuschange_starttime = None
        self.prev_status = self.stable_status
        self.action = self.stable_action
        cv2.namedWindow("Posture Detection")
        cv2.setMouseCallback("Posture Detection", self._click_event, param=self.params)

    def _click_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print("Clicked")
            bx, by, bw, bh = param["button_rect"]
            if bx <= x <= bx + bw and by <= y <= by + bh:
                self.settings.spawn()

    def update_gif(self, key, new_path):
        self.gif_holder[key] = GIFObject(new_path)

    def update_sound(self, key, new_path):
        self.sounds[key] = pygame.mixer.Sound(new_path)

    def process_frame(self):
        if not self.running:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            self.stop()
            return
        
        h, w = frame.shape[:2]
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.pose.process(img)
        
        if res.pose_landmarks:
            self.mp_draw.draw_landmarks(frame, res.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            lm = res.pose_landmarks.landmark
            
            L = lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            R = lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            nose = lm[self.mp_pose.PoseLandmark.NOSE]
            L_px = (int(L.x*w), int(L.y*h))
            R_px = (int(R.x*w), int(R.y*h))
            nose_px = (int(nose.x*w), int(nose.y*h))
            neck_px = ((L_px[0]+R_px[0])//2, (L_px[1]+R_px[1])//2)
            
            shoulder_y = (L.y + R.y) / 2
            nose_shoulder_dist = abs(nose.y - shoulder_y)
            
            if self.ref_values["calibrated"]:
                scale_factor = shoulder_y / self.ref_values["ref_shoulder_y"]
                dist_diff = nose_shoulder_dist - self.ref_values["ref_nose_shoulder_dist"] * scale_factor
                nose_depth_diff = nose.z - self.ref_values["ref_nose_z"]
                good_posture = abs(dist_diff) < 0.02 * scale_factor
                current_status = "GOOD POSTURE" if good_posture else "BAD POSTURE"
                current_action = "MOVE FARTHER FROM CAMERA" if nose_depth_diff < -0.5 else "CHIN UP" if (dist_diff < 0.01 * scale_factor) else "CHIN DOWN" if (dist_diff > 0.03 * scale_factor) else "GOOD DISTANCE"
                if current_status != self.stable_status:
                    if self.statuschange_starttime is None:
                        self.statuschange_starttime = time.time()
                    elif time.time() - self.statuschange_starttime > self.statuschange_delay:
                        self.stable_status = current_status
                        self.statuschange_starttime = None
                else:
                    self.statuschange_starttime = None
                status = self.stable_status
                self.action = current_action
            else:
                status = "PRESS 'C' TO CALIBRATE"
            
            color = (0,255,0) if (self.ref_values["calibrated"] and status == "GOOD POSTURE") else (0,0,255) if (self.ref_values["calibrated"] and status == "BAD POSTURE") else (255,255,0)
            if status == "BAD POSTURE":
                self.gif_holder["bad"].overlay_next_frame(frame)
                if self.prev_status != "BAD POSTURE":
                    print("Plays Music")
                    pygame.mixer.stop()
                    self.sounds["bad"].play(loops=-1)
            elif status == "GOOD POSTURE":
                self.gif_holder["good"].overlay_next_frame(frame)
                if self.prev_status != "GOOD POSTURE":
                    pygame.mixer.stop()
                    self.sounds["good"].play(loops=-1)
            self.prev_status = status
            
            base_y = 50
            cv2.line(frame, L_px, R_px, color, 3)
            cv2.line(frame, neck_px, nose_px, color, 2)
            cv2.circle(frame, nose_px, 8, color, -1)
            cv2.putText(frame, status, (20, base_y), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame, f"Nose-Shoulder Dist: {nose_shoulder_dist:.3f}", (20,base_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
            
            bx = w - BUTTON_W - PADDING + 8
            by = h - BUTTON_H - PADDING + 8
            button_rect = [bx, by, BUTTON_W, BUTTON_H]
            self.params["button_rect"] = button_rect

            cv2.rectangle(frame, (bx, by), (bx + BUTTON_W, by + BUTTON_H), (0, 200, 0), -1)
            self.gif_holder["wrench"].overlay_next_frame(frame, position = 'lower-right', size=(50,50))
            if self.ref_values["calibrated"]:
                cv2.putText(frame, f"Reference Nose-Shoulder Dist: {self.ref_values["ref_nose_shoulder_dist"]:.3f}", (20,base_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,255,0), 1)
                cv2.putText(frame, "Press 'R' to recalibrate", (20,base_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
                cv2.putText(frame, self.action, (20, base_y + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            if not self.ref_values["calibrated"]:
                self.gif_holder["intro"].overlay_next_frame(frame, 0.65)

        cv2.imshow('Posture Detection', frame)
        key = cv2.waitKey(1)&0xFF
        if key == ord('q'):
            self.stop()
        elif key == ord('c') or key == ord('r'):
            if res.pose_landmarks:
                lm = res.pose_landmarks.landmark
                L = lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
                R = lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
                nose = lm[self.mp_pose.PoseLandmark.NOSE]
                shoulder_y = (L.y + R.y) / 2
                self.ref_values["ref_nose_z"] = nose.z
                self.ref_values["ref_shoulder_z"] = (L.z + R.z) / 2
                self.ref_values["ref_shoulder_y"] = (L.y + R.y) / 2
                self.ref_values["ref_nose_shoulder_dist"] = abs(nose.y - shoulder_y)
                self.ref_values["calibrated"] = True
                print("Calibrated! Current posture set as reference.")
        
        self.app.after(1, self.process_frame)
    
    def start(self):
        self.running = True
        self.process_frame()
    
    def stop(self):
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()
        self.app.destroy()
