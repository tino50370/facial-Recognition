# Use the Amazon Linux 2 base image
FROM public.ecr.aws/lambda/python:3.8

# Copy function code and requirements.txt
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt ./

# Install the required dependencies
RUN pip install -r requirements.txt

# Command to run the Lambda function
CMD ["lambda_function.lambda_handler"]
