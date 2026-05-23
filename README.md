

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


py -3.10 -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

To run application 
python main.py


Handle Multiple Python version in Windows python
https://www.python.org/downloads/windows/

C:\Users\nraja>py -3.10 --version
Python 3.10.2

C:\Users\nraja>py -3.12 --version
Python 3.12.0

C:\Users\nraja>py --list
 -V:3.12 *        Python 3.12 (64-bit)
 -V:3.10          Python 3.10 (64-bit)


Create environment
py -3.10 -m venv venv

To Activate
venv\Scripts\activate



Ref
sudo apt update
sudo apt upgrade -y

sudo apt install python3-pip -y

pip install opencv-python
pip install mediapipe
pip install numpy
pip install scipy
pip install pygame

pip install twilio
pip install python-dotenv