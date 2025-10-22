#!/usr/bin/env python3
"""
Simple script to check and enable Claude model access
"""

import boto3

def check_model_access():
    """Check if Claude models are accessible"""
    
    print("🔍 Checking Claude model access...")
    
    bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
    
    # Test Claude 3 Sonnet
    try:
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body='{"messages":[{"role":"user","content":"Hello"}],"max_tokens":10,"anthropic_version":"bedrock-2023-05-31"}'
        )
        print("✅ Claude 3 Sonnet access works!")
        return True
        
    except Exception as e:
        print(f"❌ Claude access error: {e}")
        
        if "AccessDeniedException" in str(e):
            print("\n🔧 Enable model access:")
            print("1. Go to: https://console.aws.amazon.com/bedrock/")
            print("2. Click 'Model access' in left menu")
            print("3. Click 'Request model access'")
            print("4. Enable 'Claude 3 Sonnet' or 'Claude 3.5 Sonnet'")
            print("5. Submit request (approved instantly)")
            
        return False

if __name__ == "__main__":
    check_model_access()