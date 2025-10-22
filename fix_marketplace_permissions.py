#!/usr/bin/env python3
"""
Fix marketplace permissions for Bedrock model access
"""

import boto3
import json

def fix_marketplace_permissions():
    """Add marketplace permissions to agent role"""
    
    print("🔧 Adding marketplace permissions...")
    
    iam = boto3.client("iam", region_name="us-east-1")
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    
    # Marketplace policy
    marketplace_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "aws-marketplace:ViewSubscriptions",
                    "aws-marketplace:Subscribe",
                    "aws-marketplace:Unsubscribe"
                ],
                "Resource": "*"
            }
        ]
    }
    
    policy_name = "MarketplaceAccessPolicy"
    role_name = "calendar-assistant-execution-role"
    
    try:
        # Create policy
        iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(marketplace_policy),
            Description="Marketplace access for Bedrock models"
        )
        print(f"✅ Created policy: {policy_name}")
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"✅ Policy already exists: {policy_name}")
    
    # Attach to role
    try:
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=f"arn:aws:iam::{account_id}:policy/{policy_name}"
        )
        print(f"✅ Attached marketplace policy to {role_name}")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    # Re-prepare agents
    print("🔄 Re-preparing agents...")
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    
    try:
        agents = bedrock_agent.list_agents()
        for agent in agents.get('agentSummaries', []):
            if 'calendar' in agent['agentName'].lower():
                bedrock_agent.prepare_agent(agentId=agent['agentId'])
                print(f"🔄 Re-prepared: {agent['agentName']}")
    except Exception as e:
        print(f"⚠️  Error re-preparing: {e}")
    
    print("\n✅ Marketplace permissions added!")
    print("🧪 Test the agent again in AWS Console")

if __name__ == "__main__":
    fix_marketplace_permissions()