#!/usr/bin/env python3
"""
Update agent to use Claude Sonnet 4
"""

import boto3
import json

def update_model():
    """Update agent to use Claude Sonnet 4"""
    
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    
    # Load agent ID
    with open("bhagyesh_setup_complete.json", "r") as f:
        setup_info = json.load(f)
    
    agent_id = setup_info["agent_id"]
    
    print(f"🔄 Updating agent {agent_id} to use Claude Sonnet 4...")
    
    try:
        sts = boto3.client("sts")
        account_id = sts.get_caller_identity()["Account"]
        
        bedrock_agent.update_agent(
            agentId=agent_id,
            agentName="bhagyesh-calendar-assistant",
            description="Personal calendar assistant for bhagyesh - manages events with natural language",
            foundationModel="anthropic.claude-3-5-sonnet-20241022-v2:0",
            instruction="You are bhagyesh's personal calendar assistant. You help him manage his calendar events. Always address him by name and be friendly and helpful. You can list his events, add new events, and delete events.",
            agentResourceRoleArn=f"arn:aws:iam::{account_id}:role/bhagyesh-bedrock-role"
        )
        print("✅ Updated agent to use Claude Sonnet 4")
        
        # Prepare agent
        bedrock_agent.prepare_agent(agentId=agent_id)
        print("✅ Agent prepared with new model")
        
    except Exception as e:
        print(f"❌ Update error: {e}")

if __name__ == "__main__":
    update_model()