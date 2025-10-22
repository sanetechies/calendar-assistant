#!/usr/bin/env python3
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
    print(f"Agent ID: {config['agent_id']}")
    
    queries = [
        "Hello bhagyesh!",
        "What's on my calendar today?",
        "Schedule a team meeting tomorrow at 2 PM"
    ]
    
    for query in queries:
        try:
            print(f"\n📝 Query: {query}")
            
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
            
            print(f"🤖 Response: {result}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Try testing in AWS Console first:")
            print("   https://console.aws.amazon.com/bedrock/ → Agents → bhagyesh-calendar-assistant")

if __name__ == "__main__":
    test_bhagyesh_agent()
