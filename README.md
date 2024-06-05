# Facial Recognition - AWS Lambda

This repository contains an AWS Lambda function that encodes facial images stored in an S3 bucket into feature vectors using the FaceNet model. The feature vectors can be used for facial recognition and other machine learning applications.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Setup](#setup)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Cloning the Repository](#2-cloning-the-repository)
  - [3. Creating the Lambda Layer](#3-creating-the-lambda-layer)
  - [4. Creating the ECR Repository](#4-creating-the-ecr-repository)
  - [5. Creating the CodeBuild Project](#5-creating-the-codebuild-project)
  - [6. Starting the Build](#6-starting-the-build)
  - [7. Deploying the Lambda Function](#7-deploying-the-lambda-function)
- [Usage](#usage)
- [Example Event](#example-event)
- [References](#references)

## Overview

This system reads an image file from an S3 bucket, processes the image using the FaceNet model to extract facial features, and returns the resulting vector. The Lambda function leverages TensorFlow and TensorFlow Hub to perform the image processing. We use a Lambda Layer to include TensorFlow and other dependencies, which helps keep the Lambda function deployment package small and speeds up the deployment process.

## Architecture

1. **S3 Bucket**: Stores the image files.
2. **Lambda Function**: Reads the image from S3, processes it using FaceNet, and returns the feature vector.
3. **AWS ECR**: Stores the Docker image for the Lambda function.
4. **AWS CodeBuild**: Builds the Docker image and pushes it to ECR.
5. **AWS Lambda Layer**: Contains TensorFlow and other dependencies.

## Setup

### 1. Prerequisites

- AWS account with necessary permissions to create and manage Lambda functions, S3 buckets, ECR repositories, and CodeBuild projects.
- AWS CLI configured with appropriate credentials (optional if you are planning to use the AWS Console only).

### 2. Cloning the Repository

Clone the repository to your development environment:

```bash
git clone https://github.com/tino50370/facial-Recognition.git
cd facial-Recognition
```

### 3. Creating the Lambda Layer

1. Create a directory for the layer and install the dependencies:

```bash
mkdir lambda-layer
cd lambda-layer
mkdir -p python
pip install tensorflow tensorflow-hub opencv-python-headless -t python/
```

2. Zip the contents of the `lambda-layer` directory:

```bash
zip -r lambda-layer.zip python
```

3. Publish the layer to AWS Lambda:

#### Using AWS CLI:

```bash
aws lambda publish-layer-version --layer-name tensorflow-layer --zip-file fileb://lambda-layer.zip
```

#### Using AWS Console:

    1. Go to the AWS Lambda Console.
    2. Click on "Layers" in the left-hand navigation pane.
    3. Click "Create layer".
    4. Enter a name for the layer (e.g., tensorflow-layer).
    5. Under "Upload a .zip file", click "Upload" and select the `lambda-layer.zip` file from the cloned repository.
    6. Click "Create".

4. Note the ARN of the created layer.


### 4. Creating the ECR Repository

Create an ECR repository to store the Docker image.

#### Using AWS CLI:

```bash
aws ecr create-repository --repository-name face-embedding-encoder
```

Note the repository URI, which will be in the format `AWS_ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/face-embedding-encoder`.

#### Using AWS Console:

1. Go to the Amazon ECR Console.
2. Click on "Create repository".
3. Enter a name for the repository (e.g., face-embedding-encoder).
4. Click "Create repository".
5. Note the repository URI, which will be in the format `AWS_ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/face-embedding-encoder`.

### 5. Creating the CodeBuild Project

Create a CodeBuild project using the Dockerfile and buildspec.yml files included in the cloned repository.

#### Using AWS CLI:

1. Create a CodeBuild project with the following command:

```bash
aws codebuild create-project --name face-embedding-encoder-build \
    --source type=GITHUB,location=https://github.com/tino50370/facial-Recognition \
    --artifacts type=NO_ARTIFACTS \
    --environment type=LINUX_CONTAINER,image=aws/codebuild/standard:4.0,computeType=BUILD_GENERAL1_SMALL,privilegedMode=true \
    --service-role arn:aws:iam::YOUR_ACCOUNT_ID:role/CodeBuildServiceRole
```

2. Ensure that the CodeBuild service role has the AmazonEC2ContainerRegistryFullAccess policy attached:

```bash
aws iam attach-role-policy --role-name CodeBuildServiceRole --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess
```

#### Using AWS Console:

1. Go to the AWS CodeBuild Console.
2. Click on "Create project".
3. Enter a name for the project (e.g., face-embedding-encoder-build).
4. In the "Source" section, select "GitHub" and connect your repository.
5. In the "Environment" section, select "Managed image" and choose the "aws/codebuild/standard:4.0" image. Ensure "Privileged" is checked.
6. In the "Buildspec" section, choose "Use a buildspec file" and ensure it points to the buildspec.yml in the cloned repository.
7. In the "Service role" section, select an existing role or create a new one.
8. Ensure the service role has the AmazonEC2ContainerRegistryFullAccess policy attached:
   - Go to the IAM Console.
   - Select the service role.
   - Attach the policy `AmazonEC2ContainerRegistryFullAccess`.
9. Click "Create build project".

### 6. Starting the Build

Start the build in AWS CodeBuild.

#### Using AWS CLI:

```bash
aws codebuild start-build --project-name face-embedding-encoder-build
```

#### Using AWS Console:

1. Go to the AWS CodeBuild Console.
2. Select the project you created.
3. Click "Start build".
4. Monitor the build process and ensure it completes successfully.

### 7. Deploying the Lambda Function

1. **Create the Lambda Function**

   Create a new Lambda function using the AWS Management Console or CLI. Use the Docker image stored in ECR:

#### Using AWS CLI:

```bash
aws lambda create-function --function-name face-embedding-encoder \
    --package-type Image \
    --code ImageUri=AWS_ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/face-embedding-encoder:latest \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/LambdaExecutionRole \
    --timeout 120 \
    --memory-size 2048
```

#### Using AWS Console:

1. Go to the AWS Lambda Console.
2. Click "Create function".
3. Choose "Container image" as the function code source.
4. Enter a function name (e.g., face-embedding-encoder).
5. For "Container image URI", enter the URI of the Docker image in ECR.
6. Choose or create an execution role with necessary permissions.
7. Set the timeout to 120 seconds and memory size to 2048 MB.
8. Click "Create function".

2. **Add the Lambda Layer**

   Go to the AWS Lambda console, navigate to your function, and add the previously created TensorFlow layer in the "Layers" section.

### Usage

To invoke the Lambda function manually, you can use the following example event:

### Example Event

```json
{
  "bucket": "your-s3-bucket-name",
  "key": "path/to/your/image.jpg"
}
```

You can test the function using the AWS Management Console or the AWS CLI:

#### Using AWS CLI:

```bash
aws lambda invoke --function-name face-embedding-encoder --payload '{"bucket":"your-s3-bucket-name","key":"path/to/your/image.jpg"}' response.json
```

#### Using AWS Console:

1. Go to the AWS Lambda Console.
2. Select your function.
3. Click "Test".
4. Configure a new test event with the example event JSON.
5. Click "Test" to invoke the function.

## References

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/index.html)
- [AWS ECR Documentation](https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html)
- [AWS CodeBuild Documentation](https://docs.aws.amazon.com/codebuild/latest/userguide/welcome.html)
- [TensorFlow Documentation](https://www.tensorflow.org/)
- [OpenCV Documentation](https://docs.opencv.org/)