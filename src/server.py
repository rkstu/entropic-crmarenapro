"""
Entropic CRMArena Green Agent Server

A2A-compliant Green Agent for CRM agent evaluation with adversarial
robustness testing (Schema Drift + Context Rot + 7D Scoring).
"""

import argparse
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from executor import Executor


def create_agent_card(card_url: str) -> AgentCard:
    """Create the Entropic CRMArena agent card with all skills."""
    
    # Define CRM evaluation skills
    skills = [
        AgentSkill(
            id="crm-database",
            name="CRM Database Operations",
            description="Evaluate agent's ability to query CRM databases, understand schema, and extract information",
            tags=["database", "sql", "crm", "salesforce"],
            examples=[
                "Find all leads with status 'Qualified'",
                "Get case details for case number 12345",
                "List opportunities closing this month"
            ]
        ),
        AgentSkill(
            id="crm-reasoning",
            name="CRM Multi-hop Reasoning",
            description="Evaluate agent's ability to perform complex reasoning across multiple CRM records",
            tags=["reasoning", "multi-hop", "analysis"],
            examples=[
                "Which region has the highest conversion rate?",
                "What's the average handle time for priority cases?",
                "Identify leads that fail BANT qualification"
            ]
        ),
        AgentSkill(
            id="schema-drift-adaptation",
            name="Schema Drift Adaptation",
            description="Test agent's robustness to renamed/modified database columns",
            tags=["robustness", "schema", "adaptation", "adversarial"],
            examples=[
                "Handle queries when 'owner_id' is renamed to 'assigned_agent'",
                "Adapt to column name changes without explicit notification"
            ]
        ),
        AgentSkill(
            id="context-rot-filtering",
            name="Context Rot Filtering",
            description="Test agent's ability to filter irrelevant distractor records",
            tags=["robustness", "filtering", "context", "adversarial"],
            examples=[
                "Identify correct records when results contain temporal distractors",
                "Filter confusing similar records from query results"
            ]
        ),
        AgentSkill(
            id="privacy-awareness",
            name="Privacy Awareness",
            description="Test agent's ability to refuse revealing sensitive information",
            tags=["privacy", "security", "compliance"],
            examples=[
                "Properly refuse to reveal customer PII",
                "Protect confidential company information"
            ]
        ),
    ]
    
    agent_card = AgentCard(
        name="Entropic CRMArena",
        description=(
            "A2A Green Agent for CRM agent evaluation with adversarial robustness testing. "
            "Features: Schema Drift (tests adaptation to renamed columns), "
            "Context Rot (tests filtering of distractor records), "
            "7-Dimension Scoring (FUNCTIONAL, DRIFT_ADAPTATION, TOKEN_EFFICIENCY, "
            "QUERY_EFFICIENCY, ERROR_RECOVERY, TRAJECTORY_EFFICIENCY, HALLUCINATION_RATE). "
            "Based on Salesforce CRMArena benchmark with 22 task categories."
        ),
        url=card_url,
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=skills
    )
    
    return agent_card


def main():
    parser = argparse.ArgumentParser(description="Run Entropic CRMArena A2A Green Agent")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server")
    parser.add_argument("--port", type=int, default=9009, help="Port to bind the server")
    parser.add_argument("--card-url", type=str, help="URL to advertise in the agent card")
    args = parser.parse_args()

    card_url = args.card_url or f"http://{args.host}:{args.port}/"
    agent_card = create_agent_card(card_url)

    request_handler = DefaultRequestHandler(
        agent_executor=Executor(),
        task_store=InMemoryTaskStore(),
    )
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    
    print("=" * 60)
    print("Entropic CRMArena A2A Green Agent")
    print("=" * 60)
    print(f"Server: http://{args.host}:{args.port}/")
    print(f"Agent Card: {card_url}")
    print("")
    print("Features:")
    print("  - Schema Drift: Tests agent adaptation to column renames")
    print("  - Context Rot: Tests agent filtering of distractor records")
    print("  - 7D Scoring: FUNCTIONAL, DRIFT_ADAPTATION, TOKEN_EFFICIENCY,")
    print("                QUERY_EFFICIENCY, ERROR_RECOVERY, TRAJECTORY_EFFICIENCY,")
    print("                HALLUCINATION_RATE")
    print("  - CRMArena: 22 task categories from Salesforce benchmark")
    print("=" * 60)
    
    uvicorn.run(server.build(), host=args.host, port=args.port)


if __name__ == '__main__':
    main()
