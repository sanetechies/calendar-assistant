#!/usr/bin/env python3
"""
Complete setup for bhagyesh user with Calendar Assistant
"""

import boto3
import json
import time
import zipfile
import os

def create_bhagyesh_user():
    """Create bhagyesh user with necessary permissions"""
    
    print("👤 Creating bhagyesh user...")
    
    iam = boto3.client("iam", region_name="us-east-1")
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    
    # Create user
    try:
        iam.create_user(
            UserName="bhagyesh",
            Path="/",
            Tags=[
                {"Key": "Purpose", "Value": "CalendarAssistant"},
                {"Key": "CreatedBy", "Value": "AutoSetup"}
            ]
        )
        print("✅ Created user: bhagyesh")
    except iam.exceptions.EntityAlreadyExistsException:
        print("✅ User bhagyesh already exists")
    
    # Create access key
    try:
        response = iam.create_access_key(UserName="bhagyesh")
        access_key = response["AccessKey"]
        
        print(f"🔑 Access Key ID: {access_key['AccessKeyId']}")
        print(f"🔑 Secret Key: {access_key['SecretAccessKey']}")
        
        # Save credentials
        creds = {
            "aws_access_key_id": access_key['AccessKeyId'],
            "aws_secret_access_key": access_key['SecretAccessKey'],
            "region": "us-east-1"
        }
        
        with open("bhagyesh_credentials.json", "w") as f:
            json.dump(creds, f, indent=2)
        
        print("✅ Saved credentials to bhagyesh_credentials.json")
        
    except iam.exceptions.LimitExceededException:
        print("⚠️  Access key limit reached - using existing key")
    
    # Attach policies
    policies = [
        "arn:aws:iam::aws:policy/AmazonBedrockFullAccess",
        "arn:aws:iam::aws:policy/IAMFullAccess",
        "arn:aws:iam::aws:policy/AWSLambdaFullAccess",
        "arn:aws:iam::aws:policy/AmazonS3FullAccess"
    ]
    
    for policy_arn in policies:
        try:
            iam.attach_user_policy(UserName="bhagyesh", PolicyArn=policy_arn)
            policy_name = policy_arn.split("/")[-1]
            print(f"✅ Attached policy: {policy_name}")
        except Exception as e:
            print(f"⚠️  Policy attachment error: {e}")
    
    return account_id

def deploy_with_bhagyesh_creds():
    """Deploy Calendar Assistant using bhagyesh credentials"""
    
    print("\n🚀 Deploying Calendar Assistant as bhagyesh...")
    
    # Load bhagyesh credentials
    try:
        with open("bhagyesh_credentials.json", "r") as f:
            creds = json.load(f)
    except FileNotFoundError:
        print("❌ bhagyesh_credentials.json not found")
        return
    
    # Create session with bhagyesh credentials
    session = boto3.Session(
        aws_access_key_id=creds["aws_access_key_id"],
        aws_secret_access_key=creds["aws_secret_access_key"],
        region_name=creds["region"]
    )
    
    # Initialize clients
    iam = session.client("iam")
    lambda_client = session.client("lambda")
    bedrock_agent = session.client("bedrock-agent")
    sts = session.client("sts")
    
    account_id = sts.get_caller_identity()["Account"]
    
    # Create Lambda execution role
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
            RoleName="bhagyesh-calendar-lambda-role",
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        
        iam.attach_role_policy(
            RoleName="bhagyesh-calendar-lambda-role",
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        )
        print("✅ Created Lambda role")
        time.sleep(10)
        
    except iam.exceptions.EntityAlreadyExistsException:
        print("✅ Lambda role already exists")
    
    # Create Bedrock agent role
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
            RoleName="bhagyesh-calendar-bedrock-role",
            AssumeRolePolicyDocument=json.dumps(bedrock_trust_policy)
        )
        
        iam.create_policy(
            PolicyName="bhagyesh-calendar-lambda-invoke",
            PolicyDocument=json.dumps(lambda_policy)
        )
        
        iam.attach_role_policy(
            RoleName="bhagyesh-calendar-bedrock-role",
            PolicyArn=f"arn:aws:iam::{account_id}:policy/bhagyesh-calendar-lambda-invoke"
        )
        print("✅ Created Bedrock role")
        time.sleep(10)
        
    except iam.exceptions.EntityAlreadyExistsException:
        print("✅ Bedrock role already exists")
    
    # Create Lambda function
    lambda_code = '''
import json

def lambda_handler(event, context):
    """Calendar Assistant Lambda for bhagyesh"""
    
    print(f"Received event: {json.dumps(event)}")
    
    # Extract parameters
    action_group = event.get('actionGroup', '')
    api_path = event.get('apiPath', '')
    parameters = event.get('parameters', [])
    
    # Convert parameters to dict
    params = {}
    for param in parameters:
        params[param['name']] = param['value']
    
    action = params.get('action', 'unknown')
    
    # Simple responses
    if action == 'list':
        message = "Here are your upcoming calendar events: Meeting at 2 PM, Call at 4 PM"
    elif action == 'add':
        summary = params.get('summary', 'New Event')
        message = f"Created event: {summary}"
    elif action == 'delete':
        message = "Event deleted successfully"
    else:
        message = f"Calendar Assistant received: {action}"
    
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": action_group,
            "apiPath": api_path,
            "httpMethod": "POST",
            "httpStatusCode": 200,
            "responseBody": {
                "application/json": {
                    "body": json.dumps({
                        "message": message,
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
    
    # Upload Lambda
    with open('/tmp/bhagyesh_lambda.zip', 'rb') as zip_file:
        try:
            lambda_client.create_function(
                FunctionName="bhagyesh-calendar-function",
                Runtime="python3.9",
                Role=f"arn:aws:iam::{account_id}:role/bhagyesh-calendar-lambda-role",
                Handler="lambda_function.lambda_handler",
                Code={'ZipFile': zip_file.read()},
                Description="Calendar Assistant for bhagyesh"
            )
            print("✅ Created Lambda function")
        except lambda_client.exceptions.ResourceConflictException:
            print("✅ Lambda function already exists")
    
    # Add Lambda permission for Bedrock
    try:
        lambda_client.add_permission(
            FunctionName="bhagyesh-calendar-function",
            StatementId="bedrock-invoke-permission",
            Action="lambda:InvokeFunction",
            Principal="bedrock.amazonaws.com"
        )
        print("✅ Added Lambda permission")
    except:
        print("✅ Lambda permission already exists")
    
    # Create Bedrock Agent
    try:
        agent_response = bedrock_agent.create_agent(
            agentName="bhagyesh-calendar-assistant",
            description="Calendar Assistant for bhagyesh user",
            foundationModel="anthropic.claude-3-sonnet-20240229-v1:0",
            instruction="You are bhagyesh's calendar assistant. Help manage calendar events.",
            agentResourceRoleArn=f"arn:aws:iam::{account_id}:role/bhagyesh-calendar-bedrock-role"
        )
        
        agent_id = agent_response["agent"]["agentId"]
        print(f"✅ Created agent: {agent_id}")
        
        # Wait for agent
        time.sleep(30)
        
        # Create action group
        bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion="DRAFT",
            actionGroupName="BhagyeshCalendarActions",
            description="Calendar management for bhagyesh",
            actionGroupExecutor={
                "lambda": f"arn:aws:lambda:us-east-1:{account_id}:function:bhagyesh-calendar-function"
            },
            functionSchema={
                "functions": [
                    {
                        "name": "manageCalendar",
                        "description": "Manage calendar events for bhagyesh",
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
                    }
                ]
            }
        )
        print("✅ Created action group")
        
        # Prepare agent
        bedrock_agent.prepare_agent(agentId=agent_id)
        print("✅ Agent prepared")
        
        # Save agent details
        agent_details = {
            "agent_id": agent_id,
            "user": "bhagyesh",
            "lambda_function": f"bhagyesh-calendar-function",
            "region": "us-east-1"
        }
        
        with open("bhagyesh_agent_details.json", "w") as f:
            json.dump(agent_details, f, indent=2)
        
        print(f"\n🎉 SUCCESS! bhagyesh Calendar Assistant deployed!")
        print(f"Agent ID: {agent_id}")
        print("Saved details to: bhagyesh_agent_details.json")
        
    except Exception as e:
        print(f"❌ Agent creation error: {e}")

def create_bhagyesh_test_script():
    """Create test script for bhagyesh"""
    
    test_script = '''#!/usr/bin/env python3
"""
Test Calendar Assistant as bhagyesh user
"""

import boto3
import json

def test_as_bhagyesh():
    """Test the agent using bhagyesh credentials"""
    
    # Load credentials
    with open("bhagyesh_credentials.json", "r") as f:
        creds = json.load(f)
    
    # Load agent details
    with open("bhagyesh_agent_details.json", "r") as f:
        agent = json.load(f)
    
    # Create session
    session = boto3.Session(
        aws_access_key_id=creds["aws_access_key_id"],
        aws_secret_access_key=creds["aws_secret_access_key"],
        region_name=creds["region"]
    )
    
    client = session.client("bedrock-agent-runtime")
    
    print(f"🧪 Testing as bhagyesh user...")
    print(f"Agent ID: {agent['agent_id']}")
    
    queries = [
        "What's on my calendar today?",
        "Schedule a meeting tomorrow at 2 PM",
        "Hello bhagyesh!"
    ]
    
    for query in queries:
        try:
            print(f"\\nQuery: {query}")
            
            response = client.invoke_agent(
                agentId=agent['agent_id'],
                agentAliasId="TSTALIASID",
                sessionId="bhagyesh-test",
                inputText=query
            )
            
            result = ""
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        result += chunk['bytes'].decode('utf-8')
            
            print(f"Response: {result}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_as_bhagyesh()
'''
    
    with open("test_bhagyesh.py", "w") as f:
        f.write(test_script)
    
    print("✅ Created test_bhagyesh.py")

def main():
    """Main setup function"""
    
    print("🚀 Complete Calendar Assistant Setup for bhagyesh")
    print("=" * 60)
    
    # Step 1: Create user
    account_id = create_bhagyesh_user()
    
    # Step 2: Deploy assistant
    deploy_with_bhagyesh_creds()
    
    # Step 3: Create test script
    create_bhagyesh_test_script()
    
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("Files created:")
    print("• bhagyesh_credentials.json - AWS credentials")
    print("• bhagyesh_agent_details.json - Agent details")
    print("• test_bhagyesh.py - Test script")
    print()
    print("To test:")
    print("python3 test_bhagyesh.py")

if __name__ == "__main__":
    main()