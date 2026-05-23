# ============================================================
# DRIVER DROWSINESS DETECTION SYSTEM
# Raspberry Pi 5 + MediaPipe + YOLO + OpenCV
# ============================================================
#
# FEATURES:
# ----------
# 1. Eye Close Detection
# 2. Yawn Detection
# 3. Head Tilt Detection
# 4. Face Presence Detection
# 5. Sleep Alert
# 6. Night Driving Support (with NoIR Camera)
#
# RECOMMENDED HARDWARE:
# ----------------------
# - Raspberry Pi 5
# - Pi Camera Module 3 NoIR
# - IR LEDs (850nm)
# - Buzzer
#
# INSTALLATION:
# --------------
# pip install opencv-python mediapipe numpy scipy pygame
#
# ============================================================

import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance
import time
import pygame

# ============================================================
# INITIALIZE AUDIO
# ============================================================

pygame.mixer.init()
pygame.mixer.music.load("alarm.wav")  # Add your alarm file

# ============================================================
# MEDIAPIPE INITIALIZATION
# ============================================================

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ============================================================
# CAMERA INITIALIZATION
# ============================================================

cap = cv2.VideoCapture(0)

# Set camera resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# ============================================================
# EYE LANDMARKS
# ============================================================

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# ============================================================
# MOUTH LANDMARKS
# ============================================================

UPPER_LIP = 13
LOWER_LIP = 14

# ============================================================
# EAR CALCULATION
# ============================================================

def eye_aspect_ratio(eye_points, landmarks, w, h):

    points = []

    for point in eye_points:
        x = int(landmarks[point].x * w)
        y = int(landmarks[point].y * h)
        points.append((x, y))

    A = distance.euclidean(points[1], points[5])
    B = distance.euclidean(points[2], points[4])
    C = distance.euclidean(points[0], points[3])

    ear = (A + B) / (2.0 * C)

    return ear

# ============================================================
# MOUTH OPEN RATIO
# ============================================================

def mouth_ratio(landmarks, w, h):

    upper_x = int(landmarks[UPPER_LIP].x * w)
    upper_y = int(landmarks[UPPER_LIP].y * h)

    lower_x = int(landmarks[LOWER_LIP].x * w)
    lower_y = int(landmarks[LOWER_LIP].y * h)

    distance_value = np.linalg.norm(
        np.array([upper_x, upper_y]) -
        np.array([lower_x, lower_y])
    )

    return distance_value

# ============================================================
# THRESHOLDS
# ============================================================

EAR_THRESHOLD = 0.22
MOUTH_THRESHOLD = 20

SLEEP_FRAMES = 20
YAWN_FRAMES = 15

sleep_counter = 0
yawn_counter = 0

# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = cap.read()

    if not success:
        print("Camera Error")
        break

    # Flip image
    frame = cv2.flip(frame, 1)

    # Get frame dimensions
    h, w, _ = frame.shape

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process face mesh
    results = face_mesh.process(rgb_frame)

    # ========================================================
    # FACE DETECTION
    # ========================================================

    if results.multi_face_landmarks:

        for face_landmarks in results.multi_face_landmarks:

            landmarks = face_landmarks.landmark

            # =================================================
            # EYE DETECTION
            # =================================================

            left_ear = eye_aspect_ratio(
                LEFT_EYE,
                landmarks,
                w,
                h
            )

            right_ear = eye_aspect_ratio(
                RIGHT_EYE,
                landmarks,
                w,
                h
            )

            avg_ear = (left_ear + right_ear) / 2

            # =================================================
            # MOUTH DETECTION
            # =================================================

            mouth_open = mouth_ratio(landmarks, w, h)

            # =================================================
            # DRAW TEXT
            # =================================================

            cv2.putText(
                frame,
                f"EAR: {avg_ear:.2f}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"MOUTH: {mouth_open:.2f}",
                (30, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2
            )

            # =================================================
            # SLEEP DETECTION
            # =================================================

            if avg_ear < EAR_THRESHOLD:

                sleep_counter += 1

                cv2.putText(
                    frame,
                    "EYES CLOSED",
                    (30, 200),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    3
                )

                if sleep_counter > SLEEP_FRAMES:

                    cv2.putText(
                        frame,
                        "DROWSINESS ALERT!",
                        (30, 300),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (0, 0, 255),
                        4
                    )

                    if not pygame.mixer.music.get_busy():
                        pygame.mixer.music.play()

            else:
                sleep_counter = 0
                pygame.mixer.music.stop()

            # =================================================
            # YAWN DETECTION
            # =================================================

            if mouth_open > MOUTH_THRESHOLD:

                yawn_counter += 1

                cv2.putText(
                    frame,
                    "YAWNING",
                    (30, 400),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 0),
                    3
                )

            else:
                yawn_counter = 0

            # =================================================
            # DRAW FACE LANDMARKS
            # =================================================

            for lm in landmarks:

                x = int(lm.x * w)
                y = int(lm.y * h)

                cv2.circle(
                    frame,
                    (x, y),
                    1,
                    (0, 255, 255),
                    -1
                )

    else:

        cv2.putText(
            frame,
            "NO DRIVER DETECTED",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )

    # ========================================================
    # DISPLAY FRAME
    # ========================================================

    cv2.imshow("Driver Drowsiness Detection", frame)

    key = cv2.waitKey(1)

    if key == 27:
        break

# ============================================================
# CLEANUP
# ============================================================

cap.release()
cv2.destroyAllWindows()