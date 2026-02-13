"""
SenseVoice CLI - Voice to Text
- Hotkey: ` (backtick) - Start/Stop recording
- Auto paste to cursor position
- Key is suppressed (not typed)
"""

import os
import sys
import tempfile
import time
import threading
import numpy as np
import sounddevice as sd
import keyboard
import pyperclip

# Windows API
import win32gui

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Settings
SAMPLE_RATE = 16000
CHANNELS = 1
HOTKEY = '`'

# State
is_recording = False
audio_data = []
model = None
stream = None
previous_window = None


def load_model():
    """Load model"""
    global model
    print("[*] Loading SenseVoice model...")

    from funasr import AutoModel

    try:
        model = AutoModel(
            model="iic/SenseVoiceSmall",
            trust_remote_code=True,
            device="cuda:0",
            disable_update=True,
        )
        print("[OK] Model loaded (CUDA)")
    except Exception as e:
        print(f"[!] CUDA failed, switching to CPU: {e}")
        model = AutoModel(
            model="iic/SenseVoiceSmall",
            trust_remote_code=True,
            device="cpu",
            disable_update=True,
        )
        print("[OK] Model loaded (CPU)")


def audio_callback(indata, frames, time_info, status):
    """Audio callback"""
    global audio_data
    if is_recording:
        audio_data.append(indata.copy())


def start_recording():
    """Start recording"""
    global is_recording, audio_data, stream, previous_window

    # Save current active window
    previous_window = win32gui.GetForegroundWindow()

    is_recording = True
    audio_data = []

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype='float32',
        callback=audio_callback
    )
    stream.start()
    print("\n[REC] Recording... (press ` to stop)")


def stop_recording():
    """Stop recording and transcribe"""
    global is_recording, stream, previous_window

    is_recording = False

    if stream:
        stream.stop()
        stream.close()
        stream = None

    if not audio_data:
        print("[X] No audio")
        return

    print("[...] Transcribing...")

    # Combine audio
    audio = np.concatenate(audio_data, axis=0).flatten()

    # Save temp file
    import soundfile as sf
    temp_path = os.path.join(tempfile.gettempdir(), "sensevoice_temp.wav")
    sf.write(temp_path, audio, SAMPLE_RATE)

    try:
        # Transcribe with SenseVoice
        result = model.generate(
            input=temp_path,
            language="ko",  # Korean
            use_itn=True,
            batch_size_s=60,
        )

        if result and len(result) > 0:
            text = result[0].get("text", "")
            # Remove special tokens
            import re
            text = re.sub(r'<\|[^|]+\|>', '', text).strip()

            if text:
                pyperclip.copy(text)
                print(f"\n[OK] Result: {text}")

                # Restore focus and paste
                if previous_window:
                    try:
                        win32gui.SetForegroundWindow(previous_window)
                        time.sleep(0.05)
                        keyboard.send('ctrl+v')
                        print("[PASTED] Text inserted at cursor")
                    except Exception as e:
                        print(f"[!] Could not paste: {e}")
                        print("[COPIED] Use Ctrl+V to paste manually")
            else:
                print("[X] No text recognized")
        else:
            print("[X] Recognition failed")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    print("\n[READY] Press ` to record")


def toggle_recording():
    """Toggle recording"""
    global is_recording

    if is_recording:
        stop_recording()
    else:
        start_recording()


def handle_keyboard_event(event):
    """Global keyboard event handler with suppression (OpenWhisper pattern)"""
    if event.event_type == keyboard.KEY_DOWN:
        if event.name == HOTKEY:
            # Run callback in separate thread to avoid blocking
            threading.Thread(target=toggle_recording, daemon=True).start()
            return False  # Suppress the backtick key

    # Let all other keys pass through
    return True


def main():
    print("=" * 50)
    print("  SenseVoice - Voice to Text (15x faster)")
    print("=" * 50)
    print(f"  Hotkey: [ {HOTKEY} ] backtick key (suppressed)")
    print("  Auto-paste to cursor position!")
    print("  Exit: Ctrl+C")
    print("=" * 50)

    # Load model
    load_model()

    print("\n[READY] Press ` anywhere to start recording")

    # Use OpenWhisper's pattern: hook all keys with suppress=True
    keyboard.hook(handle_keyboard_event, suppress=True)

    # Keep running
    keyboard.wait()


if __name__ == "__main__":
    main()
