const AWS = require('aws-sdk');
const s3 = new AWS.S3();

exports.handler = async (event) => {
    const filename = event.queryStringParameters.filename;
    const s3BucketName = 'YOUR-S3-BUCKET-NAME-HERE';

    // Generate the pre-signed URL
    const signedUrlParams = {
        Bucket: s3BucketName,
        Key: filename,
        Expires: 60, // Link expiration in seconds
        ContentType: 'audio/wav' // Change this if necessary
    };

    try {
        const signedUrl = s3.getSignedUrl('putObject', signedUrlParams);
        
        // Return the pre-signed URL with CORS headers
        return {
            statusCode: 200,
            headers: {
                'Access-Control-Allow-Origin': '*',  // Allow requests from all domains (or specify your domain here)
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            body: JSON.stringify({ url: signedUrl })
        };
    } catch (error) {
        console.error("Error generating pre-signed URL:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: "Failed to generate pre-signed URL" })
        };
    }
};
