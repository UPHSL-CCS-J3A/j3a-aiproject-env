# Real-Time Posture Detection System

[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=21282326&assignment_repo_type=AssignmentRepo)

## Overview

A real-time computer vision application that monitors and evaluates user posture using webcam input. The system employs MediaPipe's pose estimation technology to detect body landmarks and provides immediate visual feedback on posture quality through a calibration-based approach.

## Features

- **Real-time pose detection** using MediaPipe Pose estimation
- **Calibration system** for personalized posture reference
- **Visual feedback** with color-coded status indicators
- **Live metrics display** showing nose-to-shoulder distance measurements
- **Interactive controls** for calibration and system management

## Technical Implementation

### Core Technologies
- **OpenCV**: Computer vision and video processing
- **MediaPipe**: Google's pose estimation framework
- **Python**: Primary programming language

### Algorithm Approach
The system uses a distance-based posture evaluation method:
1. Detects key body landmarks (nose, left shoulder, right shoulder)
2. Calculates vertical distance between nose and shoulder midpoint
3. Compares current measurements against calibrated reference
4. Provides real-time feedback based on deviation threshold

## Installation

### Prerequisites
- Python 3.7 or higher
- Webcam/camera device
- Windows/macOS/Linux operating system

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd j3a-aiproject-env
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## Usage Guide

### Initial Setup
1. Launch the application
2. Position yourself in front of the camera with good posture
3. Press **'C'** to calibrate your reference posture
4. The system will now monitor your posture in real-time

### Controls
| Key | Function |
|-----|----------|
| `C` | Calibrate current posture as reference |
| `R` | Recalibrate with new reference posture |
| `Q` | Quit application |

### Visual Indicators
- **Green**: Good posture (within acceptable range)
- **Red**: Poor posture (deviation detected)
- **Yellow**: Awaiting calibration

### On-Screen Information
- Current posture status
- Real-time nose-to-shoulder distance measurement
- Calibration instructions and controls

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Camera Input  │───▶│  MediaPipe Pose  │───▶│ Landmark Points │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Visual Feedback │◀───│ Posture Analysis │◀───│ Distance Calc.  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Configuration Parameters

- **Detection Confidence**: 0.5 (minimum confidence for pose detection)
- **Tracking Confidence**: 0.5 (minimum confidence for landmark tracking)
- **Posture Threshold**: 0.02 (acceptable deviation from reference)

## Development Log

Detailed development progress and technical decisions are documented in the `devlogs/` directory:
- [2025-10-25.md](devlogs/2025-10-25.md) - Initial implementation and testing

## Known Issues

- Keyboard input may not respond on certain hardware configurations
- Performance may vary based on lighting conditions and camera quality
- Requires stable camera positioning for accurate measurements

## Future Enhancements

- Audio alerts for posture correction
- Session data logging and analytics
- Multi-angle posture assessment
- Adaptive thresholding based on user characteristics
- Mobile application development

## Academic Context

This project demonstrates practical application of:
- Computer vision techniques
- Real-time image processing
- Human pose estimation
- User interface design
- Software engineering principles

## Dependencies

```
mediapipe>=0.10.0
opencv-python>=4.8.0
```

## License

This project is developed for academic purposes as part of the UPHSL CCS J3A coursework.

## Contributors

- **Student**: [Your Name]
- **Course**: CCS J3A
- **Institution**: University of Perpetual Help System Laguna
- **Academic Year**: 2024-2025

---

*For technical support or questions regarding this implementation, please refer to the development logs or contact the project maintainer.*