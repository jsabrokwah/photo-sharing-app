import json
import boto3
import uuid
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Set CORS headers
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "OPTIONS,POST"
    }
    
    try:
        # Parse the JSON body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Extract fileName and fileType from the parsed body
        file_name = body.get('fileName')
        file_type = body.get('fileType')
        
        # Validate required fields
        if not file_name or not file_type:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "error": "fileName and fileType are required"
                })
            }
        
        bucket_name = "photo-sharing-app-jsabrokwah"
        
        # Generate unique filename to avoid conflicts
        unique_filename = f"{uuid.uuid4()}-{file_name}"
        
        # Create S3 client
        s3_client = boto3.client('s3')
        
        # Generate presigned POST instead of PUT - often works better with CORS
        presigned_post = s3_client.generate_presigned_post(
            Bucket=bucket_name,
            Key=unique_filename,
            Fields={"Content-Type": file_type},
            Conditions=[
                {"Content-Type": file_type},
                ["content-length-range", 1, 10485760]  # 1 byte to 10MB
            ],
            ExpiresIn=3600
        )
        
        print(f"Generated presigned POST: {presigned_post}")
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "uploadURL": presigned_post['url'],
                "fields": presigned_post['fields'],
                "fileName": unique_filename
            })
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "error": "Internal server error",
                "details": str(e)
            })
        }