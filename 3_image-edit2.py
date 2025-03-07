import boto3
import json
import base64
import io
from PIL import Image

# Initialize Amazon Bedrock client
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

s3_client = boto3.client("s3")

# Define the model ID
model_id = "amazon.nova-canvas-v1:0"

# Function to generate an image using Nova Canvas
def generate_image(prompt):
    """Generates an image from a text prompt."""
    payload = json.dumps({
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": prompt
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": 512,
            "width": 512,
            "cfgScale": 8.0,
            "seed": 42
        }
    })
    
    response = bedrock_client.invoke_model(
        modelId=model_id, body=payload, accept="application/json", contentType="application/json"
    )
    result = json.loads(response["body"].read())
    base64_image = result.get("images")[0]
    
    # Convert base64 to image
    image_bytes = base64.b64decode(base64_image)
    return Image.open(io.BytesIO(image_bytes)), base64_image, image_bytes  # Return both image and base64 data

# Function to edit an image using IMAGE_VARIATION
def edit_image(base64_original, edit_prompt, similarity=0.75):
    """Edits an existing image using Nova Canvas IMAGE_VARIATION."""
    payload = json.dumps({
        "taskType": "IMAGE_VARIATION",  # Specifies the type of task (image variation)
        "imageVariationParams": {
            "images": [base64_original],  # Input image(s) encoded in Base64 format
            "similarityStrength": similarity,  # Degree of variation applied (higher = more change)
            "text": edit_prompt,  # Instruction on how to modify the image
            "negativeText": "blurry, low quality, distorted"  # Prevents unwanted effects
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,  # Specifies how many images to generate
            "height": 512,  # Output image height
            "width": 512,  # Output image width
            "cfgScale": 7.0  # Controls how much the model follows the prompt (higher = more strict)
        }
    })

    response = bedrock_client.invoke_model(
        modelId=model_id, body=payload, accept="application/json", contentType="application/json"
    )
    result = json.loads(response["body"].read())
    base64_edited = result.get("images")[0]

    # Convert base64 to edited image
    edited_image_bytes = base64.b64decode(base64_edited)
    return Image.open(io.BytesIO(edited_image_bytes)), edited_image_bytes

# Step 1: Generate an image
prompt = "boy standing in park with red tshirt"
original_image, base64_original, image_bytes = generate_image(prompt)
original_image.show()  # Show original image in VS Code

# Step 2: Edit the image using IMAGE_VARIATION
edit_prompt = "Make the color of tshirt dark blue"
edited_image, edited_image_bytes = edit_image(base64_original, edit_prompt)
edited_image.show()  # Show edited image in VS Code

# Define S3 bucket details
bucket_name = "jeet-store-generated-image"

image_filename1 = f"generated_images/titan_{1}.png"
image_filename2 = f"edited_images/titan_{1}.png"

# Upload image directly to S3
s3_client.put_object(
    Bucket=bucket_name,
    Key=image_filename1,
    Body=image_bytes,
    ContentType="image/png",  # Ensure the image displays in browser
    #ACL="public-read"  # Make it publicly accessible
)
s3_client.put_object(
    Bucket=bucket_name,
    Key=image_filename2,
    Body=edited_image_bytes,
    ContentType="image/png",  # Ensure the image displays in browser
    #ACL="public-read"  # Make it publicly accessible
)

# Generate the S3 public URL
s3_url = f"https://{bucket_name}.s3.amazonaws.com/{image_filename1}"
print(f"The generated image is available at: {s3_url}")

s3_url = f"https://{bucket_name}.s3.amazonaws.com/{image_filename2}"
print(f"The Edited image is available at: {s3_url}")

#   Task Type                         	Description
# "IMAGE_VARIATION"	            Generates new variations of an input image.
# "TEXT_TO_IMAGE"	            Creates an image based on a text prompt.
# "IMAGE_INPAINTING"	        Modifies or fills in missing parts of an image.
# "SUPER_RESOLUTION"	        Enhances the resolution of a given image.
# "OBJECT_REMOVAL"	            Removes unwanted objects from an image.
# "STYLE_TRANSFER"	            Applies artistic styles to an image.
# "IMAGE_CAPTIONING"        	Generates descriptive captions for an image.
# "DEPTH_ESTIMATION"	        Predicts depth information from an image.
# "SEGMENTATION"	            Identifies and segments objects in an image.
# "FACE_SWAP"	                Replaces faces in an image with a different face.
# "BACKGROUND_REMOVAL"      	Removes the background from an image.