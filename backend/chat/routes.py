from flask import Blueprint, request, jsonify, Response
from ..config import Config
import google.generativeai as genai

chat = Blueprint('chat', __name__)

genai.configure(api_key=Config.GOOGLE_API_KEY)

@chat.route('/prompt', methods=['POST'])
def stream_prompt():
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    def generate():
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                yield f"data: {chunk.text}\n\n"
        except Exception as e:
            yield f"data: {{'error': '{str(e)}'}}\n\n"

    return Response(generate(), mimetype='text/event-stream')
