#!/usr/bin/env python3
"""
Complete cleanup of all Calendar Assistant resources
"""

import boto3
import time

def cleanup_all():
    """Remove all Calendar Assistant resources"""
    
    print("🧹 Complete cleanup of Calendar Assistant resources")
    print("=" * 60)
    
    # Initialize clients
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    s3 = boto3.client("s3", region_name="us-east-1")
    lambda_client = boto3.client("lambda", region_name="us-east-1")
    iam = boto3.client("iam", region_name="us-east-1")
    
    # 1. Delete Bedrock Agents
    print("🗑️  Deleting Bedrock Agents...")
    try:
        agents = bedrock_agent.list_agents()
        for agent in agents.get('agentSummaries', []):
            if 'calendar' in agent['agentName'].lower():
                print(f"   Deleting agent: {agent['agentName']}")
                bedrock_agent.delete_agent(agentId=agent['agentId'])
    except Exception as e:
        print(f"   Error: {e}")
    
    # 2. Delete S3 Buckets
    print("🗑️  Deleting S3 Buckets...")
    try:
        buckets = s3.list_buckets()
        for bucket in buckets['Buckets']:
            if 'calendar-assistant-schema' in bucket['Name']:
                print(f"   Deleting bucket: {bucket['Name']}")
                # Delete objects first
                try:
                    objects = s3.list_objects_v2(Bucket=bucket['Name'])
                    if 'Contents' in objects:
                        for obj in objects['Contents']:
                            s3.delete_object(Bucket=bucket['Name'], Key=obj['Key'])
                    s3.delete_bucket(Bucket=bucket['Name'])
                except:
                    pass
    except Exception as e:
        print(f"   Error: {e}")
    
    # 3. Delete Lambda Functions
    print("🗑️  Deleting Lambda Functions...")
    functions_to_delete = [
        "calendar-assistant-function",
        "bhagyesh-calendar-function"
    ]
    
    for func_name in functions_to_delete:
        try:
            lambda_client.delete_function(FunctionName=func_name)
            print(f"   Deleted function: {func_name}")
        except:
            pass
    
    # 4. Delete IAM Roles and Policies
    print("🗑️  Deleting IAM Roles and Policies...")
    
    roles_to_delete = [
        "calendar-assistant-execution-role",
        "calendar-assistant-lambda-role",
        "bhagyesh-calendar-lambda-role",
        "bhagyesh-lambda-role",
        "bhagyesh-bedrock-role"
    ]
    
    policies_to_delete = [
        "calendar-assistant-lambda-policy",
        "bhagyesh-calendar-lambda-invoke",
        "bhagyesh-lambda-invoke",
        "BedrockModelInvokePolicy",
        "MarketplaceAccessPolicy"
    ]
    
    # Delete roles
    for role_name in roles_to_delete:
        try:
            # Detach all policies first
            attached_policies = iam.list_attached_role_policies(RoleName=role_name)
            for policy in attached_policies['AttachedPolicies']:
                iam.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
            
            # Delete role
            iam.delete_role(RoleName=role_name)
            print(f"   Deleted role: {role_name}")
        except:
            pass
    
    # Delete policies
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    
    for policy_name in policies_to_delete:
        try:
            iam.delete_policy(PolicyArn=f"arn:aws:iam::{account_id}:policy/{policy_name}")
            print(f"   Deleted policy: {policy_name}")
        except:
            pass
    
    # 5. Delete IAM Users
    print("🗑️  Deleting IAM Users...")
    try:
        # Delete bhagyesh user
        keys = iam.list_access_keys(UserName="bhagyesh")
        for key in keys['AccessKeyMetadata']:
            iam.delete_access_key(UserName="bhagyesh", AccessKeyId=key['AccessKeyId'])
        
        # Detach policies
        attached_policies = iam.list_attached_user_policies(UserName="bhagyesh")
        for policy in attached_policies['AttachedPolicies']:
            iam.detach_user_policy(UserName="bhagyesh", PolicyArn=policy['PolicyArn'])
        
        iam.delete_user(UserName="bhagyesh")
        print("   Deleted user: bhagyesh")
    except:
        pass
    
    print("\n✅ Cleanup complete!")
    print("All Calendar Assistant resources have been removed.")

if __name__ == "__main__":
    cleanup_all()