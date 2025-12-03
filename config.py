HEIGHT = 400
WIDTH =  600
BUTTON_W, BUTTON_H = 50, 50
PADDING = 20


# GIF Setup
gif_holder = {
    "intro": "./assets/cropped_ergonomics.gif",
    "bad": "./assets/car.gif",
    "good": "./assets/dance.gif",
    "wrench": "./assets/wrench.png",
}
ref_values ={
        "ref_nose_z": None,
        "ref_shoulder_z": None,
        "ref_shoulder_y": None,
        "ref_nose_shoulder_dist": None,
        "calibrated" : False
    }

sounds = {
    "bad": "./assets/laugh.mp3",
    "good": "./assets/placeholder.mp3"
}