import asyncio
import json
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import uuid
from datetime import datetime

@dataclass
class A2AMessage:
    """Message structure for agent-to-agent communication"""
    id: str
    sender: str
    receiver: str
    action: str
    payload: Dict[str, Any]
    timestamp: str
    response_to: Optional[str] = None

class A2AProtocol:
    """Protocol for agent-to-agent communication"""
    
    def __init__(self):
        self.agents: Dict[str, Callable] = {}
        self.message_history = []
        self.pending_responses = {}
    
    def register_agent(self, agent_name: str, message_handler: Callable):
        """Register an agent with its message handler"""
        self.agents[agent_name] = message_handler
        print(f"✅ Registered agent: {agent_name}")
    
    async def send_message(
        self, 
        sender: str, 
        receiver: str, 
        action: str, 
        payload: Dict[str, Any],
        response_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a message from one agent to another"""
        
        if receiver not in self.agents:
            raise ValueError(f"Agent {receiver} not registered")
        
        # Create message
        message = A2AMessage(
            id=str(uuid.uuid4()),
            sender=sender,
            receiver=receiver,
            action=action,
            payload=payload,
            timestamp=datetime.now().isoformat(),
            response_to=response_to
        )
        
        # Log message
        self.message_history.append(message)
        print(f"\n📨 A2A Message: {sender} → {receiver}")
        print(f"   Action: {action}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        # Send to receiver and get response
        try:
            response = await self.agents[receiver](message)
            print(f"   Response: {json.dumps(response, indent=2)}")
            return response
        except Exception as e:
            error_response = {
                "status": "error",
                "error": str(e),
                "message_id": message.id
            }
            print(f"   Error: {str(e)}")
            return error_response
    
    def get_message_history(self) -> list:
        """Get message history"""
        return self.message_history