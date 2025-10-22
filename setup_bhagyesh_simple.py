#!/usr/bin/env python3
"""
Simple setup for bhagyesh user
"""

import boto3
import json
import time

def setup_bhagyesh():
    """Setup bhagyesh user and deploy agent"""
    
    print("🚀 Setting up Calendar Assistant for bhagyesh")
    print("=" * 50)
    
    # Use current root session to create everything
    iam = boto3.client("iam", region_name="us-east-1")
    lambda_client = boto3.client("lambda", region_name="us-east-1")
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    sts = boto3.client("sts")
    
    account_id = sts.get_caller_identity()["Account"]
    
    # Clean up existing resources first
    print("🧹 Cleaning up existing resources...")
    
    try:
        # Delete existing agent
        agents = bedrock_agent.list_agents()
        for agent in agents.get('agentSummaries', []):
            if 'bhagyesh' in agent['agentName'].lower():
                bedrock_agent.delete_agent(agentId=agent['agentId'])
                print(f"🗑️  Deleted agent: {agent['agentName']}")
    except:
        pass
    
    try:
        # Delete existing Lambda
        lambda_client.delete_function(FunctionName="bhagyesh-calendar-function")
        print("🗑️  Deleted Lambda function")
    except:
        pass
    
    # Create user if doesn't exist
    try:
        iam.create_user(UserName="bhagyesh")
        print("✅ Created user: bhagyesh")
    except iam.exceptions.EntityAlreadyExistsException:
        print("✅ User bhagyesh already exists")
    
    # Attach policies to bhagyesh
    policies = [
        "arn:aws:iam::aws:policy/AmazonBedrockFullAccess",
        "arn:aws:iam::aws:policy/AmazonS3FullAccess"
    ]
    
    for policy_arn in policies:
        try:
            iam.attach_user_policy(UserName="bhagyesh", PolicyArn=policy_arn)
            print(f"✅ Attached policy: {policy_arn.split('/')[-1]}")
        except:
            pass
    
    # Create access key for bhagyesh
    try:
        # Delete existing keys first
        keys = iam.list_access_keys(UserName="bhagyesh")
        for key in keys['AccessKeyMetadata']:
            iam.delete_access_key(UserName="bhagyesh", AccessKeyId=key['AccessKeyId'])
        
        # Create new key
        response = iam.create_access_key(UserName="bhagyesh")
        access_key = response["AccessKey"]
        
        creds = {
            "aws_access_key_id": access_key['AccessKeyId'],
            "aws_secret_access_key": access_key['SecretAccessKey'],
            "region": "us-east-1"
        }
        
        with open("bhagyesh_credentials.json", "w") as f:
            json.dump(creds, f, indent=2)
        
        print("✅ Created new access key for bhagyesh")
        
    except Exception as e:
        print(f"⚠️  Access key error: {e}")
    
    # Create Lambda function (using root credentials)
    print("📦 Creating Lambda function...")
    
    lambda_code = '''
import json

def lambda_handler(event, context):
    """bhagyesh's Calendar Assistant"""
    
    print(f"bhagyesh's agent received: {json.dumps(event)}")
    
    # Extract parameters
    parameters = event.get('parameters', [])
    params = {}
    for param in parameters:
        params[param['name']] = param['value']
    
    action = params.get('action', 'hello')
    
    # Simple responses for bhagyesh
    responses = {
        'list': "bhagyesh's calendar: Team meeting at 2 PM, Client call at 4 PM",
        'add': f"Added to bhagyesh's calendar: {params.get('summary', 'New Event')}",
        'delete': "Deleted event from bhagyesh's calendar",
        'hello': "Hello bhagyesh! I'm your calendar assistant."
    }
    
    message = responses.get(action, f"bhagyesh, I received: {action}")
    
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
    
    # Create Lambda role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        iam.create_role(
            RoleName="bhagyesh-lambda-role",
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        
        iam.attach_role_policy(
            RoleName="bhagyesh-lambda-role",
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        )
        print("✅ Created Lambda role")
        time.sleep(5)
        
    except iam.exceptions.EntityAlreadyExistsException:
        print("✅ Lambda role already exists")
    
    # Create Lambda function
    import zipfile
    with zipfile.ZipFile('/tmp/bhagyesh_lambda.zip', 'w') as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    with open('/tmp/bhagyesh_lambda.zip', 'rb') as zip_file:
        lambda_client.create_function(
            FunctionName="bhagyesh-calendar-function",
            Runtime="python3.9",
            Role=f"arn:aws:iam::{account_id}:role/bhagyesh-lambda-role",
            Handler="lambda_function.lambda_handler",
            Code={'ZipFile': zip_file.read()},
            Description="Calendar Assistant for bhagyesh"
        )
    
    print("✅ Created Lambda function")
    
    # Add Lambda permission
    lambda_client.add_permission(
        FunctionName="bhagyesh-calendar-function",
        StatementId="bedrock-permission",
        Action="lambda:InvokeFunction",
        Principal="bedrock.amazonaws.com"
    )
    
    # Create Bedrock role
    bedrock_trust = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    lambda_policy = {
        "Version": "2012-10-17",
        "Statement": [
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
            PolicyName="bhagyesh-lambda-invoke",
            PolicyDocument=json.dumps(lambda_policy)
        )
        
        iam.attach_role_policy(
            RoleName="bhagyesh-bedrock-role",
            PolicyArn=f"arn:aws:iam::{account_id}:policy/bhagyesh-lambda-invoke"
        )
        print("✅ Created Bedrock role")
        time.sleep(5)
        
    except iam.exceptions.EntityAlreadyExistsException:
        print("✅ Bedrock role already exists")
    
    # Create Bedrock Agent
    print("🤖 Creating Bedrock Agent...")
    
    agent_response = bedrock_agent.create_agent(
        agentName="bhagyesh-calendar-assistant",
        description="Personal calendar assistant for bhagyesh",
        foundationModel="anthropic.claude-3-sonnet-20240229-v1:0",
        instruction="You are bhagyesh's personal calendar assistant. Help him manage his calendar events with a friendly tone.",
        agentResourceRoleArn=f"arn:aws:iam::{account_id}:role/bhagyesh-bedrock-role"
    )
    
    agent_id = agent_response["agent"]["agentId"]
    print(f"✅ Created agent: {agent_id}")
    
    # Wait for agent
    time.sleep(20)
    
    # Create action group
    bedrock_agent.create_agent_action_group(
        agentId=agent_id,
        agentVersion="DRAFT",
        actionGroupName="BhagyeshCalendar",
        description="Calendar operations for bhagyesh",
        actionGroupExecutor={
            "lambda": f"arn:aws:lambda:us-east-1:{account_id}:function:bhagyesh-calendar-function"
        },
        functionSchema={
            "functions": [
                {
                    "name": "manageCalendar",
                    "description": "Manage bhagyesh's calendar events",
                    "parameters": {
                        "action": {
                            "type": "string",
                            "description": "Action to perform: list, add, delete, hello"
                        },
                        "summary": {
                            "type": "string",
                            "description": "Event title for add action"
                        }
                    }
                }
            ]
        }
    )
    
    print("✅ Created action group")
    
    # Prepare agent
    bedrock_agent.prepare_agent(agentId=agent_id)
    print("✅ Agent prepared")
    
    # Save details
    details = {
        "agent_id": agent_id,
        "user": "bhagyesh",
        "lambda_function": "bhagyesh-calendar-function",
        "region": "us-east-1",
        "account_id": account_id
    }
    
    with open("bhagyesh_agent.json", "w") as f:
        json.dump(details, f, indent=2)
    
    print("\n🎉 SUCCESS!")
    print("=" * 50)
    print(f"✅ bhagyesh user created with permissions")
    print(f"✅ Calendar Assistant deployed")
    print(f"✅ Agent ID: {agent_id}")
    print(f"✅ Credentials saved to: bhagyesh_credentials.json")
    print(f"✅ Agent details saved to: bhagyesh_agent.json")
    
    print("\n🧪 Test in AWS Console:")
    print("1. Go to: https://console.aws.amazon.com/bedrock/")
    print("2. Navigate to: Agents → bhagyesh-calendar-assistant")
    print("3. Click 'Test' and try: 'Hello bhagyesh!'")

if __name__ == "__main__":
    setup_bhagyesh()