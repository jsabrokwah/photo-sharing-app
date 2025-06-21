# Serverless Photo Sharing Application

A serverless application built on AWS Lambda that provides image processing and thumbnail generation capabilities through a web interface.

## Features

- Upload images through a web interface using presigned URLs
- Automatic thumbnail generation for uploaded images
- List and retrieve generated thumbnails
- Secure access to images through time-limited presigned URLs
- CORS-enabled API endpoints for web integration

## Project Structure

- `src/` - Contains Lambda function source code
- `images/` - Sample images for testing
- `Screenshots/` - AWS infrastructure setup documentation
- `build-layer.sh` and `build-pillow-layer.sh` - Scripts for creating Lambda layers
- `Dockerfile` - Container configuration for creating a lambda layer for Pillow library compatible with Python 3.9 runtime

## AWS Components

- **Lambda Functions:**
  - Image Resizer: Generates thumbnails from uploaded images
  - Presigned URL Generator: Creates secure upload URLs
  - Thumbnail URL Generator: Manages thumbnail access
- **S3 Buckets:**
  - Original images bucket
  - Thumbnails bucket
- **API Gateway:** RESTful API endpoints
- **CloudWatch:** Monitoring and logging

## Project Execution

Follow the [Implementation Journey](implementation-journey.md) for a step-by-step guide on setting up the application.

## Environment Variables

- `TARGET_BUCKET` - S3 bucket for storing thumbnails
- `THUMBNAIL_BUCKET` - S3 bucket name for thumbnail access

## Development

See individual README files in each directory for specific component documentation:
- [Source Code Documentation](src/README.md)
- [Sample Images](images/README.md)
- [AWS Setup Screenshots](Screenshots/README.md)
