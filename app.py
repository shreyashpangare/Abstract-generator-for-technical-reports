from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables. Please add it to your .env file.")

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "http://localhost:5000",
    "X-Title": "Abstract Generator for Technical Reports"
}

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        print(f"Sending prompt to OpenRouter: {prompt}")

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert technical writing assistant. Generate well-written, academic-style abstracts for technical reports."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        response = requests.post(OPENROUTER_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        if not response_data or "choices" not in response_data or not response_data["choices"]:
            return jsonify({"error": "No response from AI model"}), 500

        generated_text = response_data["choices"][0]["message"]["content"]
        print(f"Received response from OpenRouter: {generated_text[:100]}...")

        return jsonify({"response": generated_text})

    except requests.exceptions.RequestException as e:
        print(f"API Error: {str(e)}")
        return jsonify({"error": f"API Error: {str(e)}"}), 500
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Failed to generate response. Please try again."}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "api_key_configured": bool(api_key)}), 200

if __name__ == "__main__":
    print("Starting Flask server...")
    print(f"API Key configured: {'Yes' if api_key else 'No'}")
    app.run(debug=True, host='127.0.0.1', port=5000)
