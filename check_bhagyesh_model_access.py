#!/usr/bin/env python3
"""
Check if bhagyesh has Claude model access
"""

import boto3
import json

def check_bhagyesh_model_access():
    """Test Claude access using bhagyesh credentials"""
    
    # Load bhagyesh credentials
    with open("bhagyesh_aws_credentials.json", "r") as f:
        creds = json.load(f)
    
    # Create session with bhagyesh credentials
    session = boto3.Session(
        aws_access_key_id=creds["aws_access_key_id"],
        aws_secret_access_key=creds["aws_secret_access_key"],
        region_name=creds["region"]
    )
    
    bedrock_runtime = session.client("bedrock-runtime")
    
    print("🔍 Testing Claude model access for bhagyesh...")
    print(f"Access Key: {creds['aws_access_key_id']}")
    
    try:
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10,
                "anthropic_version": "bedrock-2023-05-31"
            })
        )
        print("✅ bhagyesh has Claude model access!")
        return True
        
    except Exception as e:
        print(f"❌ bhagyesh Claude access error: {e}")
        
        if "AccessDeniedException" in str(e):
            print("\n🔧 Model access not enabled for this AWS account")
            print("Enable it using root account:")
            print("1. Go to: https://console.aws.amazon.com/bedrock/")
            print("2. Click 'Model access' → 'Request model access'")
            print("3. Enable 'Claude 3 Sonnet'")
            
        return False

if __name__ == "__main__":
    check_bhagyesh_model_access()