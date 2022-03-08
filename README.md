# Build a multi-language notification system using Amazon Translate and Amazon Pinpoint

## Overview

This project demonstrates how to develop a simple serverless application using AWS services to send notifications to the users or customers based on their preferred language and way of communication. This project contains source code and supporting files for a multi-language notification system using Amazon Translate and Amazon Pinpoint that you can deploy with the SAM CLI.

Use the following git command to download the source code to deploy and test:

```bash
git clone git@github.com:aws-samples/multi-language-notification-with-amazon-translate-amazon-pinpoint.git
cd multi-language-notification-with-amazon-translate-amazon-pinpoint
```

The downloaded code includes the following files and folders:

- **functions** - This directory contains the code for the application's Lambda functions.
- **statemachine** - This directory contains the definition for the state machine that orchestrates the multi-language notification workflow.
- **template.yaml** - A template that defines the application's AWS resources.

This application creates a multi-language notification workflow to translate text into various languages, converts it into voice and sms, and sends a notification to its users. It demonstrates the power of Step Functions to orchestrate Lambda functions, Amazon Translate, and Amazon Pinpoint to form complex and robust workflows.

Amazon Translate is a text translation service that uses advanced machine learning technologies to provide high-quality translation on demand. You can use Amazon Translate to translate unstructured text documents or to build applications that work in multiple languages.

Amazon Pinpoint is a flexible and scalable outbound and inbound marketing communications service. You can connect with customers over channels like email, SMS, push, voice or in-app messaging. Amazon Pinpoint is easy to set up, easy to use, and is flexible for all marketing communication scenarios. 

These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

**Note**: 
- Amazon Translate has costs associated with the service after the Free Tier usage, please see the [Amazon Translate pricing page](https://aws.amazon.com/translate/pricing/) for details.
- Amazon Pinpoint has costs associated with the service after the Free Tier usage, please see the [Amazon Pinpoint pricing page](https://aws.amazon.com/pinpoint/pricing/) for details.

## Solution Architecture
![Architecture Diagram](scripts/solution4readme.png)

## Setup and deploy the application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing serverless applications.

### Prerequisites 

* AWS CLI - Installed and Configured with a valid profile [Install the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* The Bash shell. For Linux and macOS, this is included by default. In Windows 10, you can install the [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10) to get a Windows-integrated version of Ubuntu and Bash.

Before deploy the solution, first complete the Pinpoint setup for email, sms, and voice communication.

### Step 1: Register Email and Phone number using Amazon Pinpoint console

In the the last step of the workflow it invokes Amazon Pinpoint service from the Lambda function to send the communication. Here are the steps to configure the Pinpoint service.

- In the AWS Management console, choose the Pinpoint service from the Services menu or search bar.
- Select the region you have deployed the application in. 
- Enter a name to create project.
- Configure Email, SMS, and Voice features:

    - **[Email setup](https://docs.aws.amazon.com/pinpoint/latest/userguide/channels-email-setup.html)** 
        - Choose **Configure** in **Email** and enter a valid email address in the set up Email page. 
        - Choose the verify button the verify the email address. After you verify the link in your email, choose the **Save** button.
        - **Note** - You will have to register and verify both the recipient and the sender email addresses in Pinpoint.
    - **[SMS and Voice setup](https://docs.aws.amazon.com/pinpoint/latest/userguide/channels-sms.html)** 
        - In the left navigation pane of the console, choose **SMS and voice**, and request phone numbers for sending SMS and voice messages.
        - **Note** - Make sure the **Enable the SMS channel for this project** is checked in the **Edit SMS and Voice settings** page.

### Deploy the application
Run the following command to deploy the template. The command below will package and deploy your application to AWS, with a series of prompts:

    ```bash
    sam deploy --guided
    ```

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

### Update environment variables for the Pinpoint Lambda function

The pinpoint_function has configuration variables that point to the Amazon Pinpoint project and also the phone numbers and email ids that you have setup in the above steps.

- In the AWS Management Lambda console, choose the Pinpoint Function and then choose the Configuration tab. Choose the Environment variables section and update the below variables with the values from the Amazon Pinpoint project console.

    - APP_ID -  the Pinpoint Project ID
    - CALLER_ID - the phone number you requested in Pinpoint
    - ORIG_NUMBER - the phone number you requested in Pinpoint
    - SENDER_EMAIL_ID - the email id you registered and verified in Pinpoint

Here is a screenshot of the environment variables for the Pinpoint Lambda function after updates:

![Pinpoint Diagram](scripts/pinpointvariables.png)

### Setup DynamoDB records to test the application

You will need to setup some user records in the DynamoDB table. The application will use these records for the preferred way of communication and also the users corresponding email address and phone numbers. So, make sure you enter a valid email address and phone number to receive the messages.

```sql
INSERT INTO user_profiles VALUE 
{  
    'event_id': 'Apr142022',
    'user_id': 'ui101',
    'first_name' : 'John',
    'email': 'xxx@example.com', --A valid email id to receive email
    'language' : 'en',
    'phone': '+11235550101', --A valid phone number number to receive the voice prompt
    'preference': 'email',
    'phoneme': 'en-US'
}

INSERT INTO user_profiles VALUE 
{
    'event_id': 'Apr142022',
    'user_id': 'ui102',
    'first_name' : 'Mary',
    'email': 'foo@example.com', --A valid email id to receive email
    'language' : 'de',
    'phone': '+11235550191', --A valid phone number number to receive the voice prompt
    'preference': 'sms',
    'phoneme': 'de-DE'
}

INSERT INTO user_profiles VALUE 
{  
    'event_id': 'Apr142022',
    'user_id': 'ui103',
    'first_name' : 'Arnav',
    'email': 'foo@example.com', --A valid email id to receive email
    'language' : 'fr',
    'phone': '+11235550190', --A valid phone number number to receive the voice prompt
    'preference': 'voice',
    'phoneme': 'fr-FR'
}
```

### Copy the API Gateway Endpoint URL

Copy API Gateway endpoint url from the sam deploy console or copy from AWS CloudFormation MLNStack output tab.

### Test the application

You are now ready to test your application!! You can test it using the curl command. 

Here is a sample json object to post in the body:

```json
{
    "englishTxt" : "The company is adding a new item to the menu, this will go live by May 10th. Please ensure you are prepared for this change and plan out accordingly.",
    "eventId": "Apr142022"
}
```

Here is the curl command to use:

```bash
curl -d '{json}' -H 'Content-Type: application/json' {API_GATEWAY_ENDPOINT}
```

You should receive a message back from the SQS queue similar to below:

```json
{
    "SendMessageResponse": {
        "ResponseMetadata": {
            "RequestId": "19809b83-46cf-5917-b30d-c11fd0c2d59c"
        },
        "SendMessageResult": {
            "MD5OfMessageAttributes": null,
            "MD5OfMessageBody": "fce2c5d78c337184743e5213ee76c92b",
            "MD5OfMessageSystemAttributes": null,
            "MessageId": "bbdeefe6-805b-4206-8dba-543f4571ce92",
            "SequenceNumber": null
        }
    }
}
```


### Result

You will receive a phone call, an email, and a voice message in various languages for the above message posted through the curl command. You can check the Step Functions state machine event that processed this message in the AWS console, and will see the workflow event in a succeeded state if all the above steps are setup correctly. 

Here is a screenshot of how the state machine workflow looks for a successfully processed message:

![StepFunctionsOutput Diagram](scripts/StepFunctionsoutput.png)

### Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

- Pinpoint clean up:
    - Open AWS Pinpoint console, and select the project. From the left navigation, click on Settings and General settings, click **Delete project**. Confirm again to delete the project.
    - Go to **Email**, select email identity and click **Remove email identity**
    - Go to **SMS and voice**, click on **Phone numbers**, select the numbers and remove

- Delete rest of resources with following command

```bash
aws cloudformation delete-stack --stack-name replace_with_mln_stack_name
```

### Blog Reference
[Building multi-language notification system using Amazon Translate and Amazon Pinpoint](https://aws.amazon.com/blogs/) 

## Security
See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.