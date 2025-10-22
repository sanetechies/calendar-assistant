#!/usr/bin/env python3
"""
Test the Intelligent Nextcloud Calendar AI Agent
"""

import boto3
import json

def test_nextcloud_agent():
    """Test the deployed Nextcloud Calendar AI agent"""
    
    # Load deployment info
    try:
        with open("deployment_info.json", "r") as f:
            deployment_info = json.load(f)
        agent_id = deployment_info["agent_id"]
    except FileNotFoundError:
        print("❌ Deployment info not found. Run deploy.py first.")
        return
    
    client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
    
    print("🧪 Testing Intelligent Nextcloud Calendar AI Agent")
    print(f"Agent ID: {agent_id}")
    print("=" * 60)
    
    test_queries = [
        "Hello! What can you help me with?",
        "Find me a 1-hour slot tomorrow morning",
        "What's on my calendar today?",
        "Analyze my calendar this week",
        "Reschedule my team meeting to 4 PM today",
        "Suggest optimal time for a client call with 3 people",
        "Create a standup meeting for tomorrow at 9 AM",
        "Move all my Friday meetings to next week"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 40)
        
        try:
            response = client.invoke_agent(
                agentId=agent_id,
                agentAliasId="TSTALIASID",
                sessionId=f"nextcloud-test-{i}",
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
    
    print("\n" + "=" * 60)
    print("🎉 Testing complete!")
    print("\n💡 Advanced queries to try:")
    print("• 'Find time for a 2-hour workshop next week'")
    print("• 'Reschedule all Monday meetings due to holiday'")
    print("• 'What's the best time for a team retrospective?'")
    print("• 'Block 2 hours for deep work tomorrow morning'")
    print("\n🔧 Configure your Nextcloud details in config.json")

if __name__ == "__main__":
    test_nextcloud_agent()