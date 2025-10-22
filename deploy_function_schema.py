#!/usr/bin/env python3
"""
Deploy with function schema instead of API schema
"""

import boto3
import json

def deploy_function_schema():
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    
    lambda_arn = f"arn:aws:lambda:us-east-1:{account_id}:function:calendar-assistant-function"
    
    # Get agent
    agents = bedrock_agent.list_agents()
    agent_id = agents['agentSummaries'][0]['agentId']
    
    print(f"Using agent: {agent_id}")
    
    # Function schema approach
    function_schema = {
        "functions": [
            {
                "name": "manageCalendar",
                "description": "Manage calendar events",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform: list, add, delete, reschedule"
                    },
                    "summary": {
                        "type": "string", 
                        "description": "Event title"
                    },
                    "startTime": {
                        "type": "string",
                        "description": "Start time"
                    }
                }
            }
        ]
    }
    
    try:
        response = bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion="DRAFT",
            actionGroupName="CalendarFunctions",
            description="Calendar management functions",
            actionGroupExecutor={"lambda": lambda_arn},
            functionSchema={"functions": function_schema["functions"]}
        )
        print("✅ Created action group with function schema")
        
        # Prepare agent
        bedrock_agent.prepare_agent(agentId=agent_id)
        print("✅ Agent prepared")
        
        print(f"🎉 Success! Agent ID: {agent_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    deploy_function_schema()