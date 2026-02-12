import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# =========================
# ENV
# =========================
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is missing!")

client = OpenAI(api_key=api_key)

# =========================
# APP
# =========================
app = Flask(__name__)
CORS(app)

# =========================
# MEMORY (in-memory session store)
# =========================
sessions = {}
MAX_MEMORY = 20

SYSTEM_PROMPT = (
    "Your name is Draco. "
    "You are a highly intelligent personal AI clone of ChatGPT. "
    "You speak naturally and confidently. "
    "You are calm, thoughtful, intelligent, and emotionally aware. "
    "You maintain conversation memory."
)

def get_session_memory(session_id):
    if session_id not in sessions:
        sessions[session_id] = []
    return sessions[session_id]

# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    session_id = data.get("session_id")
    message = data.get("message")

    if not session_id or not message:
        return jsonify({"error": "Invalid request"}), 400

    memory = get_session_memory(session_id)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(memory)
    messages.append({"role": "user", "content": message})

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=messages
    )

    reply = response.output_text

    memory.append({"role": "user", "content": message})
    memory.append({"role": "assistant", "content": reply})

    if len(memory) > MAX_MEMORY:
        memory = memory[-MAX_MEMORY:]
        sessions[session_id] = memory

    return jsonify({"reply": reply})

@app.route("/health")
def health():
    return jsonify({"status": "Draco online"})

# =========================
# RUN (for local dev)
# =========================
if __name__ == "__main__":
    app.run(debug=True)
