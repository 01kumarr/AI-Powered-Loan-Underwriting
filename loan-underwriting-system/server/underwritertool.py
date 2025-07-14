# agents/tool_underwriter.py

from fastmcp import FastMCP
import json
from typing import Dict, Any, List
from datetime import datetime
from llm_provider import LLMProvider
from a2a_protocol import A2AMessage

mcp = FastMCP("Underwriter Agent")
llm = LLMProvider()

# External state references (set via register_tool_state)
a2a_protocol = None
current_application = None
decision_history = []

def register_tool_state(protocol, current_app_ref, history_ref):
    global a2a_protocol, current_application, decision_history
    a2a_protocol = protocol
    current_application = current_app_ref
    decision_history = history_ref


async def llm_analyze_application(application: Dict[str, Any]) -> Dict[str, Any]:
    system_prompt = """You are an expert loan underwriter AI. Analyze loan applications and determine:
    1. What financial documents are needed
    2. Risk assessment criteria
    3. Key factors to investigate
    """

    prompt = f"""Analyze this loan application:
    - Applicant: {application.get('applicant_name')}
    - Loan Amount: ₹{application.get('loan_amount'):,.2f}
    - Business Type: {application.get('business_type')}
    - Purpose: {application.get('loan_purpose')}
    - Years in Business: {application.get('years_in_business', 0)}"""

    analysis = await llm.generate(prompt, system_prompt)
    required_docs = []
    if "gst" in analysis.lower(): required_docs.append("gst")
    if "itr" in analysis.lower() or "income tax" in analysis.lower(): required_docs.append("itr")
    if "bank" in analysis.lower(): required_docs.append("bank_statement")
    if not required_docs:
        if application.get('loan_amount', 0) > 1000000:
            required_docs = ["gst", "itr", "bank_statement"]
        else:
            required_docs = ["itr"]
    return {"analysis": analysis, "required_documents": required_docs}


async def make_llm_decision(application: Dict[str, Any], financial_data: str) -> Dict[str, Any]:
    system_prompt = """You are a senior loan underwriter making final decisions. Based on the application and financial data:
    1. Calculate a risk score (0-100, where 100 is lowest risk)
    2. Make a decision: APPROVED, APPROVED_WITH_CONDITIONS, or REJECTED
    3. Provide clear reasoning
    4. List any conditions
    Format your response as JSON"""

    prompt = f"APPLICATION: {json.dumps(application, indent=2)}\nFINANCIALS: {financial_data}"
    response = await llm.generate(prompt, system_prompt)

    try:
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        decision_data = json.loads(json_match.group()) if json_match else {}
    except:
        decision_data = {}

    return {
        "risk_score": decision_data.get("risk_score", 50),
        "decision": decision_data.get("decision", "MANUAL_REVIEW"),
        "reasoning": decision_data.get("reasoning", response),
        "conditions": decision_data.get("conditions", [])
    }


@mcp.tool()
async def analyze_loan_application(applicant_name: str, loan_amount: float, business_type: str, loan_purpose: str, years_in_business: int = 0, additional_info: str = "") -> str:
    global current_application
    current_application = {
        "applicant_name": applicant_name,
        "loan_amount": loan_amount,
        "business_type": business_type,
        "loan_purpose": loan_purpose,
        "years_in_business": years_in_business,
        "additional_info": additional_info,
        "timestamp": datetime.now().isoformat()
    }

    analysis_steps = [
        "\ud83c\udfe6 INTELLIGENT LOAN UNDERWRITING SYSTEM", "=" * 60,
        f"\ud83d\udccb Applicant: {applicant_name}",
        f"\ud83d\udcb0 Loan Amount: ₹{loan_amount:,.2f}",
        f"\ud83c\udfe2 Business Type: {business_type}",
        f"\ud83d\udcdd Purpose: {loan_purpose}",
        "\n\ud83e\udd16 AI INITIAL ASSESSMENT:"
    ]

    app_analysis = await llm_analyze_application(current_application)
    analysis_steps.append(app_analysis["analysis"])

    if a2a_protocol:
        required_docs = app_analysis["required_documents"]
        analysis_steps.append(f"\n\ud83d\udcc2 Fetching Required Documents: {', '.join(required_docs)}")

        avail_response = await a2a_protocol.send_message(
            sender="underwriter", receiver="datafetcher", action="list_available", payload={}
        )
        if avail_response["status"] == "success":
            available = avail_response["available_data_types"]
            docs_to_fetch = [doc for doc in required_docs if doc in available]
            if docs_to_fetch:
                fetch_response = await a2a_protocol.send_message(
                    sender="underwriter", receiver="datafetcher", action="fetch_and_analyze",
                    payload={"data_types": docs_to_fetch, "analysis_type": "comprehensive"}
                )
                if fetch_response["status"] == "success":
                    analysis_steps.append("\n\ud83d\udcca FINANCIAL DATA ANALYSIS:")
                    analysis_steps.append(fetch_response["summary"])
                    analysis_steps.append("\n\ud83c\udf1f FINAL UNDERWRITING DECISION:")
                    decision = await make_llm_decision(current_application, fetch_response["summary"])
                    analysis_steps.append(f"\u26a1 Risk Score: {decision['risk_score']}/100")
                    analysis_steps.append(f"\ud83d\udccc Decision: {decision['decision']}")
                    analysis_steps.append(f"\ud83d\udcdd Reasoning: {decision['reasoning']}")
                    if decision["conditions"]:
                        analysis_steps.append(f"\ud83d\udccb Conditions: {', '.join(decision['conditions'])}")
                    decision_history.append({"application": current_application, "decision": decision, "timestamp": datetime.now().isoformat()})
                else:
                    analysis_steps.append(f"\u274c Error fetching data: {fetch_response.get('error')}")
    else:
        analysis_steps.append("\n\u26a0\ufe0f A2A Protocol not configured")

    return "\n".join(analysis_steps)


@mcp.tool()
async def request_additional_documents(document_types: List[str], reason: str) -> str:
    if not a2a_protocol:
        return "Error: A2A Protocol not configured"
    response = await a2a_protocol.send_message(
        sender="underwriter", receiver="datafetcher", action="fetch_and_analyze",
        payload={"data_types": document_types, "analysis_type": "detailed", "reason": reason}
    )
    return f"\u2705 Documents Retrieved:\n{response['summary']}" if response["status"] == "success" else f"\u274c Error: {response.get('error')}"


@mcp.tool()
async def search_applicant_info(applicant_name: str, business_name: str = "") -> str:
    if not a2a_protocol:
        return "Error: A2A Protocol not configured"
    term = business_name if business_name else applicant_name
    response = await a2a_protocol.send_message(
        sender="underwriter", receiver="datafetcher", action="search_business",
        payload={"business_name": term, "search_type": "financial"}
    )
    return f"\ud83d\udd0d Search Results:\n{response['search_results'].get('ai_summary')}" if response["status"] == "success" else f"\u274c Error: {response.get('error')}"


@mcp.tool()
async def get_decision_history(limit: int = 5) -> str:
    if not decision_history:
        return "No decisions in history"
    lines = ["\ud83d\udcdc RECENT LOAN DECISIONS", "=" * 50]
    for entry in decision_history[-limit:]:
        app, dec = entry["application"], entry["decision"]
        lines.extend([
            f"\n\ud83d\uddd3 {entry['timestamp']}",
            f"\ud83d\udc64 {app['applicant_name']} - ₹{app['loan_amount']:,.2f}",
            f"\ud83c\udf1f Decision: {dec['decision']}",
            f"\u26a1 Risk Score: {dec['risk_score']}/100",
            "-" * 40
        ])
    return "\n".join(lines)


@mcp.tool()
async def human_underwriter_query(question: str, context: str = "") -> str:
    prompt = f"""As a senior underwriter, answer this:
    Question: {question}
    Context: {context}
    Application: {json.dumps(current_application, indent=2) if current_application else 'None'}"""
    response = await llm.generate(prompt)
    return f"\ud83d\udcad Underwriter Guidance:\n{response}"
