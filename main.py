import pygame
import customtkinter as ctk
from SettingsWindow import SettingsWindow
from PostureDetector import PostureDetector
from config import *


pygame.mixer.init()

app = ctk.CTk()
app.withdraw()

settings = SettingsWindow(sounds=sounds, gif_holder=gif_holder, ref_values=ref_values)
posture_detector = PostureDetector(ref_values=ref_values, settings=settings, gif_holder=gif_holder, sounds=sounds, app=app)
settings.attach_detector(posture_detector)

posture_detector.start()
app.mainloop()




