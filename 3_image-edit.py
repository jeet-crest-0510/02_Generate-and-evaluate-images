import boto3
import base64
import json
from PIL import Image
import io

def edit_image_with_bedrock(input_image_path, prompt, strength=0.8):
    # Create a Bedrock Runtime client
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

    # Set the model ID for Stable Diffusion XL
    model_id = 'stability.stable-diffusion-xl-v1'

    # Open and resize the input image
    with Image.open(input_image_path) as img:
        img = img.resize((512, 512))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

    # Construct the request payload
    request_payload = {
        "text_prompts": [{"text": prompt}],
        "init_image": img_str,
        "image_strength": strength,
        "steps": 40,
        "cfg_scale": 7,
        "seed": 42
    }

    # Invoke the model
    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(request_payload)
    )

    # Process the response
    response_body = json.loads(response['body'].read())
    output_image_data = base64.b64decode(response_body['artifacts'][0]['base64'])

    # Save the output image
    output_image_path = 'edited_image.png'
    with open(output_image_path, 'wb') as f:
        f.write(output_image_data)

    print(f"Edited image saved as {output_image_path}")

# Example usage
input_image_path = 'output/titan_297359277.png'
prompt = "Add Tiger cubs with the Tiger"
edit_image_with_bedrock(input_image_path, prompt)


# import base64
# import boto3
# import json
# import random

# # Create AWS clients
# bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
# s3_client = boto3.client("s3")

# # Set model ID
# model_id = "amazon.titan-image-generator-v1"

# # User input for text prompt
# prompt = input("Enter your image modification description: ")

# # S3 details
# bucket_name = ""
# input_image_key = "output/titan_297359277.png" #"generated_images/titan_297359277.png "  # Existing image in S3
# output_image_key = f"modified_images/titan_modified_{random.randint(1000, 9999)}.png"

# # Generate a random seed
# seed = random.randint(0, 2147483647)

# # Generate pre-signed URL for input image
# input_image_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': input_image_key}, ExpiresIn=3600)

# # Format the request payload
# request_payload = {
#     "taskType": "IMAGE_VARIATION",
#     "imageVariationParams": {
#         "text": prompt,
#         "image": input_image_url
#     },
#     "imageGenerationConfig": {
#         "numberOfImages": 1,
#         "quality": "standard",
#         "cfgScale": 8.0,
#         "height": 512,
#         "width": 512,
#         "seed": seed,
#     },
# }

# # Convert request to JSON
# request = json.dumps(request_payload)

# # Invoke the model
# response = bedrock_client.invoke_model(modelId=model_id, body=request, contentType="application/json", accept="application/json")

# # Decode the response body
# model_response = json.loads(response["body"].read())

# # Extract image data
# base64_image_data = model_response["images"][0]
# image_data = base64.b64decode(base64_image_data)

# # Upload modified image to S3
# s3_client.put_object(
#     Bucket=bucket_name,
#     Key=output_image_key,
#     Body=image_data,
#     ContentType="image/png"
# )

# # Generate public URL for the modified image
# output_image_url = f"https://{bucket_name}.s3.amazonaws.com/{output_image_key}"
# print(f"The modified image is available at: {output_image_url}")
