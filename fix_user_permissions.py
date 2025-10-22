#!/usr/bin/env python3
"""
Fix user permissions for Bedrock access
"""

import boto3

def fix_user_permissions():
    """Add Bedrock permissions to current user"""
    
    iam = boto3.client("iam", region_name="us-east-1")
    sts = boto3.client("sts")
    
    # Get current user identity
    identity = sts.get_caller_identity()
    user_arn = identity["Arn"]
    
    print(f"Current user: {user_arn}")
    
    if ":root" in user_arn:
        print("✅ You're using root account - should have all permissions")
        print("The issue might be that Bedrock model access isn't enabled.")
        print("\n🔧 Enable model access:")
        print("1. Go to: https://console.aws.amazon.com/bedrock/")
        print("2. Click 'Model access' in left menu")
        print("3. Click 'Request model access'")
        print("4. Enable 'Anthropic Claude 3 Sonnet'")
        print("5. Submit request (approved instantly)")
        
    else:
        # Extract username if it's an IAM user
        if ":user/" in user_arn:
            username = user_arn.split(":user/")[1]
            
            try:
                # Attach Bedrock policy
                iam.attach_user_policy(
                    UserName=username,
                    PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
                )
                print(f"✅ Added Bedrock permissions to user: {username}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n🧪 Test again in 1-2 minutes:")
        print("python3 test_calendar_assistant.py")

if __name__ == "__main__":
    fix_user_permissions()