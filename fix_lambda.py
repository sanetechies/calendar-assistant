#!/usr/bin/env python3
"""
Fix Lambda function for bhagyesh calendar assistant
"""

import boto3
import json
import time
import zipfile

def fix_lambda():
    """Fix Lambda function creation"""
    
    lambda_client = boto3.client("lambda", region_name="us-east-1")
    iam = boto3.client("iam", region_name="us-east-1")
    sts = boto3.client("sts")
    
    account_id = sts.get_caller_identity()["Account"]
    
    print("🔧 Fixing Lambda function...")
    
    # Wait for role to be ready
    print("⏳ Waiting for IAM role to be ready...")
    time.sleep(10)
    
    # Lambda code
    lambda_code = '''
import json

def lambda_handler(event, context):
    """bhagyesh's Personal Calendar Assistant"""
    
    print(f"bhagyesh's Calendar Assistant: {json.dumps(event)}")
    
    # Extract parameters
    parameters = event.get('parameters', [])
    params = {}
    for param in parameters:
        params[param['name']] = param['value']
    
    action = params.get('action', 'hello')
    
    # Personalized responses for bhagyesh
    if action == 'list':
        message = "bhagyesh's calendar today: Team standup at 9 AM, Client presentation at 2 PM, Gym session at 6 PM"
    elif action == 'add':
        summary = params.get('summary', 'New Event')
        start_time = params.get('startTime', 'TBD')
        message = f"Added to bhagyesh's calendar: {summary} at {start_time}"
    elif action == 'delete':
        message = "Event deleted from bhagyesh's calendar successfully"
    else:
        message = "Hello bhagyesh! I'm your personal calendar assistant. I can help you list, add, or delete calendar events."
    
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get('actionGroup', ''),
            "apiPath": event.get('apiPath', ''),
            "httpMethod": "POST",
            "httpStatusCode": 200,
            "responseBody": {
                "application/json": {
                    "body": json.dumps({
                        "message": message,
                        "user": "bhagyesh",
                        "status": "success"
                    })
                }
            }
        }
    }
'''
    
    # Create zip file
    with zipfile.ZipFile('/tmp/bhagyesh_lambda.zip', 'w') as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    # Deploy Lambda
    with open('/tmp/bhagyesh_lambda.zip', 'rb') as zip_file:
        try:
            lambda_client.create_function(
                FunctionName="bhagyesh-calendar-function",
                Runtime="python3.9",
                Role=f"arn:aws:iam::{account_id}:role/bhagyesh-lambda-role",
                Handler="lambda_function.lambda_handler",
                Code={'ZipFile': zip_file.read()},
                Description="bhagyesh's Personal Calendar Assistant",
                Tags={
                    "Owner": "bhagyesh",
                    "Purpose": "CalendarAssistant"
                }
            )
            print("✅ Created Lambda function for bhagyesh")
        except Exception as e:
            print(f"⚠️  Lambda creation error: {e}")
    
    # Add Lambda permission
    try:
        lambda_client.add_permission(
            FunctionName="bhagyesh-calendar-function",
            StatementId="bedrock-invoke-permission",
            Action="lambda:InvokeFunction",
            Principal="bedrock.amazonaws.com"
        )
        print("✅ Added Bedrock permission to Lambda")
    except Exception as e:
        print(f"⚠️  Permission error: {e}")

if __name__ == "__main__":
    fix_lambda()