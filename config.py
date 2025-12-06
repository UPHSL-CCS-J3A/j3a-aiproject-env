"""Configuration file for Posture Detection System."""

import os
import sys

# Get the correct base path for assets (works for both dev and exe)
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_PATH = sys._MEIPASS  # PyInstaller temp folder
else:
    # Running as script
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

ASSETS_PATH = os.path.join(BASE_PATH, 'assets')

# ============================================================================
# UI CONSTANTS
# ============================================================================
HEIGHT = 400
WIDTH = 600
BUTTON_W, BUTTON_H = 50, 50
PADDING = 20


# ============================================================================
# POSTURE DETECTION THRESHOLDS
# ============================================================================
GOOD_POSTURE_THRESHOLD = 0.02
CHIN_UP_THRESHOLD = 0.01
CHIN_DOWN_THRESHOLD = 0.03
CAMERA_DISTANCE_THRESHOLD = -0.5
STATUS_CHANGE_DELAY = 2  # seconds


# ============================================================================
# SETTINGS WINDOW LABELS
# ============================================================================
AUDIO_LABELS = ["Bad Posture Audio", "Good Posture Audio"]
IMAGE_LABELS = ["Intro Img", "Bad Posture Img", "Good Posture Img"]
AUDIO_KEYS = ["bad", "good"]
GIF_KEYS = ["intro", "bad", "good"]


# ============================================================================
# ASSET PATHS
# ============================================================================
def get_asset_path(filename):
    """Get the correct path for an asset file."""
    return os.path.join(ASSETS_PATH, filename)

gif_holder = {
    "intro": get_asset_path("cropped_ergonomics.gif"),
    "bad": get_asset_path("car.gif"),
    "good": get_asset_path("dance.gif"),
    "wrench": get_asset_path("wrench.png"),
}

sounds = {
    "bad": get_asset_path("laugh.mp3"),
    "good": get_asset_path("placeholder.mp3")
}


# ============================================================================
# CALIBRATION REFERENCE VALUES
# ============================================================================
ref_values = {
    "ref_nose_z": None,
    "ref_shoulder_z": None,
    "ref_shoulder_y": None,
    "ref_nose_shoulder_dist": None,
    "calibrated": False
}