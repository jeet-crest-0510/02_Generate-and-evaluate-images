import base64
import json
import random

import boto3

# Create a Bedrock Runtime client in the AWS Region of your choice.
client = boto3.client("bedrock-runtime", region_name="us-east-1")
s3_client = boto3.client("s3")

# Set the model ID.
model_id = "amazon.titan-image-generator-v1"

# Get user input for the image generation prompt.
prompt = input("Enter your image description: ")

# Generate a random seed between 0 and 858,993,459
seed = random.randint(0, 858993460)

# Format the request payload using the model's native structure.
native_request = {
    "taskType": "TEXT_IMAGE",
    "textToImageParams": {"text": prompt},
    "imageGenerationConfig": {
        "numberOfImages": 1,
        "quality": "standard",
        "cfgScale": 8.0,
        "height": 512,
        "width": 512,
        "seed": seed,
    },
}

# Convert the native request to JSON.
request = json.dumps(native_request)

# Invoke the model with the request.
response = client.invoke_model(
    modelId=model_id,
    body=request,
    contentType="application/json",
    accept="application/json"
)

# Decode the response body.
model_response = json.loads(response["body"].read())

# Extract the image data.
base64_image_data = model_response["images"][0]

# Decode image data
image_data = base64.b64decode(base64_image_data)

# Define S3 bucket details
bucket_name = "jeet-store-generated-image"

image_filename = f"generated_images/titan_{seed}.png"

# Upload image directly to S3
s3_client.put_object(
    Bucket=bucket_name,
    Key=image_filename,
    Body=image_data,
    ContentType="image/png",  # Ensure the image displays in browser
    #ACL="public-read"  # Make it publicly accessible
)

# Generate the S3 public URL
s3_url = f"https://{bucket_name}.s3.amazonaws.com/{image_filename}"
print(f"The generated image is available at: {s3_url}")

#image_path = f".../{image_filename}"
# # Save image temporarily
# with open(image_path, "wb") as file:
#     file.write(image_data)

# # Upload the image to S3
# s3_client.upload_file(image_path, bucket_name, image_filename)

# # Generate the S3 URL
# s3_url = f"https://{bucket_name}.s3.amazonaws.com/{image_filename}"
# print(f"The generated image is available at: {s3_url}")
