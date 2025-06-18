FROM python:3.9-slim

WORKDIR /app

# Install zip utility
RUN apt-get update && apt-get install -y zip && apt-get clean

# Copy requirements file if needed
#COPY src/requirements.txt .

# Install dependencies
#RUN pip install -r requirements.txt
RUN pip install Pillow

# Create directory structure for the layer
RUN mkdir -p /app/python/lib/python3.9/site-packages/

# Copy instructions for building the layer
COPY build-layer.sh /app/
RUN chmod +x /app/build-layer.sh

ENTRYPOINT ["/app/build-layer.sh"]