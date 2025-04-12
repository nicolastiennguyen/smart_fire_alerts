from flask import Flask, request, jsonify, send_from_directory
from fire_detection import detect_alarm
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    filename = 'uploaded_audio.wav'
    filepath = os.path.join('.', filename)
    file.save(filepath)
    
    is_fire = detect_alarm(filepath)
    return jsonify({'fire_detected': is_fire})

if __name__ == '__main__':
    app.run(debug=True)
