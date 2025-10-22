#!/usr/bin/env python3
"""
Call Calendar Assistant from a Lambda function
"""

import boto3
import json

def lambda_handler(event, context):
    """Lambda function to call Calendar Assistant"""
    
    # Extract user input from event
    user_input = event.get('user_input', 'What\'s on my calendar today?')
    session_id = event.get('session_id', 'lambda-session')
    
    bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
    
    agent_id = "KIW1YTWQH6"  # Replace with your agent ID
    agent_alias_id = "TSTALIASID"  # Replace with your alias ID
    
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
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': result,
                'user_input': user_input
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

# For local testing
if __name__ == "__main__":
    test_event = {
        'user_input': 'Schedule a meeting tomorrow at 3 PM',
        'session_id': 'test-123'
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))