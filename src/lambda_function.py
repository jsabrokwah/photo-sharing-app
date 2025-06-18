import json
import boto3
from PIL import Image
import io
import os
from urllib.parse import unquote_plus

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        # URL decode the key to handle spaces and special characters
        source_key = unquote_plus(event['Records'][0]['s3']['object']['key'])
        
        target_bucket = os.environ.get('TARGET_BUCKET', 'photo-sharing-thumbnails-jsabrokwah')
        target_key = f"thumb-{source_key}"
        
        # Skip if already a thumbnail
        if source_key.startswith('thumb-'):
            return {
                'statusCode': 200,
                'body': json.dumps('Skipping thumbnail processing for an existing thumbnail')
            }
        
        # Get the object from S3
        response = s3.get_object(Bucket=source_bucket, Key=source_key)
        image = Image.open(io.BytesIO(response['Body'].read()))
        
        # Convert to RGB if necessary (handles PNG with transparency, etc.)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create white background for transparent images
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Create thumbnail
        image.thumbnail((150, 150), Image.Resampling.LANCZOS)
        
        # Save as JPEG
        buffer = io.BytesIO()
        image.save(buffer, "JPEG", quality=85, optimize=True)
        buffer.seek(0)
        
        # Upload to target bucket
        s3.put_object(
            Bucket=target_bucket,
            Key=target_key,
            Body=buffer,
            ContentType="image/jpeg",
            # Add some metadata
            Metadata={
                'original-key': source_key,
                'thumbnail-size': '150x150'
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'Thumbnail created: {target_key}')
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error creating thumbnail: {str(e)}')
        }