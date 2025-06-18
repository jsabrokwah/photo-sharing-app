# Building PillowLayer for AWS Lambda

This guide explains how to build a PillowLayer for AWS Lambda using Docker with Python 3.9.

## Prerequisites

- Docker installed on your machine
- AWS CLI configured with appropriate permissions

## Building the PillowLayer

1. Run the build script:

```bash
./build-pillow-layer.sh
```

This script will:
- Build a Docker container with Python 3.9
- Run the container to create the PillowLayer
- Save the layer as `pillow_layer.zip` in the current directory

## Uploading to AWS Lambda

After building the layer, you can upload it to AWS Lambda using the AWS CLI:

```bash
aws lambda publish-layer-version \
  --layer-name PillowLayer \
  --description "Pillow library for image processing" \
  --compatible-runtimes python3.9 \
  --zip-file fileb://pillow_layer.zip
```

Or you can upload it through the AWS Management Console:

1. Go to the AWS Lambda console
2. Navigate to "Layers" in the left sidebar
3. Click "Create layer"
4. Enter "PillowLayer" as the name
5. Upload the `pillow_layer.zip` file
6. Select Python 3.9 as the compatible runtime
7. Click "Create"

## Using the Layer with Your Lambda Function

To use this layer with your Lambda function:

1. Go to your Lambda function in the AWS console
2. Scroll down to the "Layers" section
3. Click "Add a layer"
4. Select "Custom layers"
5. Select "PillowLayer" and the version you uploaded
6. Click "Add"

Your Lambda function can now import and use the Pillow library.