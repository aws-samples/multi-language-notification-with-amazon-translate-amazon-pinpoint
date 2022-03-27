import boto3
import json
import os
import logging
import random
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)


region = os.environ.get('AWS_REGION')
user_tbl = os.environ.get('USER_TABLE')
dynamo_url = 'https://dynamodb.'+region+'.amazonaws.com'

origination_number = os.environ.get('ORIG_NUMBER')
caller_id = os.environ.get('ORIG_NUMBER')
app_id = os.environ.get('APP_ID')
sender_email = os.environ.get('SENDER_EMAIL')

def lambda_handler(event, context):
    event_body = event['body']
    
    #Handle emails and voice mails
    recipients = ''
    email_users = 0
    voice_users = 0
       
    polly_client = boto3.client('polly',region_name=region)
    for key, value in event_body.items():
        print('event_id', key)
        event_id = key[:-3]
        lan_code = key[-2:]
        if not recipients :
            recipients = getUsersByEventId(event_id)

        #Send emails for all subscribers for this event and language
        try :
            for recipient in recipients :
                pref = recipient['preference']
                language = recipient['language']
                    
                
                if language == lan_code :

                    first_name = 'User'
                    if 'first_name' in recipient :
                        first_name = recipient['first_name']
                    
                    print('Sending ' + pref + ' for user', recipient['user_id'])
                    if pref == 'voice' :
                        phoneme =  phonemeCode(language)
                        if 'phoneme' in recipient :
                            phoneme = recipient['phoneme']
                        print('Phoneme', phoneme)
                        voices = polly_client.describe_voices(LanguageCode=phoneme)['Voices']
                        voiceId = ''
                        if len(voices) > 0 :
                            voiceId = voices[0]['Id']
                        elif phoneme == 'hi-IN' or pCode == 'en-IN' : 
                            voiceId = 'Aditi'
                        else :
                            voiceId = 'Joanna'
                        sendVoiceMessage(key,value,phoneme,voiceId,recipient['phone'],first_name)
                        voice_users += 1
                    elif pref == 'email' :
                        sendEmail(key,value, recipient['email'],first_name)
                        email_users += 1
                    elif pref == 'sms' : 
                        print('text communication')
                        msg = first_name + ', ' + value
                        sendSMSMessage(key,msg,recipient['phone'])
                    else:
                        print('No communication mode is available for the rater, user_id:', recipient['user_id'])
        except Exception as err:
            logger.exception("Couldn't send message for event id %s and language %s.", event_id, lan_code)
            raise err
        else:
            print(f"Message sent!\Event ID: {event_id}")
                 
    print('Total email recipients for this announcement are',str(email_users))
    print('Total voice recipients for this announcement are',str(voice_users))
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": event_body
    }
        
#Sedning voice messages   
def sendVoiceMessage(event_id, message, language_code, voice_id, dest_number, first_name) :
    ssml_message = (
        "<speak>"
           "" + message + ""
        "</speak>")
    print(f"Sending voice message from {origination_number} to {dest_number}.")
    message_id = send_voice_message(
        boto3.client('pinpoint-sms-voice'), origination_number,
        dest_number, language_code, voice_id, ssml_message)
    print('voice message id', message_id)

#Sedning voice messages    
def send_voice_message(
        sms_voice_client, origination_number, destination_number,
        language_code, voice_id, ssml_message):
    
    try:
        response = sms_voice_client.send_voice_message(
            DestinationPhoneNumber=destination_number,
            OriginationPhoneNumber=origination_number,
            #CallerId=caller_id,
            Content={
                'SSMLMessage': {
                    'LanguageCode': language_code,
                    'VoiceId': voice_id,
                    'Text': ssml_message}})
    except Exception as err:
            logger.exception("Couldn't send message from %s to %s.", origination_number, destination_number)
            raise err
    
    else:
        print(f"Message sent!\nMessage ID: {ssml_message}")
        return response['MessageId']

#Get unique langage codes for the event
def getUsersByEventId(event_id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=dynamo_url)
    
    table = dynamodb.Table(user_tbl)
    response = table.query(
        KeyConditionExpression=Key('event_id').eq(event_id)
    )

    return response['Items']   

#Using pinpoint for emails and voice
def sendEmail(event_id, message, email, first_name):

    # sending email
    SENDER = sender_email
    RECIPIENT = email
    SUBJECT = 'New announcement for the event: ' + event_id
 
    
    # The HTML body of the email.
    BODY_HTML = """<html>
        <head></head>
        <body>
            <h4>New announcement for the up coming event.</h4>
        </body>
        </html>"""            
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses')
    
    # Try to send the email.
    try:
        body = BODY_HTML+'<br><i> Dear ' + first_name + ', <br>'  + message + '</i>'    
        send_email_message(SENDER, [RECIPIENT], CHARSET, SUBJECT, body)
        
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise

def send_email_message(sender, to_addresses, char_set, subject, html_message):
    """
    Sends an email message with HTML and plain text versions.
    
    :param pinpoint_client: A Boto3 Pinpoint client.
    :param app_id: The Amazon Pinpoint project ID to use when you send this message.
    :param sender: The "From" address. This address must be verified in
                   Amazon Pinpoint in the AWS Region you're using to send email.
    :param to_addresses: The addresses on the "To" line. If your Amazon Pinpoint account
                         is in the sandbox, these addresses must be verified.
    :param char_set: The character encoding to use for the subject line and message
                     body of the email.
    :param subject: The subject line of the email.
    :param html_message: The body of the email for recipients whose email clients can
                         display HTML content.
    :param text_message: The body of the email for recipients whose email clients
                         don't support HTML content.
    :return: A dict of to_addresses and their message IDs.
    """
    try:
        pinpoint_client =  boto3.client('pinpoint')
        response = pinpoint_client.send_messages(
            ApplicationId=app_id,
            MessageRequest={
                'Addresses': {
                    to_address: {'ChannelType': 'EMAIL'} for to_address in to_addresses
                },
                'MessageConfiguration': {
                    'EmailMessage': {
                        'FromAddress': sender,
                        'SimpleEmail': {
                            'Subject': {'Charset': char_set, 'Data': subject},
                            'HtmlPart': {'Charset': char_set, 'Data': html_message}}}}})
                            
        for to_address, message in response['MessageResponse']['Result'].items() :
            print('Email Delivery status:', message['DeliveryStatus'])
            
            if(message['DeliveryStatus'] != 'SUCCESSFUL') : 
                print('Failed email message:', message)
            else:
                print('Email sent!')
            
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise

#Sending SMS message to the users
def sendSMSMessage(event_id, message, dest_number) :
    print(f"Sending text messAGE!\Event ID: {event_id}")
    try:
        pinpoint_client =  boto3.client('pinpoint')
        response = pinpoint_client.send_messages(
            ApplicationId=app_id,
            MessageRequest={
                'Addresses': {dest_number: {'ChannelType': 'SMS'}},
                'MessageConfiguration': {
                    'SMSMessage': {
                        'Body': message,
                        'MessageType': 'TRANSACTIONAL',
                        'OriginationNumber': origination_number}}})
    except ClientError:
        logger.exception("Couldn't send message.")
        raise
    else:
        return response['MessageResponse']['Result'][dest_number]['MessageId']

def phonemeCode(languageCode) :
        if languageCode == 'de':
            return "de-DE"
        elif languageCode == 'en':
            return "en-GB"
        elif languageCode == 'es':
            return "es-ES"
        elif languageCode == 'fr':
            return "fr-FR"
        elif languageCode == 'pt':
            return "pt-PT"
        elif languageCode == 'hi':
            return "hi-IN"
        elif languageCode == 'ja':
            return "ja-JP"
        elif languageCode == 'ko':
            return "ko-KR"
        elif languageCode == 'da':
            return "da-DK"
        elif languageCode == 'it':
            return "it-IT"
        elif languageCode == 'da':
            return "da-DK"
        elif languageCode == 'zh':
            return "cmn-CN"
        elif languageCode == 'ru':
            return "ru-RU"
        else:
            return "Unsupported languageCode"