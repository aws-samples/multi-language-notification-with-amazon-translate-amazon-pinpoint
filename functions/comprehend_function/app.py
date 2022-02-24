import boto3
import json
import os
import logging
import time
from botocore.exceptions import ClientError
region = os.environ.get('AWS_REGION')

def lambda_handler(event, context):
    
    print('message validity check')
    text =  event['englishTxt']
    
    comprehend = boto3.client('comprehend', region_name=region)

    sentiments = comprehend.batch_detect_sentiment(TextList=[text], LanguageCode='en')
    neutral_score = sentiments['ResultList'][0]['SentimentScore']['Neutral']
    print('sentiments score', neutral_score)
    
    pass_flag = True
    #If the score is less than 50%, message will go to review for support manager approval.
    fail_msg = ''
    if neutral_score < 0.5 :
        pass_flag = False 
        fail_msg = '**Original message:** \n"' +  text + '"\n\n This announcement message is not meeting the company standards, please revisit the message and resend it.'

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "input" : event,
        "message_validation": pass_flag,
        "neutral_score" : round(neutral_score,2),
        "fail_message" : fail_msg
    }
    