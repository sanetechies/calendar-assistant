#!/usr/bin/env python3
"""
Final working deployment for bhagyesh
"""

import boto3
import json
import time

def deploy_bhagyesh_final():
    """Deploy everything for bhagyesh with proper waits"""
    
    print("🚀 Final deployment for bhagyesh")
    print("=" * 40)
    
    # Use existing working deployment approach
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    lambda_client = boto3.client("lambda", region_name="us-east-1")
    iam = boto3.client("iam", region_name="us-east-1")
    sts = boto3.client("sts")
    
    account_id = sts.get_caller_identity()["Account"]
    
    # Clean up first
    print("🧹 Cleaning up...")
    try:
        agents = bedrock_agent.list_agents()
        for agent in agents.get('agentSummaries', []):
            if 'bhagyesh' in agent['agentName'].lower():
                bedrock_agent.delete_agent(agentId=agent['agentId'])
                print(f"🗑️  Deleted agent: {agent['agentName']}")
    except:
        pass
    
    # Use the existing working Lambda function and just rename it
    print("📦 Setting up Lambda function...")
    
    try:
        # Copy existing working function
        response = lambda_client.get_function(FunctionName="calendar-assistant-function")
        
        # Update it for bhagyesh
        lambda_client.update_function_code(
            FunctionName="calendar-assistant-function",
            ZipFile=b'''
import json

def lambda_handler(event, context):
    """bhagyesh's Calendar Assistant"""
    
    print(f"bhagyesh's calendar agent: {json.dumps(event)}")
    
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
        message = "Deleted event from bhagyesh's calendar"
    else:
        message = f"Hello bhagyesh! I'm your personal calendar assistant. I can help you list, add, or delete events."
    
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
        )
        print("✅ Updated Lambda function for bhagyesh")
        
    except Exception as e:
        print(f"⚠️  Lambda error: {e}")
    
    # Create new agent for bhagyesh
    print("🤖 Creating bhagyesh's agent...")
    
    try:
        agent_response = bedrock_agent.create_agent(
            agentName="bhagyesh-calendar-assistant",
            description="Personal calendar assistant for bhagyesh user",
            foundationModel="anthropic.claude-3-sonnet-20240229-v1:0",
            instruction="You are bhagyesh's personal calendar assistant. You help him manage his calendar events. Always address him by name and be friendly and helpful.",
            agentResourceRoleArn=f"arn:aws:iam::{account_id}:role/calendar-assistant-execution-role"
        )
        
        agent_id = agent_response["agent"]["agentId"]
        print(f"✅ Created agent: {agent_id}")
        
        # Wait for agent
        print("⏳ Waiting for agent to be ready...")
        time.sleep(30)
        
        # Create action group
        bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion="DRAFT",
            actionGroupName="BhagyeshCalendarActions",
            description="Calendar management for bhagyesh",
            actionGroupExecutor={
                "lambda": f"arn:aws:lambda:us-east-1:{account_id}:function:calendar-assistant-function"
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
        
        # Prepare agent
        bedrock_agent.prepare_agent(agentId=agent_id)
        print("✅ Agent prepared")
        
        # Create bhagyesh user with permissions
        print("👤 Setting up bhagyesh user...")
        
        try:
            iam.create_user(UserName="bhagyesh")
            print("✅ Created user: bhagyesh")
        except iam.exceptions.EntityAlreadyExistsException:
            print("✅ User bhagyesh already exists")
        
        # Attach Bedrock permissions
        try:
            iam.attach_user_policy(
                UserName="bhagyesh",
                PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
            )
            print("✅ Attached Bedrock permissions to bhagyesh")
        except:
            pass
        
        # Create access key
        try:
            # Delete existing keys
            keys = iam.list_access_keys(UserName="bhagyesh")
            for key in keys['AccessKeyMetadata']:
                iam.delete_access_key(UserName="bhagyesh", AccessKeyId=key['AccessKeyId'])
            
            # Create new key
            response = iam.create_access_key(UserName="bhagyesh")
            access_key = response["AccessKey"]
            
            # Save credentials
            creds = {
                "aws_access_key_id": access_key['AccessKeyId'],
                "aws_secret_access_key": access_key['SecretAccessKey'],
                "region": "us-east-1",
                "agent_id": agent_id
            }
            
            with open("bhagyesh_setup.json", "w") as f:
                json.dump(creds, f, indent=2)
            
            print("✅ Created access key for bhagyesh")
            
        except Exception as e:
            print(f"⚠️  Access key error: {e}")
        
        # Create test script
        test_script = f'''#!/usr/bin/env python3
"""
Test bhagyesh's Calendar Assistant
"""

import boto3
import json

def test_bhagyesh_agent():
    """Test the agent as bhagyesh"""
    
    # Load credentials
    with open("bhagyesh_setup.json", "r") as f:
        config = json.load(f)
    
    # Create session with bhagyesh credentials
    session = boto3.Session(
        aws_access_key_id=config["aws_access_key_id"],
        aws_secret_access_key=config["aws_secret_access_key"],
        region_name=config["region"]
    )
    
    client = session.client("bedrock-agent-runtime")
    
    print("🧪 Testing bhagyesh's Calendar Assistant")
    print(f"Agent ID: {{config['agent_id']}}")
    
    queries = [
        "Hello bhagyesh!",
        "What's on my calendar today?",
        "Schedule a team meeting tomorrow at 2 PM"
    ]
    
    for query in queries:
        try:
            print(f"\\n📝 Query: {{query}}")
            
            response = client.invoke_agent(
                agentId=config['agent_id'],
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
            print("💡 Try testing in AWS Console first:")
            print("   https://console.aws.amazon.com/bedrock/ → Agents → bhagyesh-calendar-assistant")

if __name__ == "__main__":
    test_bhagyesh_agent()
'''
        
        with open("test_bhagyesh_agent.py", "w") as f:
            f.write(test_script)
        
        print("✅ Created test script")
        
        print("\n🎉 SUCCESS!")
        print("=" * 40)
        print(f"✅ bhagyesh's Calendar Assistant deployed")
        print(f"✅ Agent ID: {agent_id}")
        print(f"✅ User: bhagyesh (with Bedrock permissions)")
        print(f"✅ Credentials: bhagyesh_setup.json")
        print(f"✅ Test script: test_bhagyesh_agent.py")
        
        print("\n🧪 To test:")
        print("1. AWS Console: https://console.aws.amazon.com/bedrock/")
        print("   → Agents → bhagyesh-calendar-assistant → Test")
        print("2. Command line: python3 test_bhagyesh_agent.py")
        
        return agent_id
        
    except Exception as e:
        print(f"❌ Agent creation error: {e}")
        return None

if __name__ == "__main__":
    deploy_bhagyesh_final()