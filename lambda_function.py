import json
import boto3
import numpy as np
import cv2
import tensorflow as tf
import tensorflow_hub as hub
from botocore.exceptions import NoCredentialsError

# Load the pre-trained FaceNet model from TensorFlow Hub
model_url = "https://tfhub.dev/google/facenet/1"
model = hub.load(model_url)

# Function to preprocess the image
def preprocess_image(image_data):
    np_array = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (160, 160))
    img = img.astype(np.float32)
    img = (img / 127.5) - 1.0  # Normalize to [-1, 1]
    return img

# Function to get the embedding vector from the image
def get_embedding(image_data):
    img = preprocess_image(image_data)
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    embedding = model(img)
    return embedding.numpy().tolist()  # Convert the result to a list

# Lambda handler function
def lambda_handler(event, context):
    # Initialize S3 client
    s3 = boto3.client('s3')

    try:
        # Get bucket name and image key from the event
        bucket = event['bucket']
        key = event['key']
        
        # Fetch the image from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()

        # Get the embedding vector
        embedding_vector = get_embedding(image_data)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'embedding_vector': embedding_vector
            })
        }
    except NoCredentialsError:
        return {
            'statusCode': 403,
            'body': json.dumps({
                'error': 'No AWS credentials found'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
