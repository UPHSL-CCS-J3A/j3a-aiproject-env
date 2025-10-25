# Real-Time Posture Detection System

[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=21282326&assignment_repo_type=AssignmentRepo)

### Problem Description
Poor posture has become a widespread issue due to prolonged sitting and computer usage among students and professionals. Continuous slouching or improper body alignment leads to musculoskeletal problems, including neck strain, back pain, and fatigue. Traditional posture correction methods—such as wearable devices or manual observation—can be expensive, intrusive, or unreliable.  
This project aims to address these limitations by providing a camera-based, real-time AI solution that monitors posture non-intrusively and gives immediate feedback.

---

### Proposed Solution Overview
The **Real-Time Posture Detection System** is a computer vision-based AI application that uses a webcam and MediaPipe’s pose estimation technology to detect and evaluate the user’s posture.  
It identifies key body landmarks (such as the nose, shoulders, and spine) and measures vertical distances between them. By comparing the live measurements with a calibrated reference posture, the system classifies the user’s posture as good or poor. Visual indicators on the screen provide instant feedback to help users correct their posture in real time.

---

### PEAS Model

| **Component** | **Description** |
|----------------|-----------------|
| **Performance Measure** | Accuracy of posture detection, response time for visual feedback, and reduced time spent in poor posture |
| **Environment** | Physical environment using a webcam connected to a computer; operates in real time via a virtual interface |
| **Actuators** | Visual indicators on screen (color-coded status), calibration controls, and potential audio feedback |
| **Sensors** | Webcam for live video capture; pose estimation detects nose and shoulder landmarks using MediaPipe |

---

### AI Concepts Used

| **AI Concept** | **Implementation and Justification** |
|----------------|--------------------------------------|
| **Intelligent Agent Type** | Model-based reflex agent – reacts instantly to posture deviations based on visual data and calibration reference |
| **Search or Optimization Strategy** | Uses optimization in pose landmark tracking and distance calculation to ensure stable and accurate keypoint detection |
| **Learning or Decision Component** | Employs supervised calibration logic that learns the user’s ideal posture reference; applies decision rules for good or bad posture detection |

---

### System Architecture Diagram 

```
┌────────────────────────────┐
│ Camera Input               │
│ (Webcam / Video Stream)    │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ MediaPipe Pose Detection   │
│ (Keypoint Landmark Capture)│
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Distance Calculation        │
│ (Nose-to-Shoulder Metric)   │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Posture Evaluation          │
│ (Compare vs Calibration)    │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Visual Feedback System      │
│ (Green = Good, Red = Bad)   │
└────────────────────────────┘
```
