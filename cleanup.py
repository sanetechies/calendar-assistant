#!/usr/bin/env python3
"""
Cleanup Nextcloud Calendar AI Agent resources
"""

import boto3
import json

def cleanup_nextcloud_agent():
    """Remove all Nextcloud Calendar AI Agent resources"""
    
    print("🧹 Cleaning up Nextcloud Calendar AI Agent")
    print("=" * 50)
    
    # Initialize clients
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    lambda_client = boto3.client("lambda", region_name="us-east-1")
    iam = boto3.client("iam", region_name="us-east-1")
    
    # Load deployment info
    try:
        with open("deployment_info.json", "r") as f:
            deployment_info = json.load(f)
        agent_id = deployment_info.get("agent_id")
    except FileNotFoundError:
        agent_id = None
    
    # Delete Bedrock Agent
    if agent_id:
        try:
            bedrock_agent.delete_agent(agentId=agent_id)
            print("✅ Deleted Bedrock agent")
        except Exception as e:
            print(f"⚠️ Agent deletion error: {e}")
    
    # Delete Lambda function
    try:
        lambda_client.delete_function(FunctionName="nextcloud-calendar-ai")
        print("✅ Deleted Lambda function")
    except Exception as e:
        print(f"⚠️ Lambda deletion error: {e}")
    
    # Delete IAM roles
    roles_to_delete = [
        "nextcloud-calendar-lambda-role",
        "nextcloud-calendar-bedrock-role"
    ]
    
    for role_name in roles_to_delete:
        try:
            # Detach policies
            attached_policies = iam.list_attached_role_policies(RoleName=role_name)
            for policy in attached_policies['AttachedPolicies']:
                iam.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
            
            # Delete inline policies
            inline_policies = iam.list_role_policies(RoleName=role_name)
            for policy_name in inline_policies['PolicyNames']:
                iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
            
            # Delete role
            iam.delete_role(RoleName=role_name)
            print(f"✅ Deleted role: {role_name}")
        except Exception as e:
            print(f"⚠️ Role deletion error: {e}")
    
    print("\n✅ Cleanup complete!")
    print("All Nextcloud Calendar AI Agent resources removed.")

if __name__ == "__main__":
    cleanup_nextcloud_agent()