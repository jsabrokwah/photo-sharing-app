# Sample Images Directory

This directory contains sample images for testing the image processing functionality of the application.

## Purpose

- Provides test images for verifying the image processing pipeline
- Demonstrates supported image formats and use cases
- Helps with local development and testing

## Included Files

- `sample.png`: Sample image for testing the image processing pipeline

## Usage Guidelines

1. **Testing New Uploads:**
   - Use these images to test the upload functionality through the web interface
   - Verify thumbnail generation works correctly
   - Check presigned URL generation and access

2. **Development Testing:**
   - Test image format handling
   - Verify thumbnail quality and sizing
   - Check transparent image handling

3. **Supported Formats:**
   - JPEG/JPG
   - PNG (including transparency)
   - Other formats that PIL/Pillow can process

## Best Practices

1. Keep test images under 10MB (upload limit)
2. Include various image formats for comprehensive testing
3. Test both transparent and non-transparent images
4. Include images with different aspect ratios
5. Document any special test cases or edge cases

## Notes

- Images in this directory are for testing purposes only
- Do not store sensitive or production images here
- Regular cleanup of test images is recommended
