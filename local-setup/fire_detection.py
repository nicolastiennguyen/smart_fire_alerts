import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import scipy
import csv
from scipy.io import wavfile

# Load the pre-trained YAMNet model from TensorFlow Hub
model = hub.load('https://tfhub.dev/google/yamnet/1')

# Function to load class names from the model's class map CSV
def class_names_from_csv(class_map_csv_text):
    class_names = []
    with tf.io.gfile.GFile(class_map_csv_text) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_names.append(row['display_name'])
    return class_names

# Load class names from the model’s associated class map file
class_map_path = model.class_map_path().numpy()
class_names = class_names_from_csv(class_map_path)

# Ensure the audio is at 16kHz, which YAMNet expects
def ensure_sample_rate(original_sample_rate, waveform, desired_sample_rate=16000):
    if original_sample_rate != desired_sample_rate:
        # Resample the waveform to 16kHz
        desired_length = int(round(float(len(waveform)) / original_sample_rate * desired_sample_rate))
        waveform = scipy.signal.resample(waveform, desired_length)
    return desired_sample_rate, waveform

# Load and prepare audio for inference
def load_audio(filename):
    # Load audio file
    sample_rate, wav_data = wavfile.read(filename)

    # Resample to 16kHz if needed
    sample_rate, wav_data = ensure_sample_rate(sample_rate, wav_data)

    # Convert to mono if stereo
    if len(wav_data.shape) > 1:
        wav_data = np.mean(wav_data, axis=1)

    # Normalize waveform to float values between -1.0 and 1.0
    waveform = wav_data / np.iinfo(np.int16).max
    return sample_rate, waveform

# Run the YAMNet model to detect fire-related sounds in an audio file
def detect_alarm(audio_file, top_n=5):
    # Load and process the audio
    sample_rate, waveform = load_audio(audio_file)

    # Run inference with the model
    scores, embeddings, spectrogram = model(waveform)

    # Convert TensorFlow tensor to NumPy array
    scores_np = scores.numpy()

    # Average predictions across time to get a single prediction vector
    mean_scores = np.mean(scores_np, axis=0)

    # Get the indices of the top N predicted classes
    top5 = np.argsort(mean_scores)[-top_n:][::-1]

    # Create a list of top predicted labels and their confidence scores
    top_predictions = [
        {"label": class_names[i], "score": float(mean_scores[i])}
        for i in top5
    ]

    # Define keywords that would indicate fire or an alarm sound
    fire_keywords = ['fire', 'smoke alarm', 'fire alarm', 'siren', 'smoke detector']

    # Check if any top prediction matches a fire-related keyword
    fire_detected = any(
        any(keyword in class_names[i].lower() for keyword in fire_keywords)
        for i in top5
    )

    return fire_detected, top_predictions
