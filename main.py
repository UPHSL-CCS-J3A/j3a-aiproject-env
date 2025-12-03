import cv2, mediapipe as mp, math, time
from PIL import Image, ImageTk
import numpy as np
import pygame
import customtkinter as ctk
from threading import Thread
from tkinter import filedialog
import os
import json
from GIFObject import GIFObject
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

stable_status = "GOOD POSTURE"
stable_action = "GOOD DISTANCE"
statuschange_delay = 2
statuschange_starttime = None

# Thread Function for CV
def run_posture_detection():
    global calibrated, prev_status, stable_status, statuschange_starttime, settings, ref_nose_z, ref_shoulder_z, ref_shoulder_y, ref_nose_shoulder_dist
    BUTTON_W, BUTTON_H = 50, 50
    PADDING = 20

    params = {"button_rect": [0,0,0,0]}
    cv2.namedWindow("Posture Detection")
    cv2.setMouseCallback("Posture Detection", click_event, param=params)
   
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
                gif_holder["bad"].overlay_next_frame(frame)
                if prev_status != "BAD POSTURE":
                    print("Plays Music")
                    pygame.mixer.stop()
                    sounds["bad"].play(loops=-1)
            elif status == "GOOD POSTURE":
                gif_holder["good"].overlay_next_frame(frame)
                if prev_status != "GOOD POSTURE":
                    pygame.mixer.stop()
                    sounds["good"].play(loops=-1)
            prev_status = status
            # Draw visual feedback
            base_y = 50
            cv2.line(frame, L_px, R_px, color, 3)  # shoulder line
            cv2.line(frame, neck_px, nose_px, color, 2)  # neck line
            cv2.circle(frame, nose_px, 8, color, -1)  # nose point
            cv2.putText(frame, status, (20, base_y), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame, f"Nose-Shoulder Dist: {nose_shoulder_dist:.3f}", (20,base_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
            
            # --- Compute lower-right button position ---
            bx = w - BUTTON_W - PADDING + 8
            by = h - BUTTON_H - PADDING + 8
            button_rect = [bx, by, BUTTON_W, BUTTON_H]
            params["button_rect"] = button_rect

            # --- Draw button ---
            cv2.rectangle(frame, (bx, by), (bx + BUTTON_W, by + BUTTON_H), (0, 200, 0), -1)
            wrench_png = GIFObject("./assets/wrench.png")
            wrench_png.overlay_next_frame(frame, position = 'lower-right', size=(50,50))
            if calibrated:
                cv2.putText(frame, f"Reference Nose-Shoulder Dist: {ref_nose_shoulder_dist:.3f}", (20,base_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,255,0), 1)
                cv2.putText(frame, "Press 'R' to recalibrate", (20,base_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
                cv2.putText(frame, action, (20, base_y + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            

            if not calibrated:
                gif_holder["intro"].overlay_next_frame(frame, 0.65)


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
                ref_values ={
                    "ref_nose_z": nose.z,
                    "ref_shoulder_z": (L.z + R.z) / 2,
                    "ref_shoulder_y": (L.y + R.y) / 2,
                    "ref_nose_shoulder_dist": abs(nose.y - (L.y + R.y)/2)
                }
                calibrated = True
                settings.calibration_data = ref_values
                print("Calibrated! Current posture set as reference.")
    cap.release(); cv2.destroyAllWindows()
# Calibration variables
ref_nose_shoulder_dist = None
calibrated = False
action = "GOOD DISTANCE"
# GIF Setup
gif_holder = {
    "intro": GIFObject("./assets/cropped_ergonomics.gif"),
    "bad": GIFObject("./assets/car.gif"),
    "good": GIFObject("./assets/dance.gif", 300),
}


# gif_holder["intro"] = GIFObject("./assets/cropped_ergonomics.gif")
# gif_holder["bad"] = GIFObject("./assets/car.gif")
# gif_holder["good"] = GIFObject("./assets/dance.gif", 300)

# Sound Setup
pygame.mixer.init()
sounds = {
    "bad": pygame.mixer.Sound("./assets/laugh.mp3"),
    "good": pygame.mixer.Sound("./assets/placeholder.mp3")
}
prev_status = stable_status

# Configuration Window Setup
class SettingsWindow:
    def __init__(self,sounds, gif_holder, title="Settings", width=600, height=400):
        self.title = title
        self.width = width
        self.height = height

        self.window_thread = None

        # Store file paths
        # DEFAULT FILES
        self.image_files = [
            "./assets/cropped_ergonomics.gif",   # intro
            "./assets/car.gif",                  # bad posture
            "./assets/dance.gif"                 # good posture
        ]

        self.audio_files = [
            "./assets/laugh.mp3",       # bad sound
            "./assets/placeholder.mp3"  # good sound
        ]

        self.sounds = sounds
        self.gif_holder = gif_holder
        # Store preview widgets
        self.preview_labels = []

        self.audio_labels = []  # Will store CTkLabels showing filenames
        # Audio channel
        self.channel = pygame.mixer.Channel(1)
        self.app = None
        self.calibration_data = None
        self.settings_data = None

    def spawn(self):
        """Spawn the Tkinter window in a separate thread."""
        if self.window_thread is None or not self.window_thread.is_alive():
            self.window_thread = Thread(target=self._run_window)
            self.window_thread.daemon = True
            self.window_thread.start()

    def _run_window(self):
        self._build_window()
        self._build_scroll_area()

        self._build_audio_section()
        self._build_import_section()
        self._build_image_section()
        self._build_close_button()

    def _build_window(self):
        self.window = ctk.CTkToplevel()
        self.window.title(self.title)
        self.window.geometry("800x400")
        self.window.resizable(False, False)

        ctk.CTkLabel(
            self.window, 
            text="Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=5)

    def _build_scroll_area(self):
        self.scrollable_frame = ctk.CTkScrollableFrame(self.window, width=580, height=320)
        self.scrollable_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.main_content_frame = ctk.CTkFrame(self.scrollable_frame, bg_color='gray')
        self.main_content_frame.pack(pady=10, anchor="n")

        self.left_side_frame = ctk.CTkFrame(self.main_content_frame)
        self.left_side_frame.pack(side="left", padx=20, pady=10, anchor='n')
    
    def _build_audio_section(self):
        audio_frame = ctk.CTkFrame(self.left_side_frame)
        audio_frame.pack(anchor='n')

        ctk.CTkLabel(audio_frame, text="Audio Files", font=ctk.CTkFont(size=13),
                    bg_color="#cfcfcf").pack(fill='x', pady=5)

        content = ctk.CTkFrame(audio_frame, fg_color="#dbdbdb")
        content.pack()

        self.audio_labels = []
        posture_lbl = ["Bad Posture Audio", "Good Posture Audio"]

        for i in range(2):
            ctk.CTkButton(content, text=f"Select {posture_lbl[i]}", width=200,
                        command=lambda x=i: self.select_audio(x),
                        bg_color='#dbdbdb').grid(row=i*2, column=0, padx=5, pady=(5, 0))

            ctk.CTkButton(content, text="Play", width=60,
                        command=lambda x=i: self.play_audio(x),
                        bg_color='#dbdbdb').grid(row=i*2, column=1, padx=3)

            ctk.CTkButton(content, text="Stop", width=60,
                        command=self.stop_audio,
                        bg_color='#dbdbdb').grid(row=i*2, column=2, padx=3)

            base = os.path.basename(self.audio_files[i])
            label = ctk.CTkLabel(content, text=f"{posture_lbl[i]} Loaded: {base}",
                                font=ctk.CTkFont(size=11), anchor="w")
            label.grid(row=i*2+1, column=0, columnspan=3, sticky="w", padx=5, pady=(0, 5))

            self.audio_labels.append(label)
    def _build_import_section(self):
        import_frame = ctk.CTkFrame(self.left_side_frame)
        import_frame.pack(anchor='n', pady=10, fill='x')

        ctk.CTkLabel(import_frame, text="Import Files",
                    font=ctk.CTkFont(size=13), bg_color="#cfcfcf").pack(fill='x')

        self.calibration_lbl = ctk.CTkLabel(import_frame, text="Calibration File:")
        self.calibration_lbl.pack(pady=3)

        cal_frame = ctk.CTkFrame(import_frame, fg_color="#dbdbdb")
        cal_frame.pack()

        ctk.CTkButton(cal_frame, text="Import", width=100,
                    command=self.load_calibration).pack(side='left', pady=5, padx=10)

        ctk.CTkButton(cal_frame, text="Save", width=100,
                    command=self.save_calibration).pack(side='left', pady=5, padx=10)

        self.settings_lbl = ctk.CTkLabel(import_frame, text="Settings File:")
        self.settings_lbl.pack(pady=3)

        set_frame = ctk.CTkFrame(import_frame, fg_color="#dbdbdb")
        set_frame.pack()

        ctk.CTkButton(set_frame, text="Import", width=100,
                    command=self.load_settings).pack(side='left', pady=5, padx=10)

        ctk.CTkButton(set_frame, text="Save", width=100,
                    command=self.save_settings).pack(side='left', pady=5, padx=10)
    def _build_image_section(self):
        image_frame = ctk.CTkFrame(self.main_content_frame)
        image_frame.pack(side="left", padx=20, pady=10, anchor='n')

        ctk.CTkLabel(image_frame, text="Images (GIF/PNG)",
                    font=ctk.CTkFont(size=13)).pack(pady=5)

        content = ctk.CTkFrame(image_frame)
        content.pack()

        self.preview_labels = []
        self.filename_labels = []

        posture_lbl = ["Intro Img", "Bad Posture Img", "Good Posture Img"]

        for i in range(3):
            ctk.CTkButton(content, text=f"Select Image {i+1}",
                        width=120, command=lambda x=i: self.select_image(x)
                        ).grid(row=i*2, column=0, padx=5, pady=(5, 0))

            preview = ctk.CTkLabel(content, text="[Preview]",
                                fg_color="#ddd", width=120, height=80)
            preview.grid(row=i*2, column=1, padx=10, pady=(5, 0))
            self.preview_labels.append(preview)

            label = ctk.CTkLabel(content, text=posture_lbl[i],
                                font=ctk.CTkFont(size=10), anchor="w")
            label.grid(row=i*2+1, column=0, columnspan=2,
                    sticky="w", padx=5, pady=(0, 5))
            self.filename_labels.append(label)

        # Load defaults
        for i, path in enumerate(self.image_files):
            try:
                self.show_preview(i, path)
                fname = os.path.basename(path)
                self.filename_labels[i].configure(text=f"{posture_lbl[i]} : {fname}")
            except Exception as e:
                print("Image preview error:", e)
    def _build_close_button(self):
        close_frame = ctk.CTkFrame(self.scrollable_frame)
        close_frame.pack(pady=10)

        ctk.CTkButton(close_frame, text="Close",
                    width=200,
                    command=self.window.destroy).pack()





        
    # -------------------------------------------------------
    #                   AUDIO FUNCTIONS
    # -------------------------------------------------------

    def select_audio(self, index):
        path = filedialog.askopenfilename(
            title="Select audio file",
            filetypes=[("Audio Files", "*.mp3 *.wav")]
        )
        posture_lbl = ["Bad Posture Audio", "Good Posture Audio"]
        if path:
            # Store the full path for playback
            self.audio_files[index] = path

            # Update the filename label to show only the base name
            base_filename = os.path.basename(path)
            self.audio_labels[index].configure(text=f"{posture_lbl[index]} Loaded: {base_filename}")

            print(f"Loaded audio {index+1}: {path}")
            if index == 0:
                self.sounds["bad"] = pygame.mixer.Sound(path)
            elif index == 1:
                self.sounds["good"] = pygame.mixer.Sound(path)


    def play_audio(self, index):
        file = self.audio_files[index]
        if file:
            try:
                sound = pygame.mixer.Sound(file)
                self.channel.play(sound)
            except Exception as e:
                print("Error playing audio:", e)

    def stop_audio(self):
        self.channel.stop()

    # -------------------------------------------------------
    #                   IMAGE FUNCTIONS
    # -------------------------------------------------------

    def select_image(self, index):
        path = filedialog.askopenfilename(
            title="Select image",
            filetypes=[("Image Files", "*.gif *.png")]
        )
        posture_lbl = ["Intro Img", "Bad Posture Img", "Good Posture Img"]
        if path:
            self.image_files[index] = path
            self.show_preview(index, path)
             # Update the filename label
            filename = os.path.basename(path)
            self.filename_labels[index].configure(text=f"{posture_lbl[index]} : {filename}")
            if index == 0:
                self.gif_holder["intro"] = GIFObject(path)
            elif index == 1:
                self.gif_holder["bad"] = GIFObject(path)
            elif index == 2:
                self.gif_holder["good"] = GIFObject(path)

    def show_preview(self, index, filepath):
        img = Image.open(filepath)
        img.thumbnail((100, 100))

        preview_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
        self.preview_labels[index].configure(image=preview_img, text="")
        self.preview_labels[index].image = preview_img
    
    def save_calibration(self):
        if not self.calibration_data:
            print("No calibration data to save!")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Save Calibration"
        )
        original_path = path
        if original_path:
            with open(path, "w") as f:
                json.dump(self.calibration_data, f, indent=4)
            print(f"Calibration saved to {path}")
            self.calibration_lbl.configure(text= f"Calibration File: {os.path.basename(original_path)}")

    
    def load_calibration(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            title="Load Calibration"
        )
        original_path = path
        if original_path:
            with open(path, "r") as f:
                self.calibration_data = json.load(f)
            
            # Apply calibration
            global ref_nose_z, ref_shoulder_z, ref_shoulder_y, ref_nose_shoulder_dist, calibrated
            ref_nose_z = self.calibration_data["ref_nose_z"]
            ref_shoulder_z = self.calibration_data["ref_shoulder_z"]
            ref_shoulder_y = self.calibration_data["ref_shoulder_y"]
            ref_nose_shoulder_dist = self.calibration_data["ref_nose_shoulder_dist"]
            calibrated = True
            print(f"Calibration loaded from {path}")
            self.calibration_lbl.configure(text= f"Calibration File: {os.path.basename(original_path)}")

    def save_settings(self):
        settings_data = {
            "images": self.image_files,
            "audio": self.audio_files
        }

        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Save Settings"
        )
        original_path = path
        if original_path:
            with open(path, "w") as f:
                json.dump(settings_data, f, indent=4)
            print(f"Settings saved to {path}")
            self.settings_lbl.configure(text= f"Settings File: {os.path.basename(original_path)}")
    def load_settings(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            title="Load Settings"
        )
        original_path = path
        if original_path:
            with open(path, "r") as f:
                loaded = json.load(f)

            # Load audio files
            self.audio_files = loaded.get("audio", self.audio_files)
            posture_lbl = ["Bad Posture Audio", "Good Posture Audio"]
            for i, path in enumerate(self.audio_files):
                base_filename = os.path.basename(path)
                self.audio_labels[i].configure(text=f"{posture_lbl[i]} Loaded: {base_filename}")
                if i == 0:
                    self.sounds["bad"] = pygame.mixer.Sound(path)
                elif i == 1:
                    self.sounds["good"] = pygame.mixer.Sound(path)
            # Load image files and update previews
            self.image_files = loaded.get("images", self.image_files)
            posture_lbl_img = ["Intro Img", "Bad Posture Img", "Good Posture Img"]
            for i, path in enumerate(self.image_files):
                self.show_preview(i, path)
                filename = os.path.basename(path)
                self.filename_labels[i].configure(text=f"{posture_lbl_img[i]} : {filename}")
                if i == 0:
                    self.gif_holder["intro"] = GIFObject(path)
                elif i == 1:
                    self.gif_holder["bad"] = GIFObject(path)
                elif i == 2:
                    self.gif_holder["good"] = GIFObject(path)
            print(f"Settings loaded from {path}")
            self.settings_lbl.configure(text= f"Settings File: {os.path.basename(original_path)}")




def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Clicked")
        bx, by, bw, bh = param["button_rect"]
        if bx <= x <= bx + bw and by <= y <= by + bh:
            settings.spawn()
app = ctk.CTk()
app.withdraw()
settings = SettingsWindow(sounds= sounds, gif_holder= gif_holder)
cv_thread = Thread(target=run_posture_detection, daemon=True)
cv_thread.start()

def check_thread():
    if cv_thread.is_alive():
        # Keep checking every 100 ms
        app.after(100, check_thread)
    else:
        print("CV thread finished, closing app.")
        app.destroy()  # safely terminate mainloop

# Start checking
app.after(100, check_thread)
app.mainloop()



