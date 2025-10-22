#!/usr/bin/env python3
"""
Enable Bedrock model access
"""

import boto3

def enable_bedrock_access():
    """Request access to Bedrock models"""
    
    print("🔓 Checking Bedrock model access...")
    
    # Try to invoke a simple model to test access
    bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
    
    try:
        # Test with a simple prompt
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body='{"messages":[{"role":"user","content":"Hello"}],"max_tokens":10,"anthropic_version":"bedrock-2023-05-31"}'
        )
        print("✅ Bedrock runtime access works!")
        return True
        
    except Exception as e:
        print(f"❌ Bedrock runtime error: {e}")
        
        if "AccessDeniedException" in str(e):
            print("\n💡 You need to enable model access:")
            print("1. Go to AWS Console → Bedrock → Model access")
            print("2. Request access to Anthropic Claude models")
            print("3. Wait for approval (usually instant)")
            
        return False

if __name__ == "__main__":
    enable_bedrock_access()