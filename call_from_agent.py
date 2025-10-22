#!/usr/bin/env python3
"""
Call Calendar Assistant from another Bedrock Agent
"""

import boto3
import json

def call_calendar_agent(user_input, session_id="test-session"):
    """Call the Calendar Assistant agent"""
    
    bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
    
    # Your agent details
    agent_id = "KIW1YTWQH6"  # Replace with your actual agent ID
    agent_alias_id = "TSTALIASID"  # Or use actual alias ID
    
    try:
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=user_input
        )
        
        # Process streaming response
        result = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    result += chunk['bytes'].decode('utf-8')
        
        return result
        
    except Exception as e:
        return f"Error calling agent: {e}"

# Example usage
if __name__ == "__main__":
    # Test the agent
    queries = [
        "What's on my calendar today?",
        "Schedule a meeting tomorrow at 2 PM",
        "Cancel my appointment with John"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        response = call_calendar_agent(query)
        print(f"Response: {response}\n")