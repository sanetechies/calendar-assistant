#!/usr/bin/env python3
"""
Enable Bedrock model access
"""

import boto3
import json

def enable_model_access():
    """Enable access to Claude model"""
    
    print("🔓 Enabling Bedrock model access...")
    
    bedrock = boto3.client("bedrock", region_name="us-east-1")
    
    try:
        # Try to get model access status
        response = bedrock.list_foundation_models()
        claude_models = [m for m in response['modelSummaries'] if 'claude-3-sonnet' in m['modelId']]
        
        if claude_models:
            print("✅ Claude models are available")
            print(f"Found model: {claude_models[0]['modelId']}")
        else:
            print("❌ Claude models not found")
            
    except Exception as e:
        print(f"❌ Error checking models: {e}")
    
    # The real issue might be that we need to request model access
    print("\n💡 If the agent still fails, you need to:")
    print("1. Go to AWS Console → Bedrock → Model access")
    print("2. Click 'Request model access'")
    print("3. Enable 'Anthropic Claude 3 Sonnet'")
    print("4. Submit request (usually approved instantly)")
    
    # Let's also try to test model access directly
    bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
    
    try:
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10,
                "anthropic_version": "bedrock-2023-05-31"
            })
        )
        print("✅ Model access works for your account")
        
    except Exception as e:
        print(f"❌ Model access error: {e}")
        if "AccessDeniedException" in str(e):
            print("🚨 You need to enable model access in Bedrock console!")

if __name__ == "__main__":
    enable_model_access()