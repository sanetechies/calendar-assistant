#!/usr/bin/env python3
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
    
    agent_id = "TTVDEQH6ON"
    
    print("🧪 Testing bhagyesh's Calendar Assistant")
    print(f"Agent ID: {agent_id}")
    
    queries = [
        "Hello bhagyesh!",
        "What's on my calendar today?",
        "Add a team meeting tomorrow at 2 PM",
        "Delete my 3 PM appointment"
    ]
    
    for query in queries:
        try:
            print(f"\n📝 Query: {query}")
            
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
            
            print(f"🤖 Response: {result}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_bhagyesh_calendar()
