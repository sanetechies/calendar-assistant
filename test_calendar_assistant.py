#!/usr/bin/env python3
"""
Test Calendar Assistant
"""

import boto3

def test_calendar_assistant():
    """Test the deployed Calendar Assistant"""
    
    client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
    
    agent_id = "LZTDQFRFLN"
    
    print("🧪 Testing Calendar Assistant")
    print(f"Agent ID: {agent_id}")
    
    queries = [
        "Hello! What can you help me with?",
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
                sessionId="test-session",
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
            print("💡 Try testing in AWS Console:")
            print("   https://console.aws.amazon.com/bedrock/ → Agents → calendar-assistant")

if __name__ == "__main__":
    test_calendar_assistant()
