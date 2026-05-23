import os
from dotenv import load_dotenv

import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance
import time
import pygame

from twilio.rest import Client  # Twilio library for sending messages via WhatsApp
import requests
from datetime import datetime
# Load .env file
load_dotenv()

# ----------------Telegram Config ---------------- #
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
time_now = datetime.now().time()

message = f"""Time : {time_now}
Vehicle No : 001
Driver sleeping! Give alternative driver or take a break."""

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {
    "chat_id": CHAT_ID,
    "text": message
}

# ---------------- WhatsApp Config ---------------- #   
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP_NUMBER = os.getenv("FROM_WHATSAPP_NUMBER")
TO_WHATSAPP_NUMBER = os.getenv("TO_WHATSAPP_NUMBER")
# Initialize Twilio client
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# ---------------- Sending WhatsApp Message ---------------- #
def send_whatsapp_message(message):
    print("[INFO] Sending WhatsApp message...")
    try:
        response = client.messages.create(
            from_=FROM_WHATSAPP_NUMBER,
            body=message,
            to=TO_WHATSAPP_NUMBER
        )

        # Success response
        print("[SUCCESS] Message request sent to Twilio")
        print("Message SID:", response.sid)
        print("Status:", response.status)

        return True

    except Exception as e:
        # Error response
        print("[ERROR] WhatsApp message failed")
        print("Reason:", str(e))
        return False


# ============================================================
# INITIALIZE AUDIO
# ============================================================

pygame.mixer.init()
pygame.mixer.music.load("audio/sound2.mp3")  # Add your alarm file

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
                #cv2.putText(image, text, position, font, font_scale, color, thickness)
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
                    #cv2.putText(image, text, position, font, font_scale, color, thickness)
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

                        # Play alarm for 15 seconds
                        pygame.mixer.music.play()
                        alarm_start_time = time.time()
                        while time.time() - alarm_start_time < 15:
                            # Keep window responsive
                            cv2.imshow("Driver Drowsiness Detection", frame)
                            if cv2.waitKey(1) == 27:
                                break
                        pygame.mixer.music.stop()
                        #response = requests.post(url, data=data)  # to telegram
                        #send_whatsapp_message(message)             # to whatsapp

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