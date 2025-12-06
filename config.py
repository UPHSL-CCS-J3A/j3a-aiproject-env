"""Configuration file for Posture Detection System."""

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
gif_holder = {
    "intro": "./assets/cropped_ergonomics.gif",
    "bad": "./assets/car.gif",
    "good": "./assets/dance.gif",
    "wrench": "./assets/wrench.png",
}

sounds = {
    "bad": "./assets/laugh.mp3",
    "good": "./assets/placeholder.mp3"
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