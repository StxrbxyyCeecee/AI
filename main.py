import streamlit as st
import asyncio
import requests
import re
import os
import pandas as pd
import psutil
from datetime import datetime
from voice_player import get_audio_bytes
from groq_ai import get_response
from aircraft_module import handle_aircraft_command, get_nearby_aircraft
from system_module import handle_system_command, IS_WINDOWS

# Streamlit UI Configuration
st.set_page_config(page_title="AI-FRANK", page_icon="🤖", layout="wide")

# Futuristic Styling
st.markdown("""
    <style>
    .stApp { background-color: #000216; color: #00ffff; font-family: 'Consolas', monospace; }
    .orb-glow {
        width: 100px; height: 100px; border-radius: 50%;
        background: radial-gradient(circle, #00ffff 0%, #000216 70%);
        box-shadow: 0 0 50px #00ffff; margin: auto;
        animation: pulse 2s infinite ease-in-out alternate;
    }
    @keyframes pulse { from { transform: scale(0.9); } to { transform: scale(1.1); } }
    </style>
    <div class="orb-glow"></div>
    <h1 style='text-align: center; color: #00ffff; letter-spacing: 5px; text-shadow: 0 0 20px #00ffff;'>FRANK</h1>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "initialized" not in st.session_state:
    st.session_state.initialized = False

# Sidebar Telemetry
with st.sidebar:
    st.header("💻 System Stats")
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    st.progress(cpu/100, text=f"CPU: {cpu}%")
    st.progress(ram/100, text=f"RAM: {ram}%")
    
    st.header("✈ Radar Scopes")
    planes = get_nearby_aircraft()
    st.metric("Nearby Aircraft", len(planes))
    if planes:
        # Convert the list of aircraft to a DataFrame for st.map
        radar_df = pd.DataFrame(planes)
        # st.map automatically identifies 'lat' and 'lon' columns
        st.map(radar_df[['lat', 'lon']], color='#00ffff', size=20)

        for p in planes[:3]:
            st.text(f"ID: {p['callsign']} | {p['distance']:.1f}km")

async def get_briefing():
    now = datetime.now()
    time_of_day = "morning" if now.hour < 12 else "afternoon" if now.hour < 18 else "evening"
    current_time = now.strftime("%I:%M %p")
    
    weather_task = asyncio.to_thread(requests.get, "https://wttr.in?format=%t+and+%C", timeout=5)
    news_task = asyncio.to_thread(requests.get, "https://news.google.com/news/rss", timeout=5)
    w_res, n_res = await asyncio.gather(weather_task, news_task, return_exceptions=True)

    weather = w_res.text.strip() if hasattr(w_res, 'status_code') else "unavailable"
    headline = "service unreachable"
    try:
        match = re.search(r'<item>.*?<title>(.*?)</title>', n_res.text, re.DOTALL)
        if match: headline = match.group(1).split(" - ")[0]
    except: pass

    return f"Good {time_of_day}, sir. It is {current_time}. Weather: {weather}. News: {headline}. System online. How can I assist?"

# Initialization
if not st.session_state.initialized:
    briefing = asyncio.run(get_briefing())
    st.session_state.messages.append({"role": "assistant", "content": briefing})
    audio = asyncio.run(get_audio_bytes(briefing))
    st.audio(audio, format="audio/mp3", autoplay=True)
    st.session_state.initialized = True

# Chat History
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat Input
if prompt := st.chat_input("Command Frank..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Process Command
    class StreamlitPlayer:
        def write_log(self, text): st.toast(text)
    
    player = StreamlitPlayer()
    # Capture the specific response from modules
    module_response = handle_aircraft_command(prompt, player) or handle_system_command(prompt, player)
    
    if module_response is True: # System module often returns True but logs internally
        response = "Task complete, sir. System status updated."
    elif isinstance(module_response, str): # Aircraft module now returns strings
        response = module_response
    else:
        response = get_response(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
    audio = asyncio.run(get_audio_bytes(response))
    st.audio(audio, format="audio/mp3", autoplay=True)
