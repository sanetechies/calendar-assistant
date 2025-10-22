#!/usr/bin/env python3
import boto3
import json

def fix_bedrock_role():
    iam = boto3.client("iam", region_name="us-east-1")
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    
    print("🔧 Fixing Bedrock role permissions...")
    
    # Enhanced Bedrock permissions
    bedrock_permissions = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:GetPrompt",
                    "bedrock:ListPrompts"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": f"arn:aws:lambda:us-east-1:{account_id}:function:bhagyesh-calendar-function"
            }
        ]
    }
    
    try:
        # Delete existing policy
        iam.delete_policy(PolicyArn=f"arn:aws:iam::{account_id}:policy/bhagyesh-bedrock-policy")
        print("✅ Deleted old policy")
    except:
        pass
    
    # Create new policy
    iam.create_policy(
        PolicyName="bhagyesh-bedrock-policy",
        PolicyDocument=json.dumps(bedrock_permissions),
        Description="Enhanced Bedrock permissions for bhagyesh"
    )
    
    # Attach to role
    iam.attach_role_policy(
        RoleName="bhagyesh-bedrock-role",
        PolicyArn=f"arn:aws:iam::{account_id}:policy/bhagyesh-bedrock-policy"
    )
    
    print("✅ Fixed Bedrock role permissions")

if __name__ == "__main__":
    fix_bedrock_role()