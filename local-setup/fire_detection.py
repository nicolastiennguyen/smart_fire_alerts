import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import scipy
import csv
from scipy.io import wavfile

# Load the model
model = hub.load('https://tfhub.dev/google/yamnet/1')

# Function to load class names
def class_names_from_csv(class_map_csv_text):
    class_names = []
    with tf.io.gfile.GFile(class_map_csv_text) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_names.append(row['display_name'])
    return class_names

# Load class names from the model
class_map_path = model.class_map_path().numpy()
class_names = class_names_from_csv(class_map_path)

# Function to ensure the sample rate is 16kHz
def ensure_sample_rate(original_sample_rate, waveform, desired_sample_rate=16000):
    if original_sample_rate != desired_sample_rate:
        desired_length = int(round(float(len(waveform)) / original_sample_rate * desired_sample_rate))
        waveform = scipy.signal.resample(waveform, desired_length)
    return desired_sample_rate, waveform

# Load and normalize audio
def load_audio(filename):
    sample_rate, wav_data = wavfile.read(filename)
    sample_rate, wav_data = ensure_sample_rate(sample_rate, wav_data)
    
    # If the audio is stereo (2 channels), take the average or select one channel to make it mono
    if len(wav_data.shape) > 1:
        wav_data = np.mean(wav_data, axis=1)  # Convert to mono by averaging channels
    
    waveform = wav_data / np.iinfo(np.int16).max  # Normalize the waveform to the range [-1.0, 1.0]
    return sample_rate, waveform

# Load and predict on audio file
def detect_alarm(audio_file, top_n=5):
    sample_rate, waveform = load_audio(audio_file)
    scores, embeddings, spectrogram = model(waveform)
    scores_np = scores.numpy()
    mean_scores = np.mean(scores_np, axis=0)
    
    # Get top 5 classes based on mean scores
    top5 = np.argsort(mean_scores)[-5:][::-1]
    print("Top predictions:")
    for i in top5:
        print(f" - {class_names[i]} ({mean_scores[i]:.2f})")

    # Look for fire-related sounds in top predictions
    fire_keywords = ['smoke alarm', 'fire alarm', 'siren', 'smoke detector']
    for i in top5:
        if any(keyword in class_names[i].lower() for keyword in fire_keywords):
            print("\n🚨 Fire alarm sound detected! 🚨")
            return True

    print("\n✅ No fire-related sounds detected.")
    return False