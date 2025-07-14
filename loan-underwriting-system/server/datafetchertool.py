from fastmcp import FastMCP
import os
import json
from typing import Dict, Any, List
from llm_provider import LLMProvider
import httpx

# Init
data_directory = "./data"
llm = LLMProvider()
mcp = FastMCP("DataFetcher Agent")

# 🔧 Core utility functions (can be reused anywhere)
async def fetch_data_core(data_type: str) -> Dict[str, Any]:
    file_path = os.path.join(data_directory, f"{data_type}.json")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return {
            "status": "success",
            "data_type": data_type,
            "data": data,
            "message": f"Successfully fetched {data_type} data"
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "data_type": data_type,
            "message": f"Data file {data_type}.json not found",
            "available_files": os.listdir(data_directory) if os.path.exists(data_directory) else []
        }
    except json.JSONDecodeError:
        return {
            "status": "error",
            "data_type": data_type,
            "message": f"Invalid JSON in {data_type}.json"
        }

async def analyze_financial_data_core(data_type: str) -> str:
    result = await fetch_data_core(data_type)
    if result["status"] == "success":
        return await analyze_financial_health_core(result["data"], data_type)
    else:
        return f"Error: {result['message']}"

async def analyze_financial_health_core(data: Dict[str, Any], data_type: str) -> str:
    system_prompt = """You are a financial analyst AI. Analyze the provided financial data and provide:
    1. Key insights
    2. Risk indicators
    3. Financial health score (0-100)
    4. Recommendations"""
    analysis_prompt = f"""Analyze this {data_type.upper()} data for loan underwriting purposes. 
    Focus on creditworthiness, financial stability, and risk factors."""
    return await llm.analyze_json(data, analysis_prompt)

async def intelligent_summarize_core(data_types: List[str]) -> str:
    all_data = {}
    summaries = []

    for data_type in data_types:
        result = await fetch_data_core(data_type)
        if result["status"] == "success":
            all_data[data_type] = result["data"]
            analysis = await analyze_financial_health_core(result["data"], data_type)
            summaries.append(f"📊 {data_type.upper()} Analysis:\n{analysis}")
        else:
            summaries.append(f"❌ {data_type.upper()}: {result['message']}")

    if len(all_data) > 1:
        comprehensive_prompt = """Based on all the financial data provided, give a comprehensive 
        loan underwriting assessment including:
        1. Overall financial health
        2. Combined risk assessment
        3. Loan approval recommendation
        4. Any red flags or concerns"""
        comprehensive_analysis = await llm.analyze_json(all_data, comprehensive_prompt)
        summaries.append(f"\n🎯 COMPREHENSIVE ASSESSMENT:\n{comprehensive_analysis}")

    return "\n\n".join(summaries)

async def search_business_info_core(business_name: str, search_type: str = "general") -> Dict[str, Any]:
    """Search for business information using DuckDuckGo (free, no API key required)"""
    
    # Build search query based on type
    query_suffix = {
        "financial": "financial reports revenue profit annual report",
        "legal": "legal issues lawsuit compliance violations", 
        "news": "latest news updates announcements",
        "general": "company profile overview business",
        "credit": "credit rating financial stability"
    }.get(search_type, "company information")
    
    search_query = f"{business_name} {query_suffix}"
    
    try:
        async with httpx.AsyncClient() as client:
            # DuckDuckGo instant answer API
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": search_query,
                    "format": "json",
                    "no_html": "1",
                    "skip_disambig": "1"
                },
                timeout=10.0
            )
            data = response.json()
            
            # Also try to get web search results
            web_response = await client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": search_query},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                timeout=10.0
            )
        
        search_results = {
            "business_name": business_name,
            "search_type": search_type,
            "query": search_query,
            "results": []
        }
        
        # Add instant answer if available
        if data.get("Abstract"):
            search_results["results"].append({
                "title": f"{business_name} - Overview",
                "snippet": data["Abstract"],
                "url": data.get("AbstractURL", ""),
                "source": data.get("AbstractSource", "DuckDuckGo")
            })
        
        # Add definition if available
        if data.get("Definition"):
            search_results["results"].append({
                "title": "Definition",
                "snippet": data["Definition"],
                "url": data.get("DefinitionURL", ""),
                "source": data.get("DefinitionSource", "DuckDuckGo")
            })
        
        # Add answer if available
        if data.get("Answer"):
            search_results["results"].append({
                "title": "Quick Answer",
                "snippet": data["Answer"],
                "url": data.get("AnswerType", ""),
                "source": "DuckDuckGo"
            })
        
        # Add related topics
        for topic in data.get("RelatedTopics", [])[:5]:
            if isinstance(topic, dict) and "Text" in topic:
                search_results["results"].append({
                    "title": topic.get("Text", "").split(" - ")[0][:100],
                    "snippet": topic.get("Text", ""),
                    "url": topic.get("FirstURL", ""),
                    "source": "DuckDuckGo Related"
                })
        
        # Add infobox data if available
        if data.get("Infobox"):
            infobox = data["Infobox"]
            if "content" in infobox:
                for item in infobox["content"][:3]:
                    if "value" in item:
                        search_results["results"].append({
                            "title": item.get("label", "Info"),
                            "snippet": item.get("value", ""),
                            "url": "",
                            "source": "DuckDuckGo Infobox"
                        })
        
        # If we have very few results, add a note
        if len(search_results["results"]) < 3:
            search_results["results"].append({
                "title": "Limited Results",
                "snippet": f"DuckDuckGo returned limited results for '{business_name}'. This might indicate a smaller or newer business, or you may want to search with more specific terms.",
                "url": "",
                "source": "System Note"
            })
        
        # Get AI summary of search results
        if search_results["results"]:
            ai_summary = await llm.analyze_json(
                search_results,
                f"""Analyze these search results for {business_name} and provide:
                1. Business credibility assessment based on available information
                2. What information was found vs what's missing
                3. Any potential concerns or red flags
                4. Recommendation for loan underwriting (note if more research is needed)
                Focus on {search_type} aspects."""
            )
            search_results["ai_summary"] = ai_summary
        else:
            search_results["ai_summary"] = f"No substantial search results found for {business_name}. This could indicate a very new business, a small local business, or the need for more specific search terms."
        
        return search_results
        
    except httpx.TimeoutException:
        return {
            "business_name": business_name,
            "search_type": search_type,
            "error": "Search timeout - DuckDuckGo took too long to respond",
            "results": [],
            "ai_summary": "Search timed out. Please try again."
        }
    except Exception as e:
        return {
            "business_name": business_name,
            "search_type": search_type,
            "error": f"Search error: {str(e)}",
            "results": [],
            "ai_summary": f"Search failed due to error: {str(e)}"
        }

def list_available_data_core() -> List[str]:
    files = os.listdir(data_directory) if os.path.exists(data_directory) else []
    return [f.replace('.json', '') for f in files if f.endswith('.json')]

# ✅ MCP Tools using core logic
@mcp.tool()
async def fetch_data(data_type: str) -> Dict[str, Any]:
    """Fetch data from JSON files in the data directory"""
    return await fetch_data_core(data_type)

@mcp.tool()
async def list_available_data() -> List[str]:
    """List all available data files in the data directory"""
    return list_available_data_core()

@mcp.tool()
async def analyze_financial_data(data_type: str) -> str:
    """Fetch and analyze financial data using AI"""
    return await analyze_financial_data_core(data_type)

@mcp.tool()
async def comprehensive_financial_summary(data_types: List[str]) -> str:
    """Create a comprehensive financial summary from multiple data sources"""
    return await intelligent_summarize_core(data_types)

@mcp.tool()
async def search_business_info(business_name: str, search_type: str = "general") -> Dict[str, Any]:
    """Search for business information (enhanced with AI)"""
    return await search_business_info_core(business_name, search_type)

# Export core for reuse
__all__ = [
    "mcp",
    "fetch_data_core",
    "analyze_financial_data_core", 
    "intelligent_summarize_core",
    "search_business_info_core",
    "list_available_data_core"
]