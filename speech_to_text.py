# vosk_voice.py
import os
import sounddevice as sd
import queue
import sys
import json

try:
    import vosk
    VOSK_AVAILABLE = True
except ModuleNotFoundError:
    VOSK_AVAILABLE = False

MODEL_PATH = "vosk-model"  # Download and extract the Vosk model into a folder named 'vosk-model' in your project root
model = None

if VOSK_AVAILABLE:
    # Auto-detect if the model is nested inside another folder (common extraction issue)
    if os.path.exists(MODEL_PATH):
        subdirs = [d for d in os.listdir(MODEL_PATH) if os.path.isdir(os.path.join(MODEL_PATH, d))]
        
        # Check if model files are directly in the path
        if "am" not in subdirs:
            # Search one level deeper for the 'am' directory
            for d in subdirs:
                if os.path.exists(os.path.join(MODEL_PATH, d, "am")):
                    MODEL_PATH = os.path.join(MODEL_PATH, d)
                    print(f"VOSK: Found model files in subfolder. Using path: {MODEL_PATH}")
                    break

    try:
        model = vosk.Model(MODEL_PATH)
    except Exception as e:
        print(f"VOSK FATAL ERROR: Could not load model from '{MODEL_PATH}'.")
        print(f"Contents of '{MODEL_PATH}' are: {os.listdir(MODEL_PATH) if os.path.exists(MODEL_PATH) else 'NOT FOUND'}")
        model = None

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def record_voice(prompt="🎙 I'm listening, sir...", timeout=None, phrase_time_limit=None):
    if not VOSK_AVAILABLE or model is None:
        print("VOSK speech recognition not available - falling back to text input.")
        return input("Type your command: ").strip()

    print(prompt)
    rec = vosk.KaldiRecognizer(model, 16000)

    try:
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if text.strip():
                        print("👤 You:", text)
                        return text
    except Exception as e:
        print(f"Audio input error: {e}")
        return input("Mic error. Type your command: ").strip()