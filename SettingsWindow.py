from threading import Thread
import pygame
import customtkinter as ctk
import os
from tkinter import filedialog
from GIFObject import GIFObject
from PIL import Image
import json
class SettingsWindow:
    def __init__(self,sounds, gif_holder, ref_values, title="Settings", width=600, height=400):
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
        self.ref_values = ref_values
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
   
            self.ref_values["ref_nose_z"] = self.calibration_data["ref_nose_z"]
            self.ref_values["ref_shoulder_z"] = self.calibration_data["ref_shoulder_z"]
            self.ref_values["ref_shoulder_y"] = self.calibration_data["ref_shoulder_y"]
            self.ref_values["ref_nose_shoulder_dist"] = self.calibration_data["ref_nose_shoulder_dist"]
            self.ref_values["calibrated"] = True
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
