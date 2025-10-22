#!/usr/bin/env python3
"""
Direct test of agent invocation
"""

import boto3
import json

def direct_test():
    """Direct test with explicit permissions"""
    
    # Create client with explicit region
    client = boto3.client(
        'bedrock-agent-runtime',
        region_name='us-east-1'
    )
    
    print("🔍 Testing direct agent invocation...")
    
    try:
        # Simple invoke
        response = client.invoke_agent(
            agentId='KIW1YTWQH6',
            agentAliasId='TSTALIASID', 
            sessionId='direct-test',
            inputText='Hello'
        )
        
        print("✅ Invocation successful!")
        
        # Read response
        completion = response.get('completion', [])
        result = ""
        
        for event in completion:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    result += chunk['bytes'].decode('utf-8')
        
        print(f"Agent response: {result}")
        
    except client.exceptions.AccessDeniedException as e:
        print(f"❌ Access Denied: {e}")
        print("\n🔧 Quick fix - run this AWS CLI command:")
        print("aws iam attach-user-policy --user-name YOUR_USERNAME --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess")
        
    except Exception as e:
        print(f"❌ Other error: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    direct_test()