import json
import logging
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import scipy
import csv
from scipy.io import wavfile
import io
import boto3

# Set up logging to capture logs for the Lambda function
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3 = boto3.client('s3')
sns = boto3.client('sns')
ssm = boto3.client('ssm')  # For fetching parameters from SSM Parameter Store

# Function to fetch a parameter from SSM Parameter Store
def get_parameter(name):
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response['Parameter']['Value']

# Load environment configurations securely from Parameter Store
AWS_REGION = get_parameter("/smart_fire_alerts/AWS_REGION")
BUCKET_NAME = get_parameter("/smart_fire_alerts/S3_BUCKET_NAME")
SNS_TOPIC_ARN = get_parameter("/smart_fire_alerts/SNS_TOPIC_ARN")
SNS_PHONE_NUMBER = get_parameter("/smart_fire_alerts/SNS_PHONE_NUMBER")

# Load YAMNet model from TensorFlow Hub
model = hub.load('https://tfhub.dev/google/yamnet/1')

# Function to read class names from CSV file
def class_names_from_csv(csv_content):
    class_names = []
    reader = csv.DictReader(io.StringIO(csv_content))
    for row in reader:
        class_names.append(row['display_name'])
    return class_names

# Function to load class names from S3
def load_class_names():
    obj = s3.get_object(Bucket=BUCKET_NAME, Key='yamnet_class_map.csv')
    csv_content = obj['Body'].read().decode('utf-8')
    return class_names_from_csv(csv_content)

class_names = load_class_names()

# Ensure the audio is at 16kHz, which YAMNet expects
def ensure_sample_rate(original_sample_rate, waveform, desired_sample_rate=16000):
    if original_sample_rate != desired_sample_rate:
        desired_length = int(round(len(waveform) * desired_sample_rate / original_sample_rate))
        waveform = scipy.signal.resample(waveform, desired_length)
    return desired_sample_rate, waveform

# Function to load audio from S3
def load_audio_from_s3(bucket_name, file_key):
    # Fetch the audio file from S3
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    audio_data = obj['Body'].read()

    # Load the audio data and sample rate
    sample_rate, wav_data = wavfile.read(io.BytesIO(audio_data))
    # Resample to 16kHz if necessary
    sample_rate, wav_data = ensure_sample_rate(sample_rate, wav_data)

    # If the audio is stereo, convert it to mono
    if len(wav_data.shape) > 1:
        wav_data = np.mean(wav_data, axis=1)

    # Normalize the waveform values to a range between -1.0 and 1.0
    waveform = wav_data / np.iinfo(np.int16).max
    return sample_rate, waveform

def lambda_handler(event, context):
    logger.info("Lambda triggered")

    if 'Records' in event:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']

        # Load audio data from the S3 bucket
        sample_rate, waveform = load_audio_from_s3(bucket_name, file_key)

        # Get predictions from the YAMNet model
        scores, _, _ = model(waveform) # Run the audio data through the model
        mean_scores = np.mean(scores.numpy(), axis=0) # Compute the mean score across time frames

        # Sort and format the top 5 predictions
        top5 = np.argsort(mean_scores)[-5:][::-1]
        top_predictions = [f"{class_names[i]} (Score: {mean_scores[i]:.2f})" for i in top5]

        # Check for fire-related sounds
        fire_keywords = ['fire', 'smoke alarm', 'fire alarm', 'siren', 'smoke detector', 'alarm']
        fire_detected = False # Flag to indicate if fire is detected
        detected_index = None

        # Check if any of the top predictions match fire-related keywords
        for i in top5:
            if any(keyword in class_names[i].lower() for keyword in fire_keywords):
                fire_detected = True
                detected_index = i # Store the index of the detected fire-related sound
                break

        # Prepare message for SNS
        subject = "✅ No Fire Detected"
        message = f"No fire-related sounds were detected.\n\nTop 5 Predictions:\n" + "\n".join(top_predictions)

        # If fire sound is detected, update the subject and message
        if fire_detected:
            subject = f"🚨 Fire Alert: {class_names[detected_index]} detected!"
            message = (
                f"A fire-related sound was detected.\n\n"
                f"🔥 Detected: {class_names[detected_index]} (Score: {mean_scores[detected_index]:.2f})\n\n"
                f"🔍 Top 5 Predictions:\n" + "\n".join(top_predictions)
            )

            try:
                sns.publish(
                    PhoneNumber=SNS_PHONE_NUMBER,
                    Message=f"🔥 Fire Alert: {class_names[detected_index]} detected!"
                )
            except Exception as e:
                logger.warning(f"SMS failed: {e}")

        # Send the message to SNS topic
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=subject
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'fire_detected': fire_detected,
                'top_predictions': top_predictions
            })
        }
