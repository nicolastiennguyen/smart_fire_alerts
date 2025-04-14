from flask import Flask, request, jsonify, send_from_directory
from fire_detection import detect_alarm
import os

app = Flask(__name__)

# Serve the HTML file when the root URL is accessed
@app.route('/')
def index():
    return send_from_directory('.', 'index.html') # Serve index.html from current directory

# Route to handle audio file uploads
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    filename = 'uploaded_audio.wav'
    filepath = os.path.join('.', filename)
    
     # Save the uploaded file to disk
    file.save(filepath)

    # Run the fire sound detection
    fire_detected, top_predictions = detect_alarm(filepath)

    return jsonify({
        'fire_detected': fire_detected,
        'top_predictions': top_predictions
    })

if __name__ == '__main__':
    app.run(debug=True)
