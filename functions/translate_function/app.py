import boto3
import json
import os
import logging
import time
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

region = os.environ.get('AWS_REGION')
user_tbl = os.environ.get('USER_TABLE')

dynamo_url = 'https://dynamodb.'+region+'.amazonaws.com'

def lambda_handler(event, context):
    
    print('translate the message into a different languages')
    event_body = event['input']
    text =  event_body['englishTxt']
    print('Message', text)
    event_id = event_body['eventId']
    
    data = {}
    try:
        #unique languages
        lans = getUniqueLanguageByEvent(event_id)
        print('number of unique language speakers for this event', lans)
        
        translate = boto3.client(service_name='translate', region_name=region, use_ssl=True)
        
        
        data[event_id+'-en'] = text
        
        for ln in lans :
            
            toMsg = translate.translate_text(Text=text, 
                            SourceLanguageCode="en", TargetLanguageCode=ln)
            print('Msg for ' + ln + ': ' + toMsg.get('TranslatedText'))
            
            data[event_id + '-' + ln] = toMsg.get('TranslatedText')
    except Exception as err:
            logger.exception("Couldn't translate message for event id %s.", event_id)
            raise err
    else:
        print(f"Message translation is successful for!\Event ID: {event_id}")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": data
    }

#Get unique langage codes for a given event id
def getUniqueLanguageByEvent(event_id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=dynamo_url)
    
    table = dynamodb.Table(user_tbl)
    print('event id', event_id)
    response = table.query(
        KeyConditionExpression=Key('event_id').eq(event_id)
    )

    lans = []
    for item in response['Items'] :
        lans.append(item['language'])
    lans = sorted(set(lans))
    
    return lans
