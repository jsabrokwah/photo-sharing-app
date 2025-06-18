import json
import boto3
from PIL import Image
import io
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        source_key = event['Records'][0]['s3']['object']['key']
        
        target_bucket = os.environ.get('TARGET_BUCKET', 'photo-sharing-thumbnails-jsabrokwah')
        target_key = f"thumb-{source_key}"
        
        if source_key.startswith('thumb-'):
            return {
                'statusCode': 200,
                'body': json.dumps('Skipping thumbnail processing for an existing thumbnail')
            }
        
        response = s3.get_object(Bucket=source_bucket, Key=source_key)
        image = Image.open(io.BytesIO(response['Body'].read()))
        
        image.thumbnail((150, 150))
        
        buffer = io.BytesIO()
        image.save(buffer, "JPEG")
        buffer.seek(0)
        
        s3.put_object(
            Bucket=target_bucket,
            Key=target_key,
            Body=buffer,
            ContentType="image/jpeg"
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'Thumbnail created: {target_key}')
        }
    
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error creating thumbnail: {str(e)}')
        }