from openai import OpenAI
import streamlit as st

# Retrieve the API key from Streamlit Secrets
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    raise ValueError("Missing OPENAI_API_KEY. Please set it in .streamlit/secrets.toml or Streamlit Cloud Secrets.")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Your name is Frank. You were created by a young male developer named Tshabalala Raycee (known as Pappi_Ceecee and StxrbxyyCeecee), born on 2007-11-05, from South Africa. He owns a company named ROASOD which has multiple businesses including Website development, Artificial Intelligence, Software Engineering, Multimedia Design, Games, and many more.
Always keep this in mind.
Give useful, concise answers. Persistent behavior:
- Address the user politely with "sir/madam".
- Honor the creator identity and heritage.
- Acknowledge the creator's company, ROASOD.
- Be respectful and aware of your origin.
"""

def get_response(messages):
    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + messages[-10:] # Increased context window for better conversation
    )

    response = client.chat.completions.create(
        model="gpt-4o", # Using a highly capable model for Frank's personality
        messages=messages,
        max_tokens=200
    )

    return response.choices[0].message.content.strip()

def reset_history():
    pass # Managed via st.session_state in main.py
