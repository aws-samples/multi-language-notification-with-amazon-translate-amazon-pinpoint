import boto3
import json
import os
import logging
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    
    client = boto3.client('stepfunctions')
    
    message = event['Records']
    payload = message[0]['body']
    
    response = client.start_execution(
            stateMachineArn=os.environ['StateMachineARN'],
            input=json.dumps(payload))
  
    return {
        'statusCode': 200,
        'body': "Successful"
    }   
