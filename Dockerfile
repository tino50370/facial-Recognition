# Use the Amazon Linux 2 base image
FROM public.ecr.aws/lambda/python:3.8

# Copy function code and requirements.txt
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt ./

# Install the required dependencies
RUN pip install -r requirements.txt

# Command to run the Lambda function. Specifies the entry point for the AWS Lambda function within the Docker container.
#It contains the name of the python file (lambda_function) containing the lambda function code and the name of the function defined within the lambda_function.py file that serves as the entry point for your Lambda function. AWS Lambda will call this function when an event is triggered.
CMD ["lambda_function.lambda_handler"]
