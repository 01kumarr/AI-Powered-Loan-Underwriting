from fastmcp import FastMCP
import json
from typing import Dict, Any
from datetime import datetime
from a2a_protocol import A2AMessage
from llm_provider import LLMProvider

# Import tool MCP and registration function
from server.underwritertool import mcp as tool_mcp, register_tool_state

# Replace your MCP instance with tool MCP
mcp = tool_mcp

# Global variables
a2a_protocol = None
current_application = None
decision_history = []
llm = LLMProvider()

def register_a2a(protocol):
    """Register A2A protocol"""
    global a2a_protocol
    a2a_protocol = protocol

    # Register shared states with the tool AFTER variables are defined
    register_tool_state(
    protocol=a2a_protocol,
    current_app_ref=current_application,
    history_ref=decision_history
)

# A2A Message Handler
async def handle_a2a_message(message: A2AMessage) -> Dict[str, Any]:
    """Handle incoming A2A messages"""
    
    print(f"\n🔔 Underwriter received A2A message")
    print(f"   From: {message.sender}")
    print(f"   Action: {message.action}")
    
    # Underwriter primarily sends messages but can receive updates
    return {
        "status": "acknowledged",
        "message_id": message.id,
        "timestamp": datetime.now().isoformat()
    }

# Run the MCP server
if __name__ == "__main__":
    mcp.run()