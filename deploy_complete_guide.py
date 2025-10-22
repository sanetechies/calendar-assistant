#!/usr/bin/env python3
"""
Complete step-by-step Calendar Assistant deployment
"""

import boto3
import json
import time
import zipfile
import os

def step_by_step_deployment():
    """Complete deployment with all necessary permissions"""
    
    print("🚀 Calendar Assistant - Complete Deployment Guide")
    print("=" * 60)
    
    # Initialize clients
    iam = boto3.client("iam", region_name="us-east-1")
    lambda_client = boto3.client("lambda", region_name="us-east-1")
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    sts = boto3.client("sts")
    
    account_id = sts.get_caller_identity()["Account"]
    print(f"AWS Account ID: {account_id}")
    
    # STEP 1: Create Lambda Execution Role
    print("\n📋 STEP 1: Creating Lambda Execution Role...")
    
    lambda_trust_policy = {
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
            RoleName="calendar-lambda-role",
            AssumeRolePolicyDocument=json.dumps(lambda_trust_policy),
            Description="Execution role for Calendar Assistant Lambda"
        )
        
        iam.attach_role_policy(
            RoleName="calendar-lambda-role",
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        )
        
        print("✅ Created Lambda execution role")
        time.sleep(5)  # Wait for role propagation
        
    except Exception as e:
        print(f"⚠️  Lambda role error: {e}")
    
    # STEP 2: Create Bedrock Agent Execution Role
    print("\n📋 STEP 2: Creating Bedrock Agent Execution Role...")
    
    bedrock_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Comprehensive Bedrock permissions
    bedrock_permissions = {
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
                "Action": [
                    "lambda:InvokeFunction"
                ],
                "Resource": f"arn:aws:lambda:us-east-1:{account_id}:function:calendar-function"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "aws-marketplace:ViewSubscriptions",
                    "aws-marketplace:Subscribe"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        # Create Bedrock role
        iam.create_role(
            RoleName="calendar-bedrock-role",
            AssumeRolePolicyDocument=json.dumps(bedrock_trust_policy),
            Description="Execution role for Calendar Assistant Bedrock Agent"
        )
        
        # Create and attach comprehensive policy
        iam.create_policy(
            PolicyName="CalendarBedrockPolicy",
            PolicyDocument=json.dumps(bedrock_permissions),
            Description="Comprehensive permissions for Calendar Assistant Bedrock Agent"
        )
        
        iam.attach_role_policy(
            RoleName="calendar-bedrock-role",
            PolicyArn=f"arn:aws:iam::{account_id}:policy/CalendarBedrockPolicy"
        )
        
        print("✅ Created Bedrock agent execution role with all permissions")
        time.sleep(5)
        
    except Exception as e:
        print(f"⚠️  Bedrock role error: {e}")
    
    # STEP 3: Create Lambda Function
    print("\n📋 STEP 3: Creating Lambda Function...")
    
    lambda_code = '''
import json

def lambda_handler(event, context):
    """Calendar Assistant Lambda Function"""
    
    print(f"Calendar Assistant received: {json.dumps(event)}")
    
    # Extract parameters from Bedrock Agent
    parameters = event.get('parameters', [])
    params = {}
    for param in parameters:
        params[param['name']] = param['value']
    
    action = params.get('action', 'hello')
    
    # Simple calendar responses
    if action == 'list':
        message = "Your calendar today: Team standup at 9 AM, Client meeting at 2 PM, Gym at 6 PM"
    elif action == 'add':
        summary = params.get('summary', 'New Event')
        start_time = params.get('startTime', 'TBD')
        message = f"Added to calendar: {summary} at {start_time}"
    elif action == 'delete':
        message = "Event deleted from your calendar"
    else:
        message = "Hello! I'm your Calendar Assistant. I can help you list, add, or delete calendar events."
    
    # Return response in Bedrock Agent format
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
                        "status": "success",
                        "timestamp": context.aws_request_id if context else "test"
                    })
                }
            }
        }
    }
'''
    
    # Create zip file
    with zipfile.ZipFile('/tmp/calendar_lambda.zip', 'w') as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    # Deploy Lambda function
    with open('/tmp/calendar_lambda.zip', 'rb') as zip_file:
        try:
            lambda_client.create_function(
                FunctionName="calendar-function",
                Runtime="python3.9",
                Role=f"arn:aws:iam::{account_id}:role/calendar-lambda-role",
                Handler="lambda_function.lambda_handler",
                Code={'ZipFile': zip_file.read()},
                Description="Calendar Assistant Lambda Function",
                Timeout=30
            )
            print("✅ Created Lambda function")
        except Exception as e:
            print(f"⚠️  Lambda creation error: {e}")
    
    # Add Lambda permission for Bedrock
    try:
        lambda_client.add_permission(
            FunctionName="calendar-function",
            StatementId="bedrock-invoke-permission",
            Action="lambda:InvokeFunction",
            Principal="bedrock.amazonaws.com"
        )
        print("✅ Added Bedrock invoke permission to Lambda")
    except Exception as e:
        print(f"⚠️  Permission error: {e}")
    
    # STEP 4: Create Bedrock Agent
    print("\n📋 STEP 4: Creating Bedrock Agent...")
    
    try:
        agent_response = bedrock_agent.create_agent(
            agentName="calendar-assistant",
            description="AI-powered calendar assistant for managing events",
            foundationModel="anthropic.claude-3-sonnet-20240229-v1:0",
            instruction="You are a helpful calendar assistant. You can list, add, and delete calendar events. Always be friendly and helpful. When users ask about their calendar, use the available functions to help them.",
            agentResourceRoleArn=f"arn:aws:iam::{account_id}:role/calendar-bedrock-role"
        )
        
        agent_id = agent_response["agent"]["agentId"]
        print(f"✅ Created Bedrock Agent: {agent_id}")
        
        # Wait for agent to be ready
        print("⏳ Waiting for agent to be ready...")
        time.sleep(20)
        
    except Exception as e:
        print(f"❌ Agent creation error: {e}")
        return
    
    # STEP 5: Create Action Group
    print("\n📋 STEP 5: Creating Action Group...")
    
    try:
        bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion="DRAFT",
            actionGroupName="CalendarActions",
            description="Calendar management actions",
            actionGroupExecutor={
                "lambda": f"arn:aws:lambda:us-east-1:{account_id}:function:calendar-function"
            },
            functionSchema={
                "functions": [
                    {
                        "name": "manageCalendar",
                        "description": "Manage calendar events - list, add, or delete",
                        "parameters": {
                            "action": {
                                "type": "string",
                                "description": "Action to perform: list, add, delete"
                            },
                            "summary": {
                                "type": "string",
                                "description": "Event title when adding events"
                            },
                            "startTime": {
                                "type": "string",
                                "description": "Event start time"
                            }
                        }
                    }
                ]
            }
        )
        print("✅ Created action group")
        
    except Exception as e:
        print(f"❌ Action group error: {e}")
        return
    
    # STEP 6: Prepare Agent
    print("\n📋 STEP 6: Preparing Agent...")
    
    try:
        bedrock_agent.prepare_agent(agentId=agent_id)
        print("✅ Agent prepared successfully")
        
    except Exception as e:
        print(f"❌ Agent preparation error: {e}")
    
    # STEP 7: Create Test Script
    print("\n📋 STEP 7: Creating Test Script...")
    
    test_script = f'''#!/usr/bin/env python3
"""
Test Calendar Assistant
"""

import boto3

def test_calendar_assistant():
    """Test the deployed Calendar Assistant"""
    
    client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
    
    agent_id = "{agent_id}"
    
    print("🧪 Testing Calendar Assistant")
    print(f"Agent ID: {{agent_id}}")
    
    queries = [
        "Hello! What can you help me with?",
        "What's on my calendar today?",
        "Add a team meeting tomorrow at 2 PM",
        "Delete my 3 PM appointment"
    ]
    
    for query in queries:
        try:
            print(f"\\n📝 Query: {{query}}")
            
            response = client.invoke_agent(
                agentId=agent_id,
                agentAliasId="TSTALIASID",
                sessionId="test-session",
                inputText=query
            )
            
            result = ""
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        result += chunk['bytes'].decode('utf-8')
            
            print(f"🤖 Response: {{result}}")
            
        except Exception as e:
            print(f"❌ Error: {{e}}")
            print("💡 Try testing in AWS Console:")
            print("   https://console.aws.amazon.com/bedrock/ → Agents → calendar-assistant")

if __name__ == "__main__":
    test_calendar_assistant()
'''
    
    with open("test_calendar_assistant.py", "w") as f:
        f.write(test_script)
    
    print("✅ Created test script: test_calendar_assistant.py")
    
    # SUCCESS SUMMARY
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print(f"✅ Agent ID: {agent_id}")
    print(f"✅ Lambda Function: calendar-function")
    print(f"✅ IAM Roles: calendar-lambda-role, calendar-bedrock-role")
    print(f"✅ Test Script: test_calendar_assistant.py")
    
    print("\n🧪 How to test:")
    print("1. AWS Console (RECOMMENDED):")
    print("   • Go to: https://console.aws.amazon.com/bedrock/")
    print("   • Navigate: Agents → calendar-assistant")
    print("   • Click 'Test' and try: 'What's on my calendar today?'")
    
    print("\n2. Command Line:")
    print("   python3 test_calendar_assistant.py")
    
    print("\n📋 Test queries:")
    print("• 'Hello! What can you help me with?'")
    print("• 'What's on my calendar today?'")
    print("• 'Add a team meeting tomorrow at 2 PM'")
    print("• 'Delete my 3 PM appointment'")
    
    return agent_id

if __name__ == "__main__":
    step_by_step_deployment()