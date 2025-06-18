#!/bin/bash
set -e

echo "Building Docker container for PillowLayer..."
docker build -t pillow-layer-builder .

echo "Running container to build PillowLayer..."
docker run --rm -v $(pwd):/app pillow-layer-builder

echo "PillowLayer has been built and saved to pillow_layer.zip"
echo "You can now upload this layer to AWS Lambda"