# Lambda Functions Documentation

This directory contains the AWS Lambda functions that power the serverless Photo Sharing application.

## Functions Overview

### 1. Image Resizer (`image_resizer_function.py`)

Automatically generates thumbnails when new images are uploaded to S3.

**Features:**
- Creates 150x150 thumbnails while maintaining aspect ratio
- Handles various image formats (PNG, JPEG, etc.)
- Preserves image quality with LANCZOS resampling
- Adds white background for transparent images
- Skips processing of existing thumbnails

**Environment Variables:**
- `TARGET_BUCKET`: Destination bucket for thumbnails

### 2. Presigned URL Generator (`generate_presigned_url_function.py`)

Generates secure upload URLs for the web interface.

**Features:**
- Creates time-limited presigned POST URLs
- Enforces content-type validation
- Implements file size limits (1 byte to 10MB)
- Generates unique filenames using UUID
- CORS-enabled for web access

**Configuration:**
- URL expiration: 1 hour
- Bucket name: "photo-sharing-app-yourname"

### 3. Thumbnail URL Generator (`get_thumbnail_url_function.py`)

Manages access to generated thumbnails.

**Features:**
- Lists all available thumbnails
- Generates presigned URLs for thumbnail access
- Provides thumbnail metadata (size, last modified)
- Handles both single file and bulk listing requests
- CORS-enabled for web access

**Environment Variables:**
- `THUMBNAIL_BUCKET`: Source bucket for thumbnails

## Dependencies

Required Python packages are listed in `requirements.txt`. Key dependencies include:
- boto3: AWS SDK for Python
- Pillow: Image processing library

## Deployment

1. Ensure AWS credentials are configured
2. Install dependencies in a Lambda layer
3. Deploy functions to AWS Lambda
4. Configure S3 trigger for image resizer
5. Set up API Gateway endpoints for URL generators

## Error Handling

All functions implement comprehensive error handling:
- Input validation
- S3 operation errors
- Image processing failures
- Missing environment variables

## Security

- All S3 access is temporary through presigned URLs
- Content-type validation on uploads
- File size restrictions
- CORS headers for web security
