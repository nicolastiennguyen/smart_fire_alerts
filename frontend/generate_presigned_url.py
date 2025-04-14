import boto3
import os
import json
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    print("Received event:", event)

    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }

    try:
        query_params = event.get('queryStringParameters') or {}
        filename = query_params['filename']
        print(f"Extracted filename: {filename}")
    except KeyError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Missing query string parameter: filename'})
        }

    s3_client = boto3.client('s3')
    bucket_name = os.environ.get('AUDIO_BUCKET_NAME', 'YOUR-S3-BUCKET-NAME-HERE') 

    try:
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': filename,
                'ContentType': 'audio/wav'
            },
            ExpiresIn=3600
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'url': presigned_url})
        }

    except ClientError as e:
        print(f"Error generating pre-signed URL: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to generate URL', 'message': str(e)})
        }
