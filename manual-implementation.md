# Manual Implementation Guide: Photo Sharing Application

This guide provides step-by-step instructions for implementing the Photo Sharing Application manually using the AWS Management Console.

## Project Overview

This application allows users to upload images to an S3 bucket. When an image is uploaded, an AWS Lambda function automatically creates a thumbnail version of the image and stores it in a separate S3 bucket. A simple web interface allows users to upload images and view the thumbnails.

## Implementation Steps

### Step 1: Create S3 Buckets

#### Source Bucket (for original images)
1. Sign in to the AWS Management Console
2. Navigate to **S3** service
3. Click **Create bucket**
4. Enter a unique bucket name (e.g., `photo-sharing-app-yourname`)
5. Select your preferred AWS Region
6. Under **Object Ownership**, select **ACLs disabled**
7. Under **Block Public Access settings**, uncheck "Block all public access" if you want the images to be publicly accessible
8. Enable **Versioning** if you want to maintain multiple versions of images
9. Leave other settings as default
10. Click **Create bucket**

#### Target Bucket (for thumbnails)
1. Click **Create bucket** again
2. Enter a unique bucket name (e.g., `photo-sharing-thumbnails-yourname`)
3. Select the same AWS Region as the source bucket
4. Configure the same settings as the source bucket
5. Click **Create bucket**

### Step 2: Configure CORS for the Buckets

#### For Source Bucket
1. Go to the source bucket you created
2. Click on the **Permissions** tab
3. Scroll down to **Cross-origin resource sharing (CORS)**
4. Click **Edit**
5. Enter the following CORS configuration:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": ["ETag", "x-amz-meta-custom-header", "x-amz-server-side-encryption", "x-amz-request-id", "x-amz-id-2"],
        "MaxAgeSeconds": 3600
    }
]
```
6. Click **Save changes**

#### For Target Bucket
1. Go to the target bucket you created
2. Click on the **Permissions** tab
3. Scroll down to **Cross-origin resource sharing (CORS)**
4. Click **Edit**
5. Enter the following CORS configuration:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": ["ETag", "Content-Length", "Content-Type"],
        "MaxAgeSeconds": 3600
    }
]
```
6. Click **Save changes**

> **Note**: For production environments, replace `"AllowedOrigins": ["*"]` with your specific domain(s) like `"AllowedOrigins": ["https://your-domain.com", "https://www.your-domain.com"]`

### Step 3: Create IAM Role for Lambda

1. Navigate to **IAM** service
2. In the left navigation pane, click **Roles**
3. Click **Create role**
4. Select **AWS service** as the trusted entity
5. Select **Lambda** as the use case
6. Click **Next: Permissions**
7. Search for and attach the following policies:
   - `AWSLambdaBasicExecutionRole` (for CloudWatch Logs)
8. Click **Next: Tags** (add tags if needed)
9. Click **Next: Review**
10. Name the role `lambda-s3-resizer-role`
11. Click **Create role**

### Step 4: Add Custom Permissions to the IAM Role

1. Go back to the **Roles** section in IAM
2. Find and click on the `lambda-s3-resizer-role` you just created
3. Click on the **Permissions** tab
4. Click **Add permissions** > **Create inline policy**
5. Click on the **JSON** tab
6. Replace the existing policy with:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::photo-sharing-app-yourname/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::photo-sharing-thumbnails-yourname/*"
        }
    ]
}
```
7. Replace `photo-sharing-app-yourname` and `photo-sharing-thumbnails-yourname` with your actual bucket names
8. Click **Review policy**
9. Name the policy `S3ImageProcessingPolicy`
10. Click **Create policy**

### Step 5: Create Lambda Function

1. Navigate to **Lambda** service
2. Click **Create function**
3. Select **Author from scratch**
4. Enter `ImageResizer` as the function name
5. Select **Python 3.9** as the runtime
6. Under **Permissions**, expand **Change default execution role**
7. Select **Use an existing role**
8. Select the `lambda-s3-resizer-role` you created earlier
9. Click **Create function**

### Step 6: Configure Lambda Function

1. In the **Code** tab, replace the default code with:
```python
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
        
        target_bucket = os.environ.get('TARGET_BUCKET', 'photo-sharing-thumbnails-yourname')
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
```
2. Replace `photo-sharing-thumbnails-yourname` with your actual target bucket name

### Step 7: Add Lambda Layer for PIL/Pillow

1. In the Lambda function page, scroll down to the **Layers** section
2. Click **Add a layer**
3. Select **AWS Layers**
4. Search for and select `Pillow` or `PIL` (Python Imaging Library)
5. Select the compatible version for Python 3.9
6. Click **Add**

If no AWS-provided layer is available for PIL/Pillow, you'll need to create a custom layer:

1. On your local machine, create a directory for the layer
2. Install the required packages:
```bash
mkdir -p python/lib/python3.9/site-packages
pip install Pillow -t python/lib/python3.9/site-packages
```
3. Zip the python directory:
```bash
zip -r pillow_layer.zip python
```
4. In the Lambda console, go to **Layers** > **Create layer**
5. Name it `PillowLayer`
6. Upload the zip file
7. Select Python 3.9 as the compatible runtime
8. Click **Create**
9. Go back to your Lambda function and add this custom layer

### Step 8: Configure Lambda Environment Variables

1. In the Lambda function page, go to the **Configuration** tab
2. Click on **Environment variables**
3. Click **Edit**
4. Click **Add environment variable**
5. Set `TARGET_BUCKET` as the key and your thumbnail bucket name as the value
6. Click **Save**

### Step 9: Configure Lambda Settings

1. In the Lambda function page, go to the **Configuration** tab
2. Click on **General configuration**
3. Click **Edit**
4. Set **Memory** to 256 MB
5. Set **Timeout** to 30 seconds
6. Click **Save**

### Step 10: Configure S3 Trigger for Lambda

1. In the Lambda function page, go to the **Configuration** tab
2. Click on **Triggers**
3. Click **Add trigger**
4. Select **S3** from the dropdown
5. Select your source bucket
6. For **Event type**, select **All object create events**
7. Acknowledge the recursive invocation warning (if shown)
8. Click **Add**

### Step 11: Test the Lambda Function

1. Navigate to the **S3** service
2. Go to your source bucket
3. Click **Upload**
4. Select an image file from your computer
5. Click **Upload**
6. Wait a few seconds for the Lambda function to process the image
7. Navigate to your target bucket
8. Verify that a thumbnail image with the prefix "thumb-" has been created

### Step 12: Set Up API Gateway for Secure Image Access

1. Navigate to **API Gateway** service
2. Click **Create API**
3. Select **REST API** and click **Build**
4. Select **New API** and enter the following details:
   - API name: `PhotoSharingAPI`
   - Description: `API for secure access to photo sharing application`
   - Endpoint Type: `Regional`
5. Click **Create API**

#### Create Resource for Presigned URL Generation

1. Click **Actions** > **Create Resource**
2. Enter the following details:
   - Resource Name: `presigned-url`
   - Resource Path: `/presigned-url`
3. Click **Create Resource**

#### Create POST Method for Presigned URL Generation

1. With the `/presigned-url` resource selected, click **Actions** > **Create Method**
2. Select **POST** from the dropdown and click the checkmark
3. Configure the method:
   - Integration type: **Lambda Function**
   - Lambda Region: Select your region
   - Lambda Function: `GeneratePresignedURL` (we'll create this function in the next step)
4. Click **Save**

#### Create Resource for Thumbnail Access

1. Go back to the root of your API
2. Click **Actions** > **Create Resource**
3. Enter the following details:
   - Resource Name: `thumbnails`
   - Resource Path: `/thumbnails`
4. Click **Create Resource**

#### Create GET Method for Thumbnail Access

1. With the `/thumbnails` resource selected, click **Actions** > **Create Method**
2. Select **GET** from the dropdown and click the checkmark
3. Configure the method:
   - Integration type: **Lambda Function**
   - Lambda Region: Select your region
   - Lambda Function: `GetThumbnailURL` (we'll create this function in a later step)
4. Click **Save**

#### Enable CORS for API Gateway

1. Select the `/presigned-url` resource
2. Click **Actions** > **Enable CORS**
3. Configure the following settings:
   - Access-Control-Allow-Headers: `'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'`
   - Access-Control-Allow-Methods: `'OPTIONS,POST'`
   - Access-Control-Allow-Origin: `'*'` (For production, specify your actual domain)
   - Access-Control-Expose-Headers: `'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'`
   - Access-Control-Max-Age: `'3600'`
4. Click **Enable CORS and replace existing CORS headers**

5. Select the `/thumbnails` resource
6. Click **Actions** > **Enable CORS**
7. Configure the following settings:
   - Access-Control-Allow-Headers: `'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'`
   - Access-Control-Allow-Methods: `'OPTIONS,GET'`
   - Access-Control-Allow-Origin: `'*'` (For production, specify your actual domain)
   - Access-Control-Expose-Headers: `'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'`
   - Access-Control-Max-Age: `'3600'`
8. Click **Enable CORS and replace existing CORS headers**

9. **Important**: After enabling CORS, you must redeploy the API for the changes to take effect:
   - Click **Actions** > **Deploy API**
   - Select the `prod` stage
   - Click **Deploy**

#### Deploy the API

1. Click **Actions** > **Deploy API**
2. Create a new stage:
   - Stage name: `prod`
   - Stage description: `Production environment`
3. Click **Deploy**
4. Note the **Invoke URL** displayed at the top of the stage editor page

### Step 13: Create Lambda Function for Presigned URL Generation

1. Navigate to **Lambda** service
2. Click **Create function**
3. Select **Author from scratch**
4. Enter `GeneratePresignedURL` as the function name
5. Select **Python 3.9** as the runtime
6. Under **Permissions**, expand **Change default execution role**
7. Select **Create a new role with basic Lambda permissions**
8. Click **Create function**

#### Configure Lambda Function Code

1. In the **Code** tab, replace the default code with:
```python
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
        
        bucket_name = "photo-sharing-app-yourname"
        
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
```

#### Configure Environment Variables

1. Go to the **Configuration** tab
2. Click on **Environment variables**
3. Click **Edit**
4. Add a new environment variable:
   - Key: `SOURCE_BUCKET`
   - Value: Your source bucket name (e.g., `photo-sharing-app-yourname`)
5. Click **Save**

#### Configure IAM Permissions

1. Go to the **Configuration** tab
2. Click on **Permissions**
3. Click on the role name to open it in the IAM console
4. Click **Add permissions** > **Create inline policy**
5. Click on the **JSON** tab
6. Replace the existing policy with:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::photo-sharing-app-yourname/*"
        }
    ]
}
```
7. Replace `photo-sharing-app-yourname` with your actual bucket name
8. Click **Review policy**
9. Name the policy `PresignedURLGenerationPolicy`
10. Click **Create policy**

### Step 14: Create Lambda Function for Thumbnail Access

1. Navigate to **Lambda** service
2. Click **Create function**
3. Select **Author from scratch**
4. Enter `GetThumbnailURL` as the function name
5. Select **Python 3.9** as the runtime
6. Under **Permissions**, expand **Change default execution role**
7. Select **Create a new role with basic Lambda permissions**
8. Click **Create function**

#### Configure Lambda Function Code

1. In the **Code** tab, replace the default code with:
```python
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
```

#### Configure Environment Variables

1. Go to the **Configuration** tab
2. Click on **Environment variables**
3. Click **Edit**
4. Add a new environment variable:
   - Key: `THUMBNAIL_BUCKET`
   - Value: Your thumbnail bucket name (e.g., `photo-sharing-thumbnails-yourname`)
5. Click **Save**

#### Configure IAM Permissions

1. Go to the **Configuration** tab
2. Click on **Permissions**
3. Click on the role name to open it in the IAM console
4. Click **Add permissions** > **Create inline policy**
5. Click on the **JSON** tab
6. Replace the existing policy with:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::photo-sharing-thumbnails-yourname",
                "arn:aws:s3:::photo-sharing-thumbnails-yourname/*"
            ]
        }
    ]
}
```
7. Replace `photo-sharing-thumbnails-yourname` with your actual bucket name
8. Click **Review policy**
9. Name the policy `ThumbnailAccessPolicy`
10. Click **Create policy**

### Step 15: Create a Production-Ready Web Interface

1. Create an HTML file named `index.html` on your local machine with the following content:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Photo Sharing App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        .upload-section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
        .gallery {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }
        .thumbnail {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            width: 200px;
        }
        .thumbnail:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .thumbnail img {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 3px;
        }
        .thumbnail p {
            margin: 5px 0;
            font-size: 0.9em;
            word-break: break-all;
        }
        .status {
            margin-top: 10px;
            padding: 10px;
            display: none;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
        }
        .info {
            background-color: #d1ecf1;
            color: #0c5460;
        }
        .progress-bar {
            height: 10px;
            background-color: #e9ecef;
            border-radius: 5px;
            margin-top: 10px;
            overflow: hidden;
        }
        .progress {
            height: 100%;
            background-color: #007bff;
            width: 0%;
            transition: width 0.3s;
        }
        button {
            padding: 8px 16px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background-color: #0069d9;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        input[type="file"] {
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <h1>Photo Sharing App</h1>
    
    <div class="upload-section">
        <h2>Upload an Image</h2>
        <input type="file" id="uploadFile" accept="image/*">
        <button id="uploadButton" onclick="uploadImage()">Upload</button>
        <div id="status" class="status"></div>
        <div id="progressContainer" style="display: none;">
            <div class="progress-bar">
                <div id="progressBar" class="progress"></div>
            </div>
            <div id="progressText">0%</div>
        </div>
    </div>

    <h2>Gallery</h2>
    <div id="gallery" class="gallery">
        <p>Loading images...</p>
    </div>

    <script>
        // Replace these with your actual API Gateway endpoint
        const apiEndpoint = "https://your-api-gateway-endpoint.execute-api.your-region.amazonaws.com/your-stage";
        
        // DOM elements
        const uploadButton = document.getElementById("uploadButton");
        const progressContainer = document.getElementById("progressContainer");
        const progressBar = document.getElementById("progressBar");
        const progressText = document.getElementById("progressText");
        
        async function uploadImage() {
            const fileInput = document.getElementById("uploadFile");
            
            if (!fileInput.files.length) {
                showStatus("Please select a file first", "error");
                return;
            }
            
            const file = fileInput.files[0];
            
            // Disable the upload button during upload
            uploadButton.disabled = true;
            
            try {
                // Step 1: Get a presigned POST URL from our API
                showStatus("Preparing upload...", "info");
                
                const presignedUrlResponse = await fetch(`${apiEndpoint}/presigned-url`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    mode: "cors",
                    body: JSON.stringify({
                        fileName: file.name,
                        fileType: file.type
                    })
                });
                
                if (!presignedUrlResponse.ok) {
                    const errorText = await presignedUrlResponse.text();
                    throw new Error(`Failed to get upload URL (${presignedUrlResponse.status}): ${errorText}`);
                }
                
                const presignedData = await presignedUrlResponse.json();
                const { uploadURL, fields, fileName } = presignedData;
                
                if (!uploadURL || !fields) {
                    throw new Error("Invalid response: Missing upload URL or fields");
                }
                
                console.log("Presigned POST data:", presignedData);
                
                // Step 2: Upload the file using presigned POST (FormData)
                showStatus("Uploading image...", "info");
                progressContainer.style.display = "block";
                
                // Create FormData with the presigned POST fields
                const formData = new FormData();
                
                // Add all the fields from the presigned POST first
                Object.keys(fields).forEach(key => {
                    formData.append(key, fields[key]);
                });
                
                // Add the file last (this is important for S3)
                formData.append('file', file);
                
                // Use XMLHttpRequest for upload progress tracking
                await new Promise((resolve, reject) => {
                    const xhr = new XMLHttpRequest();
                    
                    xhr.upload.addEventListener("progress", (event) => {
                        if (event.lengthComputable) {
                            const percentComplete = Math.round((event.loaded / event.total) * 100);
                            progressBar.style.width = percentComplete + "%";
                            progressText.textContent = percentComplete + "%";
                        }
                    });
                    
                    xhr.addEventListener("load", () => {
                        if (xhr.status >= 200 && xhr.status < 300) {
                            resolve();
                        } else {
                            console.error("S3 Upload Error Response:", xhr.responseText);
                            reject(new Error(`S3 Upload Error: ${xhr.status} - ${xhr.statusText}`));
                        }
                    });
                    
                    xhr.addEventListener("error", (e) => {
                        console.error("Network error during upload:", e);
                        reject(new Error("Network error occurred during upload to S3"));
                    });
                    
                    xhr.addEventListener("abort", () => {
                        reject(new Error("Upload was aborted"));
                    });
                    
                    // Use POST method for presigned POST
                    xhr.open("POST", uploadURL);
                    
                    // Don't set Content-Type header - let the browser set it with boundary for FormData
                    // xhr.setRequestHeader("Content-Type", "multipart/form-data"); // DON'T do this
                    
                    // Send the FormData
                    xhr.send(formData);
                });
                
                showStatus("Upload successful! Processing image...", "success");
                
                // Step 3: Wait for the Lambda function to process the image (create thumbnail)
                await new Promise(resolve => setTimeout(resolve, 3000));
                
                // Step 4: Refresh the gallery to show the new image
                await loadGallery();
                
                showStatus("Image uploaded and processed successfully!", "success");
                
                // Clear the file input
                fileInput.value = '';
                
            } catch (error) {
                console.error("Upload error:", error);
                showStatus("Upload failed: " + error.message, "error");
            } finally {
                // Re-enable the upload button
                uploadButton.disabled = false;
                
                // Hide progress bar after a delay
                setTimeout(() => {
                    progressContainer.style.display = "none";
                    progressBar.style.width = "0%";
                    progressText.textContent = "0%";
                }, 3000);
            }
        }

        function showStatus(message, type) {
            const statusDiv = document.getElementById("status");
            statusDiv.textContent = message;
            statusDiv.style.display = "block";
            statusDiv.className = "status " + type;
        }

        async function loadGallery() {
            const gallery = document.getElementById("gallery");
            gallery.innerHTML = "<p>Loading images...</p>";
            
            try {
                // Fetch thumbnails from our API
                const response = await fetch(`${apiEndpoint}/thumbnails`, {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    },
                    mode: "cors" // Explicitly set CORS mode
                });
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Failed to load images (${response.status})`);
                }
                
                const apiData = await response.json();
                
                // Parse the body if it's a string (which it appears to be based on your API response)
                let data;
                if (typeof apiData.body === 'string') {
                    data = JSON.parse(apiData.body);
                } else {
                    data = apiData.body;
                }
                
                
                if (data && data.thumbnails && data.thumbnails.length > 0) {
                    gallery.innerHTML = "";
                    
                    // Sort thumbnails by last modified date (newest first)
                    data.thumbnails.sort((a, b) => {
                        return new Date(b.lastModified) - new Date(a.lastModified);
                    });
                    
                    // Display thumbnails
                    data.thumbnails.forEach(thumbnail => {
                        const imgContainer = document.createElement("div");
                        imgContainer.className = "thumbnail";
                        
                        // Extract original filename without the thumb- prefix
                        const originalName = thumbnail.fileName.startsWith("thumb-") 
                            ? thumbnail.fileName.substring(6) 
                            : thumbnail.fileName;
                        
                        // Format the file size
                        const fileSize = formatFileSize(thumbnail.size);
                        
                        // Create image element with error handling
                        const img = document.createElement("img");
                        img.alt = originalName;
                        img.loading = "lazy";
                        img.onerror = function() {
                            this.onerror = null;
                            this.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='150' height='150' viewBox='0 0 150 150'%3E%3Crect width='150' height='150' fill='%23f5f5f5'/%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='14' text-anchor='middle' dominant-baseline='middle' fill='%23999'%3EImage Error%3C/text%3E%3C/svg%3E";
                        };
                        img.src = thumbnail.url;
                        
                        imgContainer.appendChild(img);
                        imgContainer.innerHTML += `
                            <p title="${originalName}">${truncateFilename(originalName, 20)}</p>
                            <p>${fileSize}</p>
                        `;
                        
                        gallery.appendChild(imgContainer);
                    });
                } else {
                    gallery.innerHTML = "<p>No images yet. Upload some!</p>";
                }
            } catch (error) {
                gallery.innerHTML = `<p>Error loading images: ${error.message}</p>`;
            }
        }
        
        // Helper function to truncate long filenames
        function truncateFilename(filename, maxLength) {
            if (filename.length <= maxLength) return filename;
            
            const extension = filename.split('.').pop();
            const nameWithoutExt = filename.substring(0, filename.length - extension.length - 1);
            
            if (nameWithoutExt.length <= maxLength - 3) return filename;
            
            return nameWithoutExt.substring(0, maxLength - 3) + '...' + (extension ? '.' + extension : '');
        }
        
        // Helper function to format file size
        function formatFileSize(bytes) {
            if (bytes < 1024) return bytes + " B";
            else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
            else return (bytes / 1048576).toFixed(1) + " MB";
        }

        // Load gallery when page loads
        window.onload = loadGallery;
    </script>
</body>
</html>
```
2. Replace `your-api-id` and `your-region` in the `apiEndpoint` variable with your actual API Gateway ID and region

### Step 16: Host the Web Interface in a Production Environment

#### Option 1: Host in CloudFront with S3 Origin (Recommended for Production)

1. Navigate to **S3** service
2. Create a new bucket for the website (e.g., `photo-sharing-website-yourname`)
3. Upload your `index.html` file to this bucket
4. **DO NOT** make the bucket public or enable static website hosting

5. Navigate to **CloudFront** service
6. Click **Create Distribution**
7. Configure the distribution:
   - Origin Domain: Select your website S3 bucket
   - Origin Access: Select **Origin access control settings (recommended)**
   - Create a new OAC: Click **Create control setting**
   - Default cache behavior: 
     - Viewer protocol policy: **Redirect HTTP to HTTPS**
     - Allowed HTTP methods: **GET, HEAD, OPTIONS**
     - Cache policy: **CachingOptimized**
     - Origin request policy: **CORS-S3Origin**
   - Web Application Firewall (WAF): **Enable security protections**
   - Default root object: `index.html`
   - Standard logging: **On** (recommended for production)
8. Click **Create distribution**
9. After the distribution is created, copy the policy provided by CloudFront
10. Go back to your S3 bucket, navigate to the **Permissions** tab, and update the bucket policy with the CloudFront policy
11. Access your website using the CloudFront domain name (e.g., `d1234abcdef.cloudfront.net`)

#### Option 2: Host with AWS Amplify (Alternative for Production)

1. Navigate to **AWS Amplify** service
2. Click **New app** > **Host web app**
3. Select **Deploy without Git provider** (for production, consider connecting to a Git repository for CI/CD)
4. Click **Continue**
5. Enter your app name (e.g., `PhotoSharingApp`)
6. Drag and drop your `index.html` file (and any other assets)
7. Click **Save and deploy**
8. Configure custom domain (recommended for production):
   - Go to **Domain management**
   - Click **Add domain**
   - Enter your domain name and follow the verification steps
9. Enable branch protection and access control for production environments

### Step 17: Set Up CloudWatch Monitoring and Alarms

1. Navigate to **CloudWatch** service
2. Create a dashboard for your application:
   - Click **Dashboards** > **Create dashboard**
   - Name it `PhotoSharingAppDashboard`
   - Add widgets for Lambda metrics, S3 metrics, and API Gateway metrics

3. Set up alarms for Lambda errors:
   - Click **Alarms** > **Create alarm**
   - Select **Lambda** > **By Function Name** > Your Lambda function
   - Select the metric **Errors**
   - Define the threshold (e.g., >= 1 for 5 consecutive datapoints)
   - Configure notification actions (SNS topic)
   - Name the alarm `LambdaErrorsAlarm`

4. Set up alarms for API Gateway 5xx errors:
   - Click **Alarms** > **Create alarm**
   - Select **API Gateway** > **By API Name** > Your API
   - Select the metric **5xx Error**
   - Define the threshold (e.g., >= 1 for 3 consecutive datapoints)
   - Configure notification actions (SNS topic)
   - Name the alarm `APIGateway5xxAlarm`

5. Create a log metric filter for Lambda timeouts:
   - Go to **Logs** > **Log groups**
   - Select your Lambda function's log group
   - Click **Actions** > **Create metric filter**
   - Filter pattern: `Task timed out`
   - Name the metric filter `LambdaTimeouts`
   - Create an alarm based on this metric

### Step 18: Implement Security Best Practices

1. **Enable AWS WAF for API Gateway**:
   - Navigate to **WAF & Shield** service
   - Click **Create web ACL**
   - Name it `PhotoSharingAPIProtection`
   - Add AWS managed rules (e.g., Core rule set, Amazon IP reputation list)
   - Associate the web ACL with your API Gateway

2. **Set up AWS Config for compliance monitoring**:
   - Navigate to **Config** service
   - Enable AWS Config
   - Add rules for S3 bucket security (e.g., s3-bucket-ssl-requests-only, s3-bucket-logging-enabled)

3. **Implement resource tagging**:
   - Add consistent tags to all resources (e.g., Project=PhotoSharing, Environment=Production)
   - Use AWS Tag Editor to ensure consistent tagging

4. **Set up AWS CloudTrail**:
   - Navigate to **CloudTrail** service
   - Create a trail that logs all API calls
   - Store logs in a dedicated S3 bucket with appropriate retention policies

### Step 19: Implement Disaster Recovery

1. **Set up S3 Cross-Region Replication**:
   - Go to your source and thumbnail S3 buckets
   - Click on the **Management** tab
   - Click **Create replication rule**
   - Configure replication to a bucket in another AWS region
   - Enable versioning on both source and destination buckets

2. **Create backup plans with AWS Backup**:
   - Navigate to **AWS Backup** service
   - Create a backup plan for your resources
   - Set appropriate backup frequency and retention periods
   - Include your Lambda functions, API Gateway configurations, and S3 buckets

3. **Document recovery procedures**:
   - Create a runbook for disaster recovery scenarios
   - Include steps to restore from backups
   - Test the recovery procedures regularly

## Troubleshooting

### Common Issues and Solutions

1. **Lambda function fails to create thumbnails**
   - Check Lambda function logs in CloudWatch for specific error messages
   - Verify IAM permissions for S3 access (both read from source and write to target)
   - Ensure the PIL/Pillow layer is correctly configured and compatible with your runtime
   - Check if the image format is supported by PIL/Pillow
   - Verify that Lambda has sufficient memory and timeout settings for processing large images

2. **API Gateway returns 5xx errors**
   - Check Lambda function logs for errors
   - Verify that the Lambda integration is correctly configured
   - Check that the request and response mappings are correct
   - Ensure CORS is properly configured if requests come from a browser

3. **CORS errors in the frontend**
   - Ensure API Gateway CORS is properly configured and the API is redeployed after changes
   - Check that S3 bucket CORS settings include all necessary headers and methods
   - Verify that Lambda functions return proper CORS headers in all responses (including error responses)
   - Use browser developer tools (Network tab) to identify which specific requests are failing
   - For presigned URLs, ensure no custom headers are added that would trigger CORS preflight requests
   - If using CloudFront, ensure the distribution has proper CORS settings in the cache policy

4. **Presigned URLs not working**
   - Verify that the URL hasn't expired (default is 5 minutes)
   - Check that the content type matches what was specified when generating the URL
   - Ensure the S3 bucket policy allows the actions specified in the presigned URL
   - Verify that the user has permission to generate presigned URLs

4. **CloudFront not serving updated content**
   - Create an invalidation to clear the CloudFront cache
   - Check the origin settings to ensure they point to the correct S3 bucket
   - Verify that the OAC (Origin Access Control) is correctly configured

5. **S3 trigger not invoking Lambda**
   - Verify that the trigger is correctly configured for the right event types
   - Check that the Lambda function has permission to be invoked by S3
   - Look for any error messages in CloudTrail logs related to S3 event notifications

## Performance Optimization

1. **Implement CloudFront for image delivery**:
   - Create a CloudFront distribution with your thumbnail bucket as the origin
   - Configure appropriate cache behaviors and TTLs
   - Use Origin Access Control to secure your S3 bucket

2. **Optimize Lambda performance**:
   - Increase memory allocation to improve CPU performance
   - Implement concurrent processing for batch uploads
   - Use Lambda Provisioned Concurrency for consistent performance

3. **Implement image compression**:
   - Modify the Lambda function to compress images before storing
   - Consider using WebP format for better compression ratios
   - Implement responsive images with multiple resolutions

## Security Enhancements

1. **Add user authentication** using Amazon Cognito:
   - Create a user pool for authentication
   - Implement token-based authorization for API Gateway
   - Add user-specific folders in S3 for image isolation

2. **Implement content moderation**:
   - Use Amazon Rekognition to detect inappropriate content
   - Create a moderation workflow for uploaded images
   - Implement automatic rejection of policy-violating content

3. **Enhance data protection**:
   - Enable S3 object encryption with AWS KMS
   - Implement bucket policies to enforce encryption
   - Use VPC endpoints for private network communication

## Conclusion

You have successfully implemented a production-ready serverless photo sharing application using AWS services. This application securely handles image uploads via presigned URLs, automatically generates thumbnails using Lambda, and serves content through a secure API Gateway and CloudFront distribution. The monitoring, security, and disaster recovery measures ensure the application is robust and reliable for production use.

By following these best practices, your photo sharing application is now:
- Secure: Using presigned URLs, WAF protection, and proper IAM permissions
- Scalable: Leveraging serverless architecture to handle varying loads
- Reliable: With monitoring, alarms, and disaster recovery procedures in place
- Cost-effective: Only paying for the resources you use
- Maintainable: With proper logging, monitoring, and documentation