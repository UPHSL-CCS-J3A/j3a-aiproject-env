import cv2, mediapipe as mp, math
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

# Calibration variables
ref_nose_shoulder_dist = None
calibrated = False

while True:
    ret, frame = cap.read()
    if not ret: break
    h, w = frame.shape[:2]
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = pose.process(img)
    
    if res.pose_landmarks:
        # Draw pose landmarks
        mp_draw.draw_landmarks(frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        lm = res.pose_landmarks.landmark
        # Get key points
        L = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
        R = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        nose = lm[mp_pose.PoseLandmark.NOSE]
        
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
            dist_diff = abs(nose_shoulder_dist - ref_nose_shoulder_dist)
            good_posture = dist_diff < 0.02  # threshold for good posture
            status = "GOOD POSTURE" if good_posture else "BAD POSTURE"
        else:
            status = "PRESS 'C' TO CALIBRATE"
        
        color = (0,255,0) if (calibrated and good_posture) else (0,0,255) if calibrated else (255,255,0)
        
        # Draw visual feedback
        cv2.line(frame, L_px, R_px, color, 3)  # shoulder line
        cv2.line(frame, neck_px, nose_px, color, 2)  # neck line
        cv2.circle(frame, nose_px, 8, color, -1)  # nose point
        cv2.putText(frame, status, (20,50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, f"Nose-Shoulder Dist: {nose_shoulder_dist:.3f}", (20,90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
        if calibrated:
            cv2.putText(frame, "Press 'R' to recalibrate", (20,130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    
    cv2.imshow('Posture Detection', frame)
    key = cv2.waitKey(1)&0xFF
    if key == ord('q'): break
    elif key == ord('c') or key == ord('r'):
        if res.pose_landmarks:
            lm = res.pose_landmarks.landmark
            L = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
            R = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            nose = lm[mp_pose.PoseLandmark.NOSE]
            shoulder_y = (L.y + R.y) / 2
            ref_nose_shoulder_dist = abs(nose.y - shoulder_y)
            calibrated = True
            print("Calibrated! Current posture set as reference.")
cap.release(); cv2.destroyAllWindows()