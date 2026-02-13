"""
SenseVoice Background Service
- Runs silently in background
- Hotkey: ` (backtick) - Start/Stop recording
- Auto paste to cursor position
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
import winsound

# Windows API
import win32gui

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
model_loaded = False


def beep_start():
    """Beep when recording starts"""
    winsound.Beep(800, 100)


def beep_stop():
    """Beep when recording stops"""
    winsound.Beep(600, 100)


def beep_done():
    """Beep when transcription done"""
    winsound.Beep(1000, 100)
    winsound.Beep(1200, 100)


def beep_error():
    """Beep on error"""
    winsound.Beep(300, 200)


def load_model():
    """Load model"""
    global model, model_loaded

    from funasr import AutoModel

    try:
        model = AutoModel(
            model="iic/SenseVoiceSmall",
            trust_remote_code=True,
            device="cuda:0",
            disable_update=True,
        )
        model_loaded = True
        # Success beep
        winsound.Beep(1000, 100)
        winsound.Beep(1500, 100)
    except Exception:
        try:
            model = AutoModel(
                model="iic/SenseVoiceSmall",
                trust_remote_code=True,
                device="cpu",
                disable_update=True,
            )
            model_loaded = True
            winsound.Beep(1000, 100)
        except Exception:
            beep_error()
            model_loaded = False


def audio_callback(indata, frames, time_info, status):
    """Audio callback"""
    global audio_data
    if is_recording:
        audio_data.append(indata.copy())


def start_recording():
    """Start recording"""
    global is_recording, audio_data, stream, previous_window

    if not model_loaded:
        beep_error()
        return

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
    beep_start()


def stop_recording():
    """Stop recording and transcribe"""
    global is_recording, stream, previous_window

    is_recording = False
    beep_stop()

    if stream:
        stream.stop()
        stream.close()
        stream = None

    if not audio_data:
        beep_error()
        return

    # Combine audio
    audio = np.concatenate(audio_data, axis=0).flatten()

    # Save temp file
    import soundfile as sf
    temp_path = os.path.join(tempfile.gettempdir(), "sensevoice_temp.wav")
    sf.write(temp_path, audio, SAMPLE_RATE)

    try:
        # Transcribe
        result = model.generate(
            input=temp_path,
            language="ko",
            use_itn=True,
            batch_size_s=60,
        )

        if result and len(result) > 0:
            text = result[0].get("text", "")
            import re
            text = re.sub(r'<\|[^|]+\|>', '', text).strip()

            if text:
                pyperclip.copy(text)

                # Restore focus and paste
                if previous_window:
                    try:
                        win32gui.SetForegroundWindow(previous_window)
                        time.sleep(0.05)
                        keyboard.send('ctrl+v')
                        beep_done()
                    except Exception:
                        beep_error()
            else:
                beep_error()
        else:
            beep_error()

    except Exception:
        beep_error()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


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
    # Load model (will beep when ready)
    load_model()

    # Use OpenWhisper's pattern: hook all keys with suppress=True
    keyboard.hook(handle_keyboard_event, suppress=True)

    # Keep running
    keyboard.wait()


if __name__ == "__main__":
    main()
