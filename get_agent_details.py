#!/usr/bin/env python3
"""
Get your Calendar Assistant agent details
"""

import boto3

def get_agent_details():
    bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")
    
    # List agents
    agents = bedrock_agent.list_agents()
    
    for agent in agents['agentSummaries']:
        if 'calendar' in agent['agentName'].lower():
            agent_id = agent['agentId']
            print(f"Agent ID: {agent_id}")
            print(f"Agent Name: {agent['agentName']}")
            
            # Get aliases
            try:
                aliases = bedrock_agent.list_agent_aliases(agentId=agent_id)
                for alias in aliases['agentAliasSummaries']:
                    print(f"Alias ID: {alias['agentAliasId']}")
                    print(f"Alias Name: {alias['agentAliasName']}")
            except:
                print("No aliases found - use 'TSTALIASID' for testing")
            
            return agent_id
    
    print("No calendar agent found")
    return None

if __name__ == "__main__":
    get_agent_details()