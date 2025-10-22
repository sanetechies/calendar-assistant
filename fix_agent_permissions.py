#!/usr/bin/env python3
"""
Fix agent execution role permissions
"""

import boto3
import json

def fix_agent_permissions():
    """Add Bedrock model permissions to agent execution role"""
    
    print("🔧 Fixing agent execution role permissions...")
    
    iam = boto3.client("iam", region_name="us-east-1")
    
    # Bedrock model invoke policy
    bedrock_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": "*"
            }
        ]
    }
    
    role_name = "calendar-assistant-execution-role"
    policy_name = "BedrockModelInvokePolicy"
    
    try:
        # Create the policy
        iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(bedrock_policy),
            Description="Allow Bedrock model invocation for agents"
        )
        print(f"✅ Created policy: {policy_name}")
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"✅ Policy already exists: {policy_name}")
    
    # Get account ID
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    
    # Attach policy to role
    try:
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=f"arn:aws:iam::{account_id}:policy/{policy_name}"
        )
        print(f"✅ Attached policy to role: {role_name}")
    except Exception as e:
        print(f"⚠️  Error attaching policy: {e}")
    
    # Also attach AWS managed Bedrock policy
    try:
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
        )
        print("✅ Attached AmazonBedrockFullAccess policy")
    except Exception as e:
        print(f"⚠️  Error attaching managed policy: {e}")
    
    print("\n🔄 Re-preparing agents...")
    
    # Re-prepare all agents to pick up new permissions
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    
    try:
        agents = bedrock_agent.list_agents()
        for agent in agents.get('agentSummaries', []):
            if 'calendar' in agent['agentName'].lower():
                print(f"🔄 Re-preparing agent: {agent['agentName']}")
                bedrock_agent.prepare_agent(agentId=agent['agentId'])
    except Exception as e:
        print(f"⚠️  Error re-preparing agents: {e}")
    
    print("\n✅ Permissions fixed! Wait 1-2 minutes then test again.")

if __name__ == "__main__":
    fix_agent_permissions()