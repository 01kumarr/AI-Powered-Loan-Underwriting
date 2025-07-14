from datetime import datetime
from typing import Dict, Any
from a2a_protocol import A2AMessage

# Import the MCP tools and core functions
from server.datafetchertool import (
    fetch_data_core,
    analyze_financial_data_core,
    intelligent_summarize_core,
    search_business_info_core,
    list_available_data_core,
    mcp
)

# Global variables for A2A
a2a_protocol = None

def register_a2a(protocol):
    """Register A2A protocol"""
    global a2a_protocol
    a2a_protocol = protocol

# A2A Message Handler
async def handle_a2a_message(message: A2AMessage) -> Dict[str, Any]:
    """Handle incoming A2A messages from other agents"""
    
    print(f"\n🔔 DataFetcher received A2A message")
    print(f"   From: {message.sender}")
    print(f"   Action: {message.action}")
    
    try:
        if message.action == "fetch_and_analyze":
            data_types = message.payload.get("data_types", [])
            analysis_type = message.payload.get("analysis_type", "comprehensive")
            
            if analysis_type == "comprehensive":
                # Use the core function directly
                summary = await intelligent_summarize_core(data_types)
            else:
                # Individual analysis
                summaries = []
                for data_type in data_types:
                    analysis = await analyze_financial_data_core(data_type)
                    summaries.append(f"{data_type.upper()}:\n{analysis}")
                summary = "\n\n".join(summaries)
            
            return {
                "status": "success",
                "message_id": message.id,
                "summary": summary,
                "data_types_processed": data_types,
                "timestamp": datetime.now().isoformat()
            }
        
        elif message.action == "search_business":
            business_name = message.payload.get("business_name", "")
            search_type = message.payload.get("search_type", "general")
            
            # Use the core function directly
            search_results = await search_business_info_core(business_name, search_type)
            
            return {
                "status": "success",
                "message_id": message.id,
                "search_results": search_results,
                "timestamp": datetime.now().isoformat()
            }
        
        elif message.action == "list_available":
            # Use the core function directly
            available_data = list_available_data_core()
            
            return {
                "status": "success",
                "message_id": message.id,
                "available_data_types": available_data,
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            return {
                "status": "error",
                "message_id": message.id,
                "error": f"Unknown action: {message.action}",
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        import traceback
        print(f"   Error details: {traceback.format_exc()}")
        return {
            "status": "error",
            "message_id": message.id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Run the MCP server if this file is executed directly
if __name__ == "__main__":
    mcp.run()