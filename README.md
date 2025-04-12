# 🔥 Smart Fire Alerts

A prototype solution using AI, Python, and AWS to detect fire-related audio events and send real-time alerts to improve public safety.

---

## 📌 Problem Statement

According to the National Fire Protection Association (NFPA), nearly three out of five home fire deaths occur in properties without working smoke alarms, or where alarms go unheard. In many residential settings, especially those with elderly residents, individuals with disabilities, or those who are away from home, traditional fire alarms may sound but fail to alert anyone. This delay in emergency response significantly increases the risk of injury, death, and property loss.

The risk is even greater for individuals with hearing impairments or those located far from the alarm’s sound. While modern fire alarms are designed to alert homeowners in the event of a fire, many systems lack mechanisms to verify whether the alarm has been acknowledged, or to escalate the situation to emergency contacts or services. Additionally, current smart home systems often fail to integrate real-time verification or automatic notification, leaving dangerous gaps in the response process.

---

## 🚀 Solution Overview

This project implements an AI-powered fire sound detection system that enables users to upload .wav audio files for analysis. The system uses a pre-trained sound classification model (YAMNet from TensorFlow Hub) to process the uploaded audio and identify fire-related sounds, such as fire alarms, smoke detectors, sirens, and other emergency signals. When a fire-related sound is detected, the system sends an immediate SMS alert and publishes a notification to an Amazon SNS topic, simulating a rapid emergency response.

> 🧪 This prototype is designed for local testing. The AWS infrastructure is fully implemented, but users are not expected to deploy it themselves.

---

## 🧠 AI Component

- **Model**: [YAMNet](https://tfhub.dev/google/yamnet/1) from TensorFlow Hub — a deep net that predicts audio event classes from the AudioSet dataset.
- **Detection Logic**: After scoring an audio file, the system checks if any of the top 5 predicted classes include fire-related keywords: `fire`, `smoke alarm`, `fire alarm`, `siren`, `alarm`, or `smoke detector`.

---

## 🐍 Python Implementation

- `lambda_function.py`: Main inference function loaded into a Dockerized AWS Lambda. It:
  - Downloads audio from S3.
  - Resamples and processes audio.
  - Runs inference with YAMNet.
  - Publishes an alert to an SNS topic and sends an SMS if fire sounds are detected.

- `generate_presigned_url.py`: Generates a pre-signed S3 URL so that users can upload audio securely from the frontend.

---

## 🕸️ Web Architecture (AWS)

![Architecture](architecture.png)

**AWS Services Used**:
- **S3**: Stores uploaded audio files, class map, and hosts the static `index.html` frontend.
- **Lambda**: 
  - Docker-based audio classification handler triggered by S3 `ObjectCreated` events.
  - Generates pre-signed URLs for secure file uploads from the frontend.
- **API Gateway**: Exposes a REST API to interact with the Lambda functions, especially for pre-signed URL generation.
- **SNS**: Sends alerts via SMS and SNS topics.
- **SSM Parameter Store**: Stores secure config values like SNS topic ARN, phone number, region, and bucket name.


---

## 💻 Local Setup Instructions

This is the recommended way to test the AI model locally. We include a self-contained Python + HTML/JS interface that simulates uploading a file and running the model.

### 🔧 Requirements

- Python 3.8+
- Install required packages:

```bash
pip install -r requirements.txt
```

### ▶️ How to Run

From the `local-setup` directory:

1. Install the dependencies:

    ```bash
    pip install flask tensorflow tensorflow_hub scipy
    ```

2. Start the Flask app:

    ```bash
    python app.py
    ```

3. Open your browser to `http://localhost:5000`.

4. Upload a `.wav` file with a fire alarm sound (e.g., `Fire_Alarm_01.wav`).

You’ll see a result like:

- ✅ **No fire-related sounds detected.**
- 🚨 **Fire alarm sound detected!**

---

## 📝 Additional Notes

This prototype does not require deployment to AWS for testing. All AI inference and detection runs locally, using the provided Python scripts and Flask app.

---

## 👨‍💻 Contact

If you have any questions, feel free to reach out to me:

- **LinkedIn**: [https://www.linkedin.com/in/nicolas--nguyen/](https://www.linkedin.com/in/nicolas--nguyen/)
