from flask import Blueprint, request, jsonify, Response
from config import Config
from google import genai

chat = Blueprint('chat', __name__)

client = genai.Client(api_key=Config.GOOGLE_API_KEY)

@chat.route('/prompt', methods=['POST'])
def stream_prompt():
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    def generate():
        try:
            response = client.models.generate_content_stream(
                model='gemini-2.5-flash',
                contents=prompt
            )
            for chunk in response:
                if chunk.text:
                    yield f"data: {chunk.text}\n\n"
        except Exception as e:
            yield f"data: {{'error': '{str(e)}'}}\n\n"

    return Response(generate(), mimetype='text/event-stream')
