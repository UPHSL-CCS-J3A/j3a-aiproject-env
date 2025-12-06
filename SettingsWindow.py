"""Settings window for configuring posture detection assets and calibration."""

import pygame
import customtkinter as ctk
import os
from tkinter import filedialog
from PIL import Image
import json
from config import WIDTH, HEIGHT, AUDIO_LABELS, IMAGE_LABELS, AUDIO_KEYS, GIF_KEYS


class SettingsWindow:
    """Manages the settings UI for audio, images, and calibration."""
    
    def __init__(self, sounds, gif_holder, ref_values, app, title="Settings"):
        """Initialize the settings window.
        
        Args:
            sounds: Dictionary of sound file paths
            gif_holder: Dictionary of GIF file paths
            ref_values: Dictionary containing calibration reference values
            app: Main CTk application instance
            title: Window title
        """
        self.title = title
        self.width = WIDTH
        self.height = HEIGHT
        self.window = None

        # Store references to shared data
        self.sounds = sounds
        self.gif_holder = gif_holder
        self.ref_values = ref_values
        self.app = app
        
        # UI widget references
        self.preview_labels = []
        self.filename_labels = []
        self.audio_labels = []
        
        # Audio playback channel
        self.channel = pygame.mixer.Channel(1)
        
        # Data storage
        self.calibration_data = None
        self.settings_data = None

    # ========================================================================
    # WINDOW MANAGEMENT
    # ========================================================================
    
    def spawn(self):
        """Open the settings window if not already open."""
        if self.window is None or not self.window.winfo_exists():
            self.app.after(0, self._build_ui)

    def attach_detector(self, detector):
        """Attach the posture detector instance for updates."""
        self.detector = detector
    
    # ========================================================================
    # UI CONSTRUCTION
    # ========================================================================
    
    def _build_ui(self):
        """Build the complete settings UI."""
        self._build_window()
        self._build_scroll_area()
        self._build_audio_section()
        self._build_import_section()
        self._build_image_section()
        self._build_close_button()

    def _build_window(self):
        """Create the main settings window."""
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
        """Create the scrollable content area."""
        self.scrollable_frame = ctk.CTkScrollableFrame(self.window, width=580, height=320)
        self.scrollable_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.main_content_frame = ctk.CTkFrame(self.scrollable_frame, bg_color='gray')
        self.main_content_frame.pack(pady=10, anchor="n")

        self.left_side_frame = ctk.CTkFrame(self.main_content_frame)
        self.left_side_frame.pack(side="left", padx=20, pady=10, anchor='n')
    
    def _build_audio_section(self):
        """Build the audio file selection section."""
        audio_frame = ctk.CTkFrame(self.left_side_frame)
        audio_frame.pack(anchor='n')

        ctk.CTkLabel(
            audio_frame,
            text="Audio Files",
            font=ctk.CTkFont(size=13),
            bg_color="#cfcfcf"
        ).pack(fill='x', pady=5)

        content = ctk.CTkFrame(audio_frame, fg_color="#dbdbdb")
        content.pack()

        self.audio_labels = []
        for i in range(2):
            # Select button
            ctk.CTkButton(
                content,
                text=f"Select {AUDIO_LABELS[i]}",
                width=200,
                command=lambda x=i: self.select_audio(x),
                bg_color='#dbdbdb'
            ).grid(row=i*2, column=0, padx=5, pady=(5, 0))

            # Play button
            ctk.CTkButton(
                content,
                text="Play",
                width=60,
                command=lambda x=i: self.play_audio(x),
                bg_color='#dbdbdb'
            ).grid(row=i*2, column=1, padx=3)

            # Stop button
            ctk.CTkButton(
                content,
                text="Stop",
                width=60,
                command=self.stop_audio,
                bg_color='#dbdbdb'
            ).grid(row=i*2, column=2, padx=3)

            # Filename label
            audio_key = AUDIO_KEYS[i]
            base = os.path.basename(self.sounds[audio_key])
            label = ctk.CTkLabel(
                content,
                text=f"{AUDIO_LABELS[i]} Loaded: {base}",
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            label.grid(row=i*2+1, column=0, columnspan=3, sticky="w", padx=5, pady=(0, 5))
            self.audio_labels.append(label)
    
    def _build_import_section(self):
        """Build the calibration and settings import/export section."""
        import_frame = ctk.CTkFrame(self.left_side_frame)
        import_frame.pack(anchor='n', pady=10, fill='x')

        ctk.CTkLabel(
            import_frame,
            text="Import Files",
            font=ctk.CTkFont(size=13),
            bg_color="#cfcfcf"
        ).pack(fill='x')

        # Calibration section
        self.calibration_lbl = ctk.CTkLabel(import_frame, text="Calibration File:")
        self.calibration_lbl.pack(pady=3)

        cal_frame = ctk.CTkFrame(import_frame, fg_color="#dbdbdb")
        cal_frame.pack()

        ctk.CTkButton(
            cal_frame,
            text="Import",
            width=100,
            command=self.load_calibration
        ).pack(side='left', pady=5, padx=10)

        ctk.CTkButton(
            cal_frame,
            text="Save",
            width=100,
            command=self.save_calibration
        ).pack(side='left', pady=5, padx=10)

        # Settings section
        self.settings_lbl = ctk.CTkLabel(import_frame, text="Settings File:")
        self.settings_lbl.pack(pady=3)

        set_frame = ctk.CTkFrame(import_frame, fg_color="#dbdbdb")
        set_frame.pack()

        ctk.CTkButton(
            set_frame,
            text="Import",
            width=100,
            command=self.load_settings
        ).pack(side='left', pady=5, padx=10)

        ctk.CTkButton(
            set_frame,
            text="Save",
            width=100,
            command=self.save_settings
        ).pack(side='left', pady=5, padx=10)
    
    def _build_image_section(self):
        """Build the image/GIF selection section."""
        image_frame = ctk.CTkFrame(self.main_content_frame)
        image_frame.pack(side="left", padx=20, pady=10, anchor='n')

        ctk.CTkLabel(
            image_frame,
            text="Images (GIF/PNG)",
            font=ctk.CTkFont(size=13)
        ).pack(pady=5)

        content = ctk.CTkFrame(image_frame)
        content.pack()

        self.preview_labels = []
        self.filename_labels = []

        for i in range(3):
            # Select button
            ctk.CTkButton(
                content,
                text=f"Select Image {i+1}",
                width=120,
                command=lambda x=i: self.select_image(x)
            ).grid(row=i*2, column=0, padx=5, pady=(5, 0))

            # Preview label
            preview = ctk.CTkLabel(
                content,
                text="[Preview]",
                fg_color="#ddd",
                width=120,
                height=80
            )
            preview.grid(row=i*2, column=1, padx=10, pady=(5, 0))
            self.preview_labels.append(preview)

            # Filename label
            label = ctk.CTkLabel(
                content,
                text=IMAGE_LABELS[i],
                font=ctk.CTkFont(size=10),
                anchor="w"
            )
            label.grid(row=i*2+1, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 5))
            self.filename_labels.append(label)

        # Load default previews
        self._load_default_previews()
    
    def _load_default_previews(self):
        """Load preview images for default GIF files."""
        for i, key in enumerate(GIF_KEYS):
            try:
                path = self.gif_holder[key]
                self.show_preview(i, path)
                fname = os.path.basename(path)
                self.filename_labels[i].configure(text=f"{IMAGE_LABELS[i]} : {fname}")
            except Exception as e:
                print(f"Image preview error: {e}")
    
    def _build_close_button(self):
        """Build the close button."""
        close_frame = ctk.CTkFrame(self.scrollable_frame)
        close_frame.pack(pady=10)

        ctk.CTkButton(
            close_frame,
            text="Close",
            width=200,
            command=self.window.destroy
        ).pack()

    # ========================================================================
    # AUDIO FUNCTIONS
    # ========================================================================

    def select_audio(self, index):
        """Open file dialog to select an audio file."""
        path = filedialog.askopenfilename(
            title="Select audio file",
            filetypes=[("Audio Files", "*.mp3 *.wav")]
        )
        
        if path:
            audio_key = AUDIO_KEYS[index]
            self.sounds[audio_key] = path
            self.detector.update_sound(audio_key, path)
            
            base_filename = os.path.basename(path)
            self.audio_labels[index].configure(
                text=f"{AUDIO_LABELS[index]} Loaded: {base_filename}"
            )
            print(f"Loaded audio {index+1}: {path}")

    def play_audio(self, index):
        """Play the selected audio file."""
        audio_key = AUDIO_KEYS[index]
        file = self.sounds[audio_key]
        
        if file:
            try:
                sound = pygame.mixer.Sound(file)
                self.channel.play(sound)
            except Exception as e:
                print(f"Error playing audio: {e}")

    def stop_audio(self):
        """Stop audio playback."""
        self.channel.stop()

    # ========================================================================
    # IMAGE FUNCTIONS
    # ========================================================================

    def select_image(self, index):
        """Open file dialog to select an image/GIF file."""
        path = filedialog.askopenfilename(
            title="Select image",
            filetypes=[("Image Files", "*.gif *.png")]
        )
        
        if path:
            gif_key = GIF_KEYS[index]
            self.gif_holder[gif_key] = path
            self.detector.update_gif(gif_key, path)
            self.show_preview(index, path)
            
            filename = os.path.basename(path)
            self.filename_labels[index].configure(
                text=f"{IMAGE_LABELS[index]} : {filename}"
            )

    def show_preview(self, index, filepath):
        """Display a preview of the selected image."""
        img = Image.open(filepath)
        img.thumbnail((100, 100))

        preview_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
        self.preview_labels[index].configure(image=preview_img, text="")
        self.preview_labels[index].image = preview_img
    
    # ========================================================================
    # CALIBRATION FUNCTIONS
    # ========================================================================
    
    def save_calibration(self):
        """Save current calibration data to a JSON file."""
        if not self.calibration_data:
            print("No calibration data to save!")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Save Calibration"
        )
        
        if path:
            with open(path, "w") as f:
                json.dump(self.calibration_data, f, indent=4)
            print(f"Calibration saved to {path}")
            self.calibration_lbl.configure(
                text=f"Calibration File: {os.path.basename(path)}"
            )
    
    def load_calibration(self):
        """Load calibration data from a JSON file."""
        path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            title="Load Calibration"
        )
        
        if path:
            with open(path, "r") as f:
                self.calibration_data = json.load(f)
            
            # Apply calibration to ref_values
            self.ref_values["ref_nose_z"] = self.calibration_data["ref_nose_z"]
            self.ref_values["ref_shoulder_z"] = self.calibration_data["ref_shoulder_z"]
            self.ref_values["ref_shoulder_y"] = self.calibration_data["ref_shoulder_y"]
            self.ref_values["ref_nose_shoulder_dist"] = self.calibration_data["ref_nose_shoulder_dist"]
            self.ref_values["calibrated"] = True
            
            print(f"Calibration loaded from {path}")
            self.calibration_lbl.configure(
                text=f"Calibration File: {os.path.basename(path)}"
            )
    
    # ========================================================================
    # SETTINGS FUNCTIONS
    # ========================================================================
    
    def save_settings(self):
        """Save current settings (audio and images) to a JSON file."""
        settings_data = {
            "images": [self.gif_holder[key] for key in GIF_KEYS],
            "audio": [self.sounds[key] for key in AUDIO_KEYS]
        }

        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Save Settings"
        )
        
        if path:
            with open(path, "w") as f:
                json.dump(settings_data, f, indent=4)
            print(f"Settings saved to {path}")
            self.settings_lbl.configure(
                text=f"Settings File: {os.path.basename(path)}"
            )
    
    def load_settings(self):
        """Load settings (audio and images) from a JSON file."""
        path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            title="Load Settings"
        )
        
        if path:
            with open(path, "r") as f:
                loaded = json.load(f)

            # Load audio files
            audio_files = loaded.get("audio", [self.sounds[key] for key in AUDIO_KEYS])
            for i, audio_path in enumerate(audio_files):
                audio_key = AUDIO_KEYS[i]
                self.sounds[audio_key] = audio_path
                self.detector.update_sound(audio_key, audio_path)
                
                base_filename = os.path.basename(audio_path)
                self.audio_labels[i].configure(
                    text=f"{AUDIO_LABELS[i]} Loaded: {base_filename}"
                )
            
            # Load image files
            image_files = loaded.get("images", [self.gif_holder[key] for key in GIF_KEYS])
            for i, image_path in enumerate(image_files):
                gif_key = GIF_KEYS[i]
                self.gif_holder[gif_key] = image_path
                self.detector.update_gif(gif_key, image_path)
                self.show_preview(i, image_path)
                
                filename = os.path.basename(image_path)
                self.filename_labels[i].configure(
                    text=f"{IMAGE_LABELS[i]} : {filename}"
                )
            
            print(f"Settings loaded from {path}")
            self.settings_lbl.configure(
                text=f"Settings File: {os.path.basename(path)}"
            )
