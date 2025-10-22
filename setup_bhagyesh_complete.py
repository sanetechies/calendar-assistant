#!/usr/bin/env python3
"""
Complete Calendar Assistant setup for bhagyesh user only
"""

import boto3
import json
import time
import zipfile

def setup_bhagyesh_complete():
    """Complete setup for bhagyesh user with all permissions"""
    
    print("🚀 Complete Calendar Assistant Setup for bhagyesh")
    print("=" * 60)
    
    # Use root credentials to create everything
    iam = boto3.client("iam", region_name="us-east-1")
    lambda_client = boto3.client("lambda", region_name="us-east-1")
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    sts = boto3.client("sts")
    
    account_id = sts.get_caller_identity()["Account"]
    
    # STEP 1: Create bhagyesh user with all permissions
    print("\n👤 STEP 1: Creating bhagyesh user...")
    
    try:
        iam.create_user(
            UserName="bhagyesh",
            Tags=[
                {"Key": "Purpose", "Value": "CalendarAssistant"},
                {"Key": "Owner", "Value": "bhagyesh"}
            ]
        )
        print("✅ Created user: bhagyesh")
    except iam.exceptions.EntityAlreadyExistsException:
        print("✅ User bhagyesh already exists")
    
    # Attach comprehensive policies to bhagyesh
    policies_for_bhagyesh = [
        "arn:aws:iam::aws:policy/AmazonBedrockFullAccess",
        "arn:aws:iam::aws:policy/IAMFullAccess",
        "arn:aws:iam::aws:policy/AWSLambdaFullAccess",
        "arn:aws:iam::aws:policy/AmazonS3FullAccess",
        "arn:aws:iam::aws:policy/AWSMarketplaceFullAccess"
    ]
    
    for policy_arn in policies_for_bhagyesh:
        try:
            iam.attach_user_policy(UserName="bhagyesh", PolicyArn=policy_arn)
            policy_name = policy_arn.split("/")[-1]
            print(f"✅ Attached {policy_name} to bhagyesh")
        except Exception as e:
            print(f"⚠️  Policy error: {e}")
    
    # Create access key for bhagyesh
    try:
        # Delete existing keys first
        keys = iam.list_access_keys(UserName="bhagyesh")
        for key in keys['AccessKeyMetadata']:
            iam.delete_access_key(UserName="bhagyesh", AccessKeyId=key['AccessKeyId'])
        
        # Create new key
        response = iam.create_access_key(UserName="bhagyesh")
        access_key = response["AccessKey"]
        
        bhagyesh_creds = {
            "aws_access_key_id": access_key['AccessKeyId'],
            "aws_secret_access_key": access_key['SecretAccessKey'],
            "region": "us-east-1"
        }
        
        with open("bhagyesh_aws_credentials.json", "w") as f:
            json.dump(bhagyesh_creds, f, indent=2)
        
        print("✅ Created access key for bhagyesh")
        print(f"   Access Key: {access_key['AccessKeyId']}")
        
    except Exception as e:
        print(f"⚠️  Access key error: {e}")
    
    # STEP 2: Create Lambda role (owned by bhagyesh)
    print("\n📦 STEP 2: Creating Lambda resources...")
    
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
            RoleName="bhagyesh-lambda-role",
            AssumeRolePolicyDocument=json.dumps(lambda_trust_policy),
            Description="Lambda execution role for bhagyesh's Calendar Assistant",
            Tags=[
                {"Key": "Owner", "Value": "bhagyesh"},
                {"Key": "Purpose", "Value": "CalendarAssistant"}
            ]
        )
        
        iam.attach_role_policy(
            RoleName="bhagyesh-lambda-role",
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        )
        
        print("✅ Created Lambda role for bhagyesh")
        time.sleep(5)
        
    except Exception as e:
        print(f"⚠️  Lambda role error: {e}")
    
    # STEP 3: Create Bedrock role (owned by bhagyesh)
    print("\n🤖 STEP 3: Creating Bedrock resources...")
    
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
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:GetPrompt",
                    "bedrock:ListPrompts",
                    "bedrock:GetAgent",
                    "bedrock:ListAgents",
                    "bedrock:GetAgentVersion",
                    "bedrock:ListAgentVersions",
                    "bedrock:GetAgentActionGroup",
                    "bedrock:ListAgentActionGroups",
                    "bedrock:GetKnowledgeBase",
                    "bedrock:ListKnowledgeBases",
                    "bedrock:Retrieve",
                    "bedrock:RetrieveAndGenerate"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": f"arn:aws:lambda:us-east-1:{account_id}:function:bhagyesh-calendar-function"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "aws-marketplace:ViewSubscriptions",
                    "aws-marketplace:Subscribe",
                    "aws-marketplace:Unsubscribe",
                    "aws-marketplace:ListSubscriptions",
                    "aws-marketplace:GetSubscription",
                    "aws-marketplace:DescribeEntity",
                    "aws-marketplace:ListEntities"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        # Create Bedrock role
        iam.create_role(
            RoleName="bhagyesh-bedrock-role",
            AssumeRolePolicyDocument=json.dumps(bedrock_trust_policy),
            Description="Bedrock execution role for bhagyesh's Calendar Assistant",
            Tags=[
                {"Key": "Owner", "Value": "bhagyesh"},
                {"Key": "Purpose", "Value": "CalendarAssistant"}
            ]
        )
        
        # Create and attach policy
        iam.create_policy(
            PolicyName="bhagyesh-bedrock-policy",
            PolicyDocument=json.dumps(bedrock_permissions),
            Description="Comprehensive Bedrock permissions for bhagyesh"
        )
        
        iam.attach_role_policy(
            RoleName="bhagyesh-bedrock-role",
            PolicyArn=f"arn:aws:iam::{account_id}:policy/bhagyesh-bedrock-policy"
        )
        
        print("✅ Created Bedrock role for bhagyesh")
        time.sleep(5)
        
    except Exception as e:
        print(f"⚠️  Bedrock role error: {e}")
    
    # STEP 4: Create Lambda function
    print("\n⚡ STEP 4: Creating Lambda function...")
    
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
    
    # STEP 5: Create Bedrock Agent
    print("\n🧠 STEP 5: Creating Bedrock Agent...")
    
    try:
        agent_response = bedrock_agent.create_agent(
            agentName="bhagyesh-calendar-assistant",
            description="Personal calendar assistant for bhagyesh - manages events with natural language",
            foundationModel="anthropic.claude-3-5-sonnet-20241022-v2:0",
            instruction="You are bhagyesh's personal calendar assistant. You help him manage his calendar events. Always address him by name and be friendly and helpful. You can list his events, add new events, and delete events.",
            agentResourceRoleArn=f"arn:aws:iam::{account_id}:role/bhagyesh-bedrock-role",
            tags={
                "Owner": "bhagyesh",
                "Purpose": "CalendarAssistant"
            }
        )
        
        agent_id = agent_response["agent"]["agentId"]
        print(f"✅ Created Bedrock Agent for bhagyesh: {agent_id}")
        
        # Wait for agent
        time.sleep(20)
        
    except Exception as e:
        print(f"❌ Agent creation error: {e}")
        return
    
    # STEP 6: Create Action Group
    print("\n⚙️ STEP 6: Creating Action Group...")
    
    try:
        bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion="DRAFT",
            actionGroupName="BhagyeshCalendarActions",
            description="Calendar management actions for bhagyesh",
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
        print("✅ Created action group for bhagyesh")
        
    except Exception as e:
        print(f"❌ Action group error: {e}")
        return
    
    # STEP 7: Prepare Agent
    print("\n🔄 STEP 7: Preparing Agent...")
    
    try:
        bedrock_agent.prepare_agent(agentId=agent_id)
        print("✅ Agent prepared successfully")
        
    except Exception as e:
        print(f"❌ Agent preparation error: {e}")
    
    # STEP 8: Create bhagyesh test script
    print("\n📝 STEP 8: Creating test script for bhagyesh...")
    
    test_script = f'''#!/usr/bin/env python3
"""
Test bhagyesh's Calendar Assistant
"""

import boto3
import json

def test_bhagyesh_calendar():
    """Test using bhagyesh's credentials"""
    
    # Load bhagyesh credentials
    with open("bhagyesh_aws_credentials.json", "r") as f:
        creds = json.load(f)
    
    # Create session with bhagyesh credentials
    session = boto3.Session(
        aws_access_key_id=creds["aws_access_key_id"],
        aws_secret_access_key=creds["aws_secret_access_key"],
        region_name=creds["region"]
    )
    
    client = session.client("bedrock-agent-runtime")
    
    agent_id = "{agent_id}"
    
    print("🧪 Testing bhagyesh's Calendar Assistant")
    print(f"Agent ID: {{agent_id}}")
    
    queries = [
        "Hello bhagyesh!",
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
                sessionId="bhagyesh-session",
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

if __name__ == "__main__":
    test_bhagyesh_calendar()
'''
    
    with open("test_bhagyesh_calendar.py", "w") as f:
        f.write(test_script)
    
    print("✅ Created test script: test_bhagyesh_calendar.py")
    
    # Save complete setup info
    setup_info = {
        "user": "bhagyesh",
        "agent_id": agent_id,
        "lambda_function": "bhagyesh-calendar-function",
        "lambda_role": "bhagyesh-lambda-role",
        "bedrock_role": "bhagyesh-bedrock-role",
        "region": "us-east-1",
        "account_id": account_id
    }
    
    with open("bhagyesh_setup_complete.json", "w") as f:
        json.dump(setup_info, f, indent=2)
    
    # SUCCESS SUMMARY
    print("\n" + "=" * 60)
    print("🎉 BHAGYESH CALENDAR ASSISTANT - COMPLETE!")
    print("=" * 60)
    print(f"✅ User: bhagyesh (with full permissions)")
    print(f"✅ Agent ID: {agent_id}")
    print(f"✅ Lambda: bhagyesh-calendar-function")
    print(f"✅ All resources tagged with Owner: bhagyesh")
    
    print("\n📁 Files created:")
    print("• bhagyesh_aws_credentials.json - AWS credentials")
    print("• test_bhagyesh_calendar.py - Test script")
    print("• bhagyesh_setup_complete.json - Complete setup info")
    
    print("\n🧪 How to test:")
    print("1. AWS Console (as root):")
    print("   https://console.aws.amazon.com/bedrock/ → Agents → bhagyesh-calendar-assistant")
    
    print("\n2. Command line (as bhagyesh):")
    print("   python3 test_bhagyesh_calendar.py")
    
    print("\n💡 Everything is owned by bhagyesh user!")
    print("All resources are tagged and configured for bhagyesh only.")
    
    return agent_id

if __name__ == "__main__":
    setup_bhagyesh_complete()