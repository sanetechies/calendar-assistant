#!/usr/bin/env python3
import boto3
import json
import time

def fix_final():
    iam = boto3.client("iam", region_name="us-east-1")
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    
    with open("bhagyesh_setup_complete.json", "r") as f:
        setup_info = json.load(f)
    agent_id = setup_info["agent_id"]
    
    print("🔧 Final fix for all issues...")
    
    # Update policy inline
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
        iam.put_role_policy(
            RoleName="bhagyesh-bedrock-role",
            PolicyName="InlineBedrock",
            PolicyDocument=json.dumps(bedrock_permissions)
        )
        print("✅ Updated role with inline policy")
    except Exception as e:
        print(f"⚠️ Policy error: {e}")
    
    # Wait and prepare agent
    time.sleep(5)
    try:
        bedrock_agent.prepare_agent(agentId=agent_id)
        print("✅ Agent prepared")
    except Exception as e:
        print(f"⚠️ Prepare error: {e}")

if __name__ == "__main__":
    fix_final()