#!/bin/bash
set -e

echo "Building PillowLayer for AWS Lambda..."

# Install Pillow into the Python directory structure
pip install Pillow -t /app/python/lib/python3.9/site-packages/

# Create the layer zip file
cd /app
zip -r pillow_layer.zip python

echo "PillowLayer has been created as pillow_layer.zip"
echo "The layer is now ready to be uploaded to AWS Lambda"

# Keep container running if requested
if [ "$1" = "keep-alive" ]; then
  echo "Container will remain running. Use Ctrl+C to stop."
  tail -f /dev/null
fi