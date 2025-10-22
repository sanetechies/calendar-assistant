#!/usr/bin/env python3
"""
Deploy Calendar Assistant without model access check
"""

import boto3
import json
import time
import zipfile

def deploy_without_model_check():
    """Deploy agent first, enable model access later"""
    
    print("🚀 Calendar Assistant - Deploy First, Enable Models Later")
    print("=" * 60)
    
    iam = boto3.client("iam", region_name="us-east-1")
    lambda_client = boto3.client("lambda", region_name="us-east-1")
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    sts = boto3.client("sts")
    
    account_id = sts.get_caller_identity()["Account"]
    
    # STEP 1: Create bhagyesh user
    print("\n👤 STEP 1: Creating bhagyesh user...")
    
    try:
        iam.create_user(UserName="bhagyesh")
        print("✅ Created user: bhagyesh")
    except iam.exceptions.EntityAlreadyExistsException:
        print("✅ User bhagyesh already exists")
    
    iam.attach_user_policy(
        UserName="bhagyesh",
        PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
    )
    
    # Create access key
    try:
        keys = iam.list_access_keys(UserName="bhagyesh")
        for key in keys['AccessKeyMetadata']:
            iam.delete_access_key(UserName="bhagyesh", AccessKeyId=key['AccessKeyId'])
        
        response = iam.create_access_key(UserName="bhagyesh")
        access_key = response["AccessKey"]
        
        creds = {
            "aws_access_key_id": access_key['AccessKeyId'],
            "aws_secret_access_key": access_key['SecretAccessKey'],
            "region": "us-east-1"
        }
        
        with open("bhagyesh_credentials.json", "w") as f:
            json.dump(creds, f, indent=2)
        
        print(f"✅ Created access key: {access_key['AccessKeyId']}")
        
    except Exception as e:
        print(f"⚠️  Access key error: {e}")
    
    # STEP 2: Create Lambda role
    print("\n📦 STEP 2: Creating Lambda role...")
    
    lambda_trust = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    try:
        iam.create_role(
            RoleName="bhagyesh-lambda-role",
            AssumeRolePolicyDocument=json.dumps(lambda_trust)
        )
        
        iam.attach_role_policy(
            RoleName="bhagyesh-lambda-role",
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        )
        
        print("✅ Created Lambda role")
        time.sleep(5)
        
    except Exception as e:
        print(f"⚠️  Lambda role error: {e}")
    
    # STEP 3: Create Bedrock role
    print("\n🤖 STEP 3: Creating Bedrock role...")
    
    bedrock_trust = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    bedrock_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": f"arn:aws:lambda:us-east-1:{account_id}:function:bhagyesh-calendar-function"
            }
        ]
    }
    
    try:
        iam.create_role(
            RoleName="bhagyesh-bedrock-role",
            AssumeRolePolicyDocument=json.dumps(bedrock_trust)
        )
        
        iam.create_policy(
            PolicyName="bhagyesh-bedrock-policy",
            PolicyDocument=json.dumps(bedrock_policy)
        )
        
        iam.attach_role_policy(
            RoleName="bhagyesh-bedrock-role",
            PolicyArn=f"arn:aws:iam::{account_id}:policy/bhagyesh-bedrock-policy"
        )
        
        print("✅ Created Bedrock role")
        time.sleep(5)
        
    except Exception as e:
        print(f"⚠️  Bedrock role error: {e}")
    
    # STEP 4: Create Lambda function
    print("\n⚡ STEP 4: Creating Lambda function...")
    
    lambda_code = '''
import json

def lambda_handler(event, context):
    """bhagyesh's Calendar Assistant"""
    
    print(f"bhagyesh's assistant: {json.dumps(event)}")
    
    parameters = event.get('parameters', [])
    params = {}
    for param in parameters:
        params[param['name']] = param['value']
    
    action = params.get('action', 'hello')
    
    if action == 'list':
        message = "bhagyesh's calendar: Team standup at 9 AM, Client meeting at 2 PM, Gym at 6 PM"
    elif action == 'add':
        summary = params.get('summary', 'New Event')
        message = f"Added to bhagyesh's calendar: {summary}"
    elif action == 'delete':
        message = "Event deleted from bhagyesh's calendar"
    else:
        message = "Hello bhagyesh! I'm your personal calendar assistant."
    
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
                        "user": "bhagyesh"
                    })
                }
            }
        }
    }
'''
    
    with zipfile.ZipFile('/tmp/lambda.zip', 'w') as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    with open('/tmp/lambda.zip', 'rb') as zip_file:
        try:
            lambda_client.create_function(
                FunctionName="bhagyesh-calendar-function",
                Runtime="python3.9",
                Role=f"arn:aws:iam::{account_id}:role/bhagyesh-lambda-role",
                Handler="lambda_function.lambda_handler",
                Code={'ZipFile': zip_file.read()}
            )
            print("✅ Created Lambda function")
        except Exception as e:
            print(f"⚠️  Lambda error: {e}")
    
    try:
        lambda_client.add_permission(
            FunctionName="bhagyesh-calendar-function",
            StatementId="bedrock-permission",
            Action="lambda:InvokeFunction",
            Principal="bedrock.amazonaws.com"
        )
        print("✅ Added Lambda permission")
    except Exception as e:
        print(f"⚠️  Permission error: {e}")
    
    # STEP 5: Create Bedrock Agent
    print("\n🧠 STEP 5: Creating Bedrock Agent...")
    
    try:
        agent_response = bedrock_agent.create_agent(
            agentName="bhagyesh-calendar-assistant",
            description="Personal calendar assistant for bhagyesh",
            foundationModel="anthropic.claude-3-sonnet-20240229-v1:0",
            instruction="You are bhagyesh's personal calendar assistant. Help him manage calendar events.",
            agentResourceRoleArn=f"arn:aws:iam::{account_id}:role/bhagyesh-bedrock-role"
        )
        
        agent_id = agent_response["agent"]["agentId"]
        print(f"✅ Created agent: {agent_id}")
        
        time.sleep(20)
        
    except Exception as e:
        print(f"❌ Agent error: {e}")
        return
    
    # STEP 6: Create Action Group
    print("\n⚙️ STEP 6: Creating Action Group...")
    
    try:
        bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion="DRAFT",
            actionGroupName="CalendarActions",
            actionGroupExecutor={
                "lambda": f"arn:aws:lambda:us-east-1:{account_id}:function:bhagyesh-calendar-function"
            },
            functionSchema={
                "functions": [{
                    "name": "manageCalendar",
                    "description": "Manage bhagyesh's calendar",
                    "parameters": {
                        "action": {
                            "type": "string",
                            "description": "Action: list, add, delete"
                        },
                        "summary": {
                            "type": "string",
                            "description": "Event title"
                        }
                    }
                }]
            }
        )
        print("✅ Created action group")
        
    except Exception as e:
        print(f"❌ Action group error: {e}")
        return
    
    # STEP 7: Prepare Agent
    print("\n🔄 STEP 7: Preparing Agent...")
    
    try:
        bedrock_agent.prepare_agent(agentId=agent_id)
        print("✅ Agent prepared")
        
    except Exception as e:
        print(f"❌ Preparation error: {e}")
    
    # Save info
    setup_info = {
        "agent_id": agent_id,
        "user": "bhagyesh",
        "lambda_function": "bhagyesh-calendar-function"
    }
    
    with open("bhagyesh_final_setup.json", "w") as f:
        json.dump(setup_info, f, indent=2)
    
    # SUCCESS
    print("\n" + "=" * 60)
    print("🎉 AGENT DEPLOYED!")
    print("=" * 60)
    print(f"✅ Agent ID: {agent_id}")
    print(f"✅ User: bhagyesh")
    print(f"✅ Lambda: bhagyesh-calendar-function")
    
    print("\n🔧 NEXT STEP: Enable Model Access")
    print("1. Go to: https://console.aws.amazon.com/bedrock/")
    print("2. Click 'Model access' → 'Request model access'")
    print("3. Enable 'Claude 3 Sonnet'")
    print("4. Add valid payment method if required")
    
    print("\n🧪 Then test:")
    print("AWS Console: Agents → bhagyesh-calendar-assistant → Test")
    
    return agent_id

if __name__ == "__main__":
    deploy_without_model_check()