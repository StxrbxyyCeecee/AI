import re
import os
import time
from aircraft_module import match_commands
import streamlit as st

# Graceful Windows Hardware Access for Cloud Deployment
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    IS_WINDOWS = True
except ImportError:
    IS_WINDOWS = False
    # Define these as None so the linter knows they exist in the namespace
    cast = None
    POINTER = None
    CLSCTX_ALL = None
    AudioUtilities = IAudioEndpointVolume = None

def get_volume_interface():
    """Helper to access the Windows Master Volume interface."""
    if not IS_WINDOWS: return None
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

def set_volume(level_percent):
    """Sets master volume to a specific percentage (0-100)."""
    volume = get_volume_interface()
    if not volume: return
    # Convert 0-100 to 0.0-1.0 scalar
    scalar = max(0.0, min(1.0, level_percent / 100.0))
    volume.SetMasterVolumeLevelScalar(scalar, None)

def change_volume(amount):
    """Increases or decreases volume by a relative amount."""
    volume = get_volume_interface()
    if not volume: return 0
    current = volume.GetMasterVolumeLevelScalar()
    new_volume = max(0.0, min(1.0, current + (amount / 100.0)))
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    return int(new_volume * 100)

def handle_system_command(user_text, player):
    user_text = user_text.lower()

    # 1. Set specific volume (e.g., "set volume to 50 percent")
    volume_match = re.search(r"volume (?:to|at) (\d+)", user_text)
    if volume_match and "set" in user_text:
        level = int(volume_match.group(1))
        set_volume(level)
        msg = f"Adjusting volume to {level} percent, sir."
        player.write_log(msg)
        return True

    # 2. Increase Volume
    if match_commands(user_text, ["increase volume", "volume up", "make it louder"]):
        new_level = change_volume(15)
        msg = f"Volume increased to {new_level} percent."
        player.write_log(msg)
        return True

    # 3. Decrease Volume
    if match_commands(user_text, ["decrease volume", "volume down", "lower the volume"]):
        new_level = change_volume(-15)
        msg = f"Volume lowered to {new_level} percent."
        player.write_log(msg)
        return True

    # 4. Mute/Unmute
    if match_commands(user_text, ["mute system", "silence audio", "mute volume"]):
        volume = get_volume_interface()
        if volume:
            volume.SetMute(1, None)
            player.write_log("System muted.")
            return True
        return False

    if match_commands(user_text, ["unmute system", "restore audio", "unmute volume"]):
        volume = get_volume_interface()
        if volume: volume.SetMute(0, None)
        msg = "Audio restored, sir."
        player.write_log(msg)
        return True

    # 5. Shutdown System
    if match_commands(user_text, ["stop the program", "shutdown", "exit frank", "terminate system", "self destruct"]):
        msg = "Terminating all system processes. Goodbye, sir."
        player.write_log(msg)
        st.toast("System shutting down...")
        st.stop()
        return True

    return False