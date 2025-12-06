"""Real-time posture detection using MediaPipe Pose and OpenCV."""

import cv2
import mediapipe as mp
import time
import pygame
from threading import Thread, Lock
from GIFObject import GIFObject
from config import (
    BUTTON_W, BUTTON_H, PADDING,
    GOOD_POSTURE_THRESHOLD, CHIN_UP_THRESHOLD, CHIN_DOWN_THRESHOLD,
    CAMERA_DISTANCE_THRESHOLD, STATUS_CHANGE_DELAY
)


class PostureDetector:
    """Detects and monitors user posture in real-time using webcam."""
    
    def __init__(self, ref_values, settings, sounds, gif_holder, app):
        """Initialize the posture detector.
        
        Args:
            ref_values: Dictionary containing calibration reference values
            settings: SettingsWindow instance for configuration
            sounds: Dictionary of sound file paths
            gif_holder: Dictionary of GIF file paths
            app: Main CTk application instance
        """
        # Initialize GIF objects
        self.gif_holder = {
            key: GIFObject(path) for key, path in gif_holder.items()
        }
        
        # Initialize sound objects
        self.sounds = {
            key: pygame.mixer.Sound(path) for key, path in sounds.items()
        }
        
        # Store references
        self.ref_values = ref_values
        self.settings = settings
        self.app = app
        self.running = True
        self.lock = Lock()
        self.cv_thread = None

        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        
        # UI parameters
        self.params = {"button_rect": [0, 0, 0, 0]}
        
        # Posture state tracking
        self.stable_status = "GOOD POSTURE"
        self.stable_action = "GOOD DISTANCE"
        self.statuschange_starttime = None
        self.prev_status = self.stable_status
        self.action = self.stable_action

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================
    
    def _click_event(self, event, x, y, flags, param):
        """Handle mouse click events on the OpenCV window."""
        if event == cv2.EVENT_LBUTTONDOWN:
            bx, by, bw, bh = param["button_rect"]
            if bx <= x <= bx + bw and by <= y <= by + bh:
                self.settings.spawn()

    # ========================================================================
    # ASSET UPDATE METHODS
    # ========================================================================
    
    def update_gif(self, key, new_path):
        """Update a GIF asset with a new file path."""
        self.gif_holder[key] = GIFObject(new_path)

    def update_sound(self, key, new_path):
        """Update a sound asset with a new file path."""
        self.sounds[key] = pygame.mixer.Sound(new_path)

    # ========================================================================
    # POSTURE ANALYSIS
    # ========================================================================
    
    def _calculate_posture_status(self, nose, shoulder_y, nose_shoulder_dist):
        """Calculate current posture status and recommended action.
        
        Args:
            nose: MediaPipe nose landmark
            shoulder_y: Average Y position of shoulders
            nose_shoulder_dist: Distance between nose and shoulders
            
        Returns:
            tuple: (status, action) strings
        """
        if not self.ref_values["calibrated"]:
            return "PRESS 'C' TO CALIBRATE", "GOOD DISTANCE"
        
        # Calculate scale factor based on distance from camera
        scale_factor = shoulder_y / self.ref_values["ref_shoulder_y"]
        dist_diff = nose_shoulder_dist - self.ref_values["ref_nose_shoulder_dist"] * scale_factor
        nose_depth_diff = nose.z - self.ref_values["ref_nose_z"]
        
        # Determine posture quality
        good_posture = abs(dist_diff) < GOOD_POSTURE_THRESHOLD * scale_factor
        current_status = "GOOD POSTURE" if good_posture else "BAD POSTURE"
        
        # Determine recommended action
        if nose_depth_diff < CAMERA_DISTANCE_THRESHOLD:
            current_action = "MOVE FARTHER FROM CAMERA"
        elif dist_diff < CHIN_UP_THRESHOLD * scale_factor:
            current_action = "CHIN UP"
        elif dist_diff > CHIN_DOWN_THRESHOLD * scale_factor:
            current_action = "CHIN DOWN"
        else:
            current_action = "GOOD DISTANCE"
        
        # Apply status change delay to prevent flickering
        if current_status != self.stable_status:
            if self.statuschange_starttime is None:
                self.statuschange_starttime = time.time()
            elif time.time() - self.statuschange_starttime > STATUS_CHANGE_DELAY:
                self.stable_status = current_status
                self.statuschange_starttime = None
        else:
            self.statuschange_starttime = None
        
        return self.stable_status, current_action

    def _handle_audio_feedback(self, status):
        """Play appropriate audio feedback based on posture status."""
        if status == "BAD POSTURE" and self.prev_status != "BAD POSTURE":
            pygame.mixer.stop()
            self.sounds["bad"].play(loops=-1)
        elif status == "GOOD POSTURE" and self.prev_status != "GOOD POSTURE":
            pygame.mixer.stop()
            self.sounds["good"].play(loops=-1)
        self.prev_status = status

    def _get_status_color(self, status):
        """Get the color for the current posture status."""
        if self.ref_values["calibrated"]:
            return (0, 255, 0) if status == "GOOD POSTURE" else (0, 0, 255)
        return (255, 255, 0)

    # ========================================================================
    # RENDERING
    # ========================================================================
    
    def _draw_pose_overlay(self, frame, L_px, R_px, nose_px, neck_px, color):
        """Draw pose landmarks and connections on the frame."""
        cv2.line(frame, L_px, R_px, color, 3)  # Shoulder line
        cv2.line(frame, neck_px, nose_px, color, 2)  # Neck line
        cv2.circle(frame, nose_px, 8, color, -1)  # Nose point

    def _draw_status_text(self, frame, status, nose_shoulder_dist, base_y, color):
        """Draw status information text on the frame."""
        cv2.putText(frame, status, (20, base_y), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(
            frame,
            f"Nose-Shoulder Dist: {nose_shoulder_dist:.3f}",
            (20, base_y + 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1
        )
        
        if self.ref_values["calibrated"]:
            cv2.putText(
                frame,
                f"Reference Nose-Shoulder Dist: {self.ref_values['ref_nose_shoulder_dist']:.3f}",
                (20, base_y + 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 255, 0),
                1
            )
            cv2.putText(
                frame,
                "Press 'R' to recalibrate",
                (20, base_y + 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
            cv2.putText(
                frame,
                self.action,
                (20, base_y + 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1
            )

    def _draw_settings_button(self, frame, w, h):
        """Draw the settings button in the lower-right corner."""
        bx = w - BUTTON_W - PADDING + 8
        by = h - BUTTON_H - PADDING + 8
        self.params["button_rect"] = [bx, by, BUTTON_W, BUTTON_H]
        
        cv2.rectangle(frame, (bx, by), (bx + BUTTON_W, by + BUTTON_H), (0, 200, 0), -1)
        self.gif_holder["wrench"].overlay_next_frame(frame, position='lower-right', size=(50, 50))

    # ========================================================================
    # CALIBRATION
    # ========================================================================
    
    def _calibrate(self, landmarks):
        """Calibrate the reference posture from current pose landmarks."""
        lm = landmarks.landmark
        L = lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        R = lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        nose = lm[self.mp_pose.PoseLandmark.NOSE]
        
        shoulder_y = (L.y + R.y) / 2
        self.ref_values["ref_nose_z"] = nose.z
        self.ref_values["ref_shoulder_z"] = (L.z + R.z) / 2
        self.ref_values["ref_shoulder_y"] = shoulder_y
        self.ref_values["ref_nose_shoulder_dist"] = abs(nose.y - shoulder_y)
        self.ref_values["calibrated"] = True
        print("Calibrated! Current posture set as reference.")

    # ========================================================================
    # MAIN PROCESSING LOOP
    # ========================================================================
    
    def _cv_loop(self):
        """OpenCV processing loop running in separate thread."""
        # Setup OpenCV window in the thread
        cv2.namedWindow("Posture Detection")
        cv2.setMouseCallback("Posture Detection", self._click_event, param=self.params)
        
        while self.running:
            # Capture frame
            ret, frame = self.cap.read()
            if not ret:
                break
            
            h, w = frame.shape[:2]
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = self.pose.process(img)
            
            if res.pose_landmarks:
                # Draw pose landmarks
                self.mp_draw.draw_landmarks(frame, res.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                lm = res.pose_landmarks.landmark
                
                # Extract key landmarks
                L = lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
                R = lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
                nose = lm[self.mp_pose.PoseLandmark.NOSE]
                
                # Convert to pixel coordinates
                L_px = (int(L.x * w), int(L.y * h))
                R_px = (int(R.x * w), int(R.y * h))
                nose_px = (int(nose.x * w), int(nose.y * h))
                neck_px = ((L_px[0] + R_px[0]) // 2, (L_px[1] + R_px[1]) // 2)
                
                # Calculate posture metrics
                shoulder_y = (L.y + R.y) / 2
                nose_shoulder_dist = abs(nose.y - shoulder_y)
                
                # Determine posture status
                with self.lock:
                    status, self.action = self._calculate_posture_status(nose, shoulder_y, nose_shoulder_dist)
                    color = self._get_status_color(status)
                
                # Handle audio feedback
                self._handle_audio_feedback(status)
                
                # Overlay GIF based on status
                if status == "BAD POSTURE":
                    self.gif_holder["bad"].overlay_next_frame(frame)
                elif status == "GOOD POSTURE":
                    self.gif_holder["good"].overlay_next_frame(frame)
                
                # Draw visual feedback
                self._draw_pose_overlay(frame, L_px, R_px, nose_px, neck_px, color)
                self._draw_status_text(frame, status, nose_shoulder_dist, 50, color)
                self._draw_settings_button(frame, w, h)
                
                # Show intro GIF if not calibrated
                if not self.ref_values["calibrated"]:
                    self.gif_holder["intro"].overlay_next_frame(frame, 0.65)

            # Display frame
            cv2.imshow('Posture Detection', frame)
            
            # Process OpenCV window events
            key = cv2.waitKey(1) & 0xFF
            
            # Handle keyboard input
            if key == ord('q'):
                self.running = False
                break
            elif key in [ord('c'), ord('r')]:
                if res.pose_landmarks:
                    with self.lock:
                        self._calibrate(res.pose_landmarks)
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        self.app.after(0, self.app.destroy)
    
    # ========================================================================
    # LIFECYCLE METHODS
    # ========================================================================
    
    def start(self):
        """Start the posture detection loop in a separate thread."""
        self.running = True
        self.cv_thread = Thread(target=self._cv_loop, daemon=True)
        self.cv_thread.start()
    
    def stop(self):
        """Stop the posture detection and cleanup resources."""
        self.running = False
        if self.cv_thread and self.cv_thread.is_alive():
            self.cv_thread.join(timeout=1.0)
