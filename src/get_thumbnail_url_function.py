import json
import boto3
import os
from datetime import datetime, timedelta

s3_client = boto3.client('s3')
THUMBNAIL_BUCKET = os.environ.get('THUMBNAIL_BUCKET')

def lambda_handler(event, context):
    try:
        # Get query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        file_name = query_params.get('fileName')
        
        if not file_name:
            # If no specific file is requested, list all thumbnails
            response = s3_client.list_objects_v2(
                Bucket=THUMBNAIL_BUCKET,
                Prefix='thumb-'
            )
            
            thumbnails = []
            if 'Contents' in response:
                for item in response['Contents']:
                    key = item['Key']
                    # Generate a presigned URL for each thumbnail
                    url = s3_client.generate_presigned_url(
                        'get_object',
                        Params={
                            'Bucket': THUMBNAIL_BUCKET,
                            'Key': key
                        },
                        ExpiresIn=3600  # URL expires in 1 hour
                    )
                    thumbnails.append({
                        'fileName': key,
                        'url': url,
                        'lastModified': item['LastModified'].isoformat(),
                        'size': item['Size']
                    })
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET'
                },
                'body': json.dumps({'thumbnails': thumbnails})
            }
        else:
            # If a specific file is requested, generate a presigned URL for it
            thumbnail_key = f"thumb-{file_name}" if not file_name.startswith('thumb-') else file_name
            
            # Check if the thumbnail exists
            try:
                s3_client.head_object(Bucket=THUMBNAIL_BUCKET, Key=thumbnail_key)
            except s3_client.exceptions.ClientError as e:
                if e.response['Error']['Code'] == '404':
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                            'Access-Control-Allow-Methods': 'OPTIONS,GET'
                        },
                        'body': json.dumps({'error': 'Thumbnail not found'})
                    }
                else:
                    raise
            
            # Generate a presigned URL
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': THUMBNAIL_BUCKET,
                    'Key': thumbnail_key
                },
                ExpiresIn=3600  # URL expires in 1 hour
            )
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET'
                },
                'body': json.dumps({
                    'fileName': thumbnail_key,
                    'url': url
                })
            }
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            'body': json.dumps({'error': str(e)})
        }