# Use an official AWS Lambda Python runtime as a base image
FROM public.ecr.aws/lambda/python:3.8

# Install necessary system dependencies
RUN pip install --upgrade pip
RUN pip install tensorflow tensorflow-hub scipy boto3 numpy

# Copy your function code and class map CSV to the container
COPY smart_fire_detection.py /var/task/
COPY yamnet_class_map.csv /var/task/

# Set the entry point for the Lambda function
CMD ["smart_fire_detection.lambda_handler"]
