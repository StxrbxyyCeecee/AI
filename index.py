from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_text = data.get('text', '')
    
    # This is where your AI logic (like OpenAI or Gemini API calls) would go.
    # For now, we simulate a response.
    response_text = f"Frank received: {user_text}. How can I help further?"
    
    return jsonify({
        "status": "success",
        "reply": response_text
    })

# Vercel needs the 'app' object to be available