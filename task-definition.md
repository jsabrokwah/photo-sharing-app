
# Lab Instructions: Building a Photo Sharing App with AWS S3 & Lambda for Image Resizing

## Objective
By the end of this lab, you will:
- Set up an S3 bucket for storing uploaded photos
- Configure an AWS Lambda function that automatically resizes images into thumbnails when uploaded to S3
- Set up an API Gateway (optional) to serve images
- Create a simple front-end web app to upload and display images

## Prerequisites
Before starting, make sure you have:
- An AWS account with permissions for S3, Lambda, IAM, and API Gateway
- Node.js and AWS CLI installed on your system
- Basic knowledge of JavaScript, AWS services, and HTML/CSS

## Step 1: Create an S3 Bucket for Image Uploads
1. Login to AWS Console
2. Navigate to S3 → Click Create Bucket
3. Enter a unique bucket name, e.g., `photo-sharing-app-bucket`
4. Select the AWS region closest to you
5. Disable Block all public access (optional, if public access to images is required)
6. Click Create Bucket

## Step 2: Set Up an S3 Bucket for Thumbnails
1. Create another bucket (e.g., `photo-sharing-thumbnails`)
2. Keep similar settings as the first bucket
3. Ensure it allows read access for the front-end

## Step 3: Create an IAM Role for Lambda
1. Navigate to IAM → Roles → Create Role
2. Choose AWS Service → Lambda
3. Attach the following policies:
   - `AmazonS3FullAccess` (or limit access to your specific S3 buckets)
   - `AWSLambdaBasicExecutionRole`
4. Name the role: `lambda-s3-resizer-role` and Create Role

## Step 4: Create an AWS Lambda Function for Resizing Images
1. Go to AWS Lambda → Create Function
2. Select Author from Scratch
3. Function name: `ImageResizer`
4. Runtime: Python 3.9
5. Execution role: Choose Existing Role → Select `lambda-s3-resizer-role`
6. Click Create Function

### Add Code to Resize Images

Replace the default code with:

```python
import json
import boto3
from PIL import Image
import io

s3 = boto3.client('s3')

def lambda_handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']

    target_bucket = "photo-sharing-thumbnails"
    target_key = f"thumb-{source_key}"

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
```

Click **Deploy**.

## Step 5: Configure S3 Event Trigger for Lambda
1. Go to S3, open `photo-sharing-app-bucket`
2. Go to **Properties** → **Event notifications**
3. Click **Create Event Notification**
4. Name it `ResizeImages`
5. Event Type: Put (for new uploads)
6. Destination: Lambda Function → Select `ImageResizer`
7. Save the event notification

## Step 6: Test the Lambda Function
1. Upload an image to the bucket:
   ```bash
   aws s3 cp sample.jpg s3://photo-sharing-app-bucket/
   ```
2. Check the thumbnails bucket:
   ```bash
   aws s3 ls s3://photo-sharing-thumbnails/
   ```

## Step 7: Set Up API Gateway (Optional - Serving Images Publicly)
1. Go to API Gateway → Create API
2. Choose REST API → New API
3. Name it `PhotoAPI` → Click Create API
4. Click Actions → Create Resource
   - Resource Name: images
   - Resource Path: `/images`
5. Click Actions → Create Method
   - Choose GET → Click the Checkmark
   - Integration Type: AWS Service
   - AWS Region: Select your region
   - AWS Service: S3
   - HTTP Method: GET
   - Bucket Name: `photo-sharing-thumbnails`
   - Path: `{image}`
   - Click Save
6. Deploy the API
   - Click Actions → Deploy API
   - Stage Name: prod
   - Click Deploy
7. Test your API:
   ```bash
   curl https://<your-api-id>.execute-api.<region>.amazonaws.com/prod/images/thumb-sample.jpg
   ```

## Step 8: Build a Simple Front-End Web App

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Photo Sharing App</title>
</head>
<body>
    <h1>Upload an Image</h1>
    <input type="file" id="uploadFile">
    <button onclick="uploadImage()">Upload</button>

    <h2>Gallery</h2>
    <div id="gallery"></div>

    <script>
        async function uploadImage() {
            let fileInput = document.getElementById("uploadFile");
            let file = fileInput.files[0];
            let fileName = encodeURIComponent(file.name);

            let uploadUrl = `https://photo-sharing-app-bucket.s3.amazonaws.com/${fileName}`;

            let response = await fetch(uploadUrl, {
                method: "PUT",
                body: file
            });

            if (response.ok) {
                alert("Uploaded successfully!");
                displayImages();
            }
        }

        async function displayImages() {
            let gallery = document.getElementById("gallery");
            gallery.innerHTML = "";

            let imageUrl = "https://photo-sharing-thumbnails.s3.amazonaws.com/thumb-sample.jpg";
            let imgElement = `<img src="${imageUrl}" width="150" height="150">`;
            gallery.innerHTML += imgElement;
        }

        displayImages();
    </script>
</body>
</html>
```

You can host this HTML file on Amazon S3 (Static Website Hosting) or AWS Amplify.

## Conclusion
You have successfully built a photo-sharing web app that:
- Stores images in S3
- Automatically resizes images using AWS Lambda
- Serves resized images using API Gateway (optional)
- Displays images in a web app

You can improve it by adding:
- User authentication (AWS Cognito)
- Database for metadata (DynamoDB or RDS)
- Mobile app integration
