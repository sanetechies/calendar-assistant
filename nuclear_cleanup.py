#!/usr/bin/env python3
"""
Nuclear cleanup - Force delete everything
"""

import boto3
import time

def nuclear_cleanup():
    """Delete everything by force"""
    
    print("💥 NUCLEAR CLEANUP - Force deleting all resources")
    print("=" * 60)
    
    # Initialize clients
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    lambda_client = boto3.client("lambda", region_name="us-east-1")
    iam = boto3.client("iam", region_name="us-east-1")
    cf = boto3.client("cloudformation", region_name="us-east-1")
    
    # 1. Delete ALL Bedrock Agents
    print("🗑️ Deleting ALL Bedrock Agents...")
    try:
        agents = bedrock_agent.list_agents()
        for agent in agents.get('agentSummaries', []):
            try:
                print(f"   Deleting agent: {agent['agentName']} ({agent['agentId']})")
                bedrock_agent.delete_agent(agentId=agent['agentId'])
            except Exception as e:
                print(f"   ⚠️ Failed to delete {agent['agentName']}: {e}")
    except Exception as e:
        print(f"⚠️ Error listing agents: {e}")
    
    # 2. Delete ALL Lambda functions with our prefix
    print("🗑️ Deleting Lambda functions...")
    try:
        functions = lambda_client.list_functions()
        for func in functions['Functions']:
            func_name = func['FunctionName']
            if any(keyword in func_name.lower() for keyword in ['nextcloud', 'calendar', 'bedrock-agent']):
                try:
                    print(f"   Deleting function: {func_name}")
                    lambda_client.delete_function(FunctionName=func_name)
                except Exception as e:
                    print(f"   ⚠️ Failed to delete {func_name}: {e}")
    except Exception as e:
        print(f"⚠️ Error listing functions: {e}")
    
    # 3. Delete ALL related IAM roles
    print("🗑️ Deleting IAM roles...")
    try:
        roles = iam.list_roles()
        for role in roles['Roles']:
            role_name = role['RoleName']
            if any(keyword in role_name.lower() for keyword in ['nextcloud', 'calendar', 'bedrock']):
                try:
                    print(f"   Deleting role: {role_name}")
                    
                    # Detach all managed policies
                    attached_policies = iam.list_attached_role_policies(RoleName=role_name)
                    for policy in attached_policies['AttachedPolicies']:
                        iam.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
                    
                    # Delete all inline policies
                    inline_policies = iam.list_role_policies(RoleName=role_name)
                    for policy_name in inline_policies['PolicyNames']:
                        iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
                    
                    # Delete the role
                    iam.delete_role(RoleName=role_name)
                    
                except Exception as e:
                    print(f"   ⚠️ Failed to delete {role_name}: {e}")
    except Exception as e:
        print(f"⚠️ Error listing roles: {e}")
    
    # 4. Force delete CloudFormation stack with retain policy
    print("🗑️ Force deleting CloudFormation stack...")
    try:
        # Try to delete with retain policy for stuck resources
        cf.delete_stack(
            StackName="nextcloud-calendar-ai",
            RetainResources=[]  # Don't retain anything
        )
        print("✅ Stack deletion re-initiated")
    except Exception as e:
        print(f"⚠️ Stack deletion error: {e}")
    
    # 5. Wait a bit and check
    print("\n⏳ Waiting 30 seconds...")
    time.sleep(30)
    
    try:
        status = cf.describe_stacks(StackName="nextcloud-calendar-ai")['Stacks'][0]['StackStatus']
        print(f"Stack status: {status}")
    except:
        print("✅ Stack appears to be deleted!")
    
    print("\n💥 Nuclear cleanup complete!")
    print("All resources should be forcefully removed.")

if __name__ == "__main__":
    nuclear_cleanup()