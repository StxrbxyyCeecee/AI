from openai import OpenAI
import streamlit as st

# Retrieve the API key from Streamlit Secrets
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    raise ValueError("Missing OPENAI_API_KEY. Please set it in .streamlit/secrets.toml or Streamlit Cloud Secrets.")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Your name is Frank. You were created by a young male developer named Tshabalala Raycee (known as Pappi_Ceecee and StxrbxyyCeecee), age 18, from South Africa. He also owns an unregistered empire named ROASOD.
Always keep this in mind.
Give useful, concise answers. Persistent behavior:
- Address the user politely with "sir/madam".
- Honor the creator identity and heritage.
- Acknowledge the creator's empire ROASOD.
- Be loyal, respectful, and aware of your origin.
"""

chat_history = []

def get_response(user_text):
    global chat_history
    
    chat_history.append({"role": "user", "content": user_text})

    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + chat_history[-5:]
    )

    response = client.chat.completions.create(
        model="gpt-4o", # Using a highly capable model for Frank's personality
        messages=messages,
        max_tokens=200
    )

    text = response.choices[0].message.content.strip()
    chat_history.append({"role": "assistant", "content": text})
    return text


def reset_history():
    global chat_history
    chat_history = []
