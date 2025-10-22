#!/usr/bin/env python3
import boto3
import json

def fix_role():
    iam = boto3.client("iam", region_name="us-east-1")
    
    # Delete and recreate the role with correct trust policy
    try:
        iam.detach_role_policy(
            RoleName="bhagyesh-lambda-role",
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        )
        iam.delete_role(RoleName="bhagyesh-lambda-role")
        print("✅ Deleted old role")
    except:
        pass
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    iam.create_role(
        RoleName="bhagyesh-lambda-role",
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description="Lambda execution role for bhagyesh's Calendar Assistant"
    )
    
    iam.attach_role_policy(
        RoleName="bhagyesh-lambda-role",
        PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    )
    
    print("✅ Fixed Lambda role")

if __name__ == "__main__":
    fix_role()