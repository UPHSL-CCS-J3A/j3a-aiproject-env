"""Main entry point for Real-Time Posture Detection System."""

import pygame
import customtkinter as ctk
from SettingsWindow import SettingsWindow
from PostureDetector import PostureDetector
from config import sounds, gif_holder, ref_values


def main():
    """Initialize and run the posture detection application."""
    # Initialize audio mixer
    pygame.mixer.init()
    
    # Create main CTk application (hidden)
    app = ctk.CTk()
    app.withdraw()
    
    # Initialize settings window
    settings = SettingsWindow(
        sounds=sounds,
        gif_holder=gif_holder,
        ref_values=ref_values,
        app=app
    )
    
    # Initialize posture detector
    posture_detector = PostureDetector(
        ref_values=ref_values,
        settings=settings,
        gif_holder=gif_holder,
        sounds=sounds,
        app=app
    )
    
    # Link detector to settings
    settings.attach_detector(posture_detector)
    
    # Start posture detection
    posture_detector.start()
    
    # Run main event loop
    app.mainloop()


if __name__ == "__main__":
    main()




