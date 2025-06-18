# Photo Sharing Application

A serverless application that automatically generates thumbnails for uploaded images using AWS Lambda and S3.

## Architecture

- **S3 Buckets**: Two buckets for storing original images and thumbnails
- **Lambda Function**: Automatically resizes images when uploaded to the source bucket
- **Front-end**: Simple web interface for uploading and viewing images

## Deployment Instructions

### Prerequisites

- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.9 or later

### Deployment Steps

1. **Build the Lambda package**:

```bash
cd src
pip install -r requirements.txt -t .
cd ..
```

2. **Deploy the CloudFormation stack**:

```bash
sam build
sam deploy --guided
```

During the guided deployment, you'll be prompted for:
- Stack name (e.g., photo-sharing-app)
- AWS Region
- Parameter values for bucket names
- Confirmation of IAM role creation

3. **Test the deployment**:

Upload an image to the source bucket:
```bash
aws s3 cp images/sample.png s3://photo-sharing-app-jsabrokwah/
```

Check if the thumbnail was created:
```bash
aws s3 ls s3://photo-sharing-thumbnails-jsabrokwah/
```

4. **Deploy the front-end**:

For local testing, simply open the `index.html` file in a browser.

For production, upload the front-end files to an S3 bucket configured for static website hosting:
```bash
aws s3 cp index.html s3://your-frontend-bucket/
```

## Usage

1. Open the web application
2. Click "Choose File" to select an image
3. Click "Upload" to upload the image
4. The thumbnail will automatically be generated and displayed in the gallery

## Customization

- Modify the thumbnail size in `src/lambda_function.py`
- Customize the front-end styling in `index.html`
- Adjust the CloudFormation template parameters for different bucket names