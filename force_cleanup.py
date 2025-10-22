#!/usr/bin/env python3
"""
Force cleanup all Nextcloud Calendar AI resources
"""

import boto3
import time

def force_cleanup():
    """Force delete all resources"""
    
    print("🧹 Force cleaning up Nextcloud Calendar AI resources")
    print("=" * 60)
    
    # Initialize clients
    cf = boto3.client("cloudformation", region_name="us-east-1")
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    lambda_client = boto3.client("lambda", region_name="us-east-1")
    iam = boto3.client("iam", region_name="us-east-1")
    
    # 1. Force delete CloudFormation stack
    print("🗑️ Force deleting CloudFormation stack...")
    try:
        cf.delete_stack(StackName="nextcloud-calendar-ai")
        print("✅ Stack deletion initiated")
    except Exception as e:
        print(f"⚠️ Stack deletion error: {e}")
    
    # 2. Delete Bedrock Agents directly
    print("🗑️ Deleting Bedrock Agents...")
    try:
        agents = bedrock_agent.list_agents()
        for agent in agents.get('agentSummaries', []):
            if 'nextcloud-calendar' in agent['agentName'].lower():
                print(f"   Deleting agent: {agent['agentName']}")
                bedrock_agent.delete_agent(agentId=agent['agentId'])
    except Exception as e:
        print(f"⚠️ Agent deletion error: {e}")
    
    # 3. Delete Lambda functions directly
    print("🗑️ Deleting Lambda functions...")
    functions_to_delete = [
        "nextcloud-calendar-ai",
        "bedrock-agent-custom-resource"
    ]
    
    for func_name in functions_to_delete:
        try:
            lambda_client.delete_function(FunctionName=func_name)
            print(f"   Deleted function: {func_name}")
        except Exception as e:
            print(f"⚠️ Function deletion error: {e}")
    
    # 4. Delete IAM roles directly
    print("🗑️ Deleting IAM roles...")
    roles_to_delete = [
        "nextcloud-calendar-lambda-role",
        "nextcloud-calendar-bedrock-role"
    ]
    
    for role_name in roles_to_delete:
        try:
            # Detach all policies
            attached_policies = iam.list_attached_role_policies(RoleName=role_name)
            for policy in attached_policies['AttachedPolicies']:
                iam.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
            
            # Delete inline policies
            inline_policies = iam.list_role_policies(RoleName=role_name)
            for policy_name in inline_policies['PolicyNames']:
                iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
            
            # Delete role
            iam.delete_role(RoleName=role_name)
            print(f"   Deleted role: {role_name}")
        except Exception as e:
            print(f"⚠️ Role deletion error: {e}")
    
    # 5. Wait and check stack status
    print("\n⏳ Waiting for stack deletion to complete...")
    try:
        cf.get_waiter('stack_delete_complete').wait(
            StackName="nextcloud-calendar-ai",
            WaiterConfig={'MaxAttempts': 30, 'Delay': 10}
        )
        print("✅ Stack deleted successfully")
    except Exception as e:
        print(f"⚠️ Stack deletion timeout: {e}")
    
    print("\n✅ Force cleanup complete!")
    print("All resources should be removed.")

if __name__ == "__main__":
    force_cleanup()