#!/usr/bin/env python3
"""
Fix all permissions for bhagyesh calendar assistant
"""

import boto3
import json

def fix_permissions():
    """Fix all permissions"""
    
    iam = boto3.client("iam", region_name="us-east-1")
    
    print("🔧 Fixing permissions...")
    
    # Add correct Lambda policy to bhagyesh
    try:
        iam.attach_user_policy(
            UserName="bhagyesh",
            PolicyArn="arn:aws:iam::aws:policy/AWSLambda_FullAccess"
        )
        print("✅ Attached AWSLambda_FullAccess to bhagyesh")
    except Exception as e:
        print(f"⚠️  Lambda policy error: {e}")
    
    # Add Bedrock Agent Runtime permissions to bhagyesh
    bedrock_runtime_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock-agent-runtime:InvokeAgent",
                    "bedrock-runtime:InvokeModel",
                    "bedrock-runtime:InvokeModelWithResponseStream"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        iam.create_policy(
            PolicyName="bhagyesh-bedrock-runtime-policy",
            PolicyDocument=json.dumps(bedrock_runtime_policy),
            Description="Bedrock runtime permissions for bhagyesh"
        )
        print("✅ Created Bedrock runtime policy")
    except Exception as e:
        print(f"⚠️  Runtime policy creation error: {e}")
    
    # Attach runtime policy to bhagyesh
    try:
        sts = boto3.client("sts")
        account_id = sts.get_caller_identity()["Account"]
        
        iam.attach_user_policy(
            UserName="bhagyesh",
            PolicyArn=f"arn:aws:iam::{account_id}:policy/bhagyesh-bedrock-runtime-policy"
        )
        print("✅ Attached runtime policy to bhagyesh")
    except Exception as e:
        print(f"⚠️  Runtime policy attach error: {e}")
    
    print("\n✅ Permissions fixed!")
    print("\n⚠️  IMPORTANT: You must enable model access in Bedrock console:")
    print("1. Go to: https://console.aws.amazon.com/bedrock/")
    print("2. Click 'Model access' in left menu")
    print("3. Click 'Request model access'")
    print("4. Enable 'Claude 3.5 Sonnet (latest available model)")
    print("5. Submit (approved instantly)")

if __name__ == "__main__":
    fix_permissions()