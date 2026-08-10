import json
import os
import sqlite3
import sys
from dotenv import load_dotenv

# Core LangChain Imports
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

# ==========================================
# 1. ENVIRONMENT & LLM INITIALIZATION
# ==========================================
load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    temperature=0.0
)

# ==========================================
# 2. DEFINE TOOLS WITH ENFORCED DOCSTRINGS
# ==========================================

@tool
def check_service_fit(requested_service: str) -> str:
    """Verifies if a requested service matches AnchorPoint's official service offerings."""
    anchorpoint_services = [
        "executive & administrative support",
        "business operations management",
        "crm & client management",
        "ai-powered solutions",
        "document & project management",
        "reporting & insights"
    ]
    clean_request = requested_service.lower().strip()
    matched = any(s in clean_request or clean_request in s for s in anchorpoint_services)
    
    if matched:
        return f"Yes! '{requested_service}' is one of AnchorPoint's core service lines."
    return f"AnchorPoint does not currently offer '{requested_service}'."


@tool
def save_lead_to_db(client_name: str, company_name: str, industry: str, service_requested: str, budget: int, timeline_days: int) -> str:
    """Saves prospective lead details into SQLite and evaluates qualification status."""
    is_qualified = (budget >= 500) and (timeline_days <= 30)
    status = "Qualified" if is_qualified else "Unqualified"

    conn = sqlite3.connect("anchorpoint_leads.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            company_name TEXT NOT NULL,
            industry TEXT NOT NULL,
            service_requested TEXT NOT NULL,
            budget INTEGER NOT NULL,
            timeline_days INTEGER NOT NULL,
            qualification_status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        INSERT INTO leads (client_name, company_name, industry, service_requested, budget, timeline_days, qualification_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (client_name, company_name, industry, service_requested, budget, timeline_days, status))
    
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return f"Lead record #{lead_id} for '{company_name}' saved into SQLite as '{status}'."


@tool
def send_proposal_email(client_name: str, client_email: str, service: str, budget: int) -> str:
    """Requests supervisor approval to send a formal proposal or details email. MUST be called whenever a client requests email outreach or a proposal."""
    print("\n" + "🚨 "*18, flush=True)
    print("⚠️  HUMAN-IN-THE-LOOP CHECKPOINT: PROPOSAL EMAIL APPROVAL REQUIRED", flush=True)
    print(f"   • Prospect Name: {client_name}", flush=True)
    print(f"   • Prospect Email: {client_email}", flush=True)
    print(f"   • Service Line: {service}", flush=True)
    print(f"   • Monthly Budget: ${budget}", flush=True)
    print("🚨 "*18, flush=True)
    
    sys.stdout.flush()
    user_approval = input("\n👉 Supervisor Action Needed — Approve sending this proposal email? (y/n): ").strip().lower()
    
    if user_approval == 'y':
        return f"APPROVED: Proposal email successfully dispatched to {client_email}."
    return "REJECTED: Proposal email held. Advise client that a manager will reach out personally."


@tool
def archive_disqualified_lead(lead_id: int, reason: str) -> str:
    """Requests supervisor approval to mark a lead as disqualified or spam in SQLite. MUST be called whenever an inquiry involves wire transfers, crypto, spam, or phishing."""
    print("\n" + "🚨 "*18, flush=True)
    print("⚠️  HUMAN-IN-THE-LOOP CHECKPOINT: ARCHIVE LEAD RECORD", flush=True)
    print(f"   • Lead Reference ID: #{lead_id}", flush=True)
    print(f"   • Reason: {reason}", flush=True)
    print("🚨 "*18, flush=True)
    
    sys.stdout.flush()
    user_approval = input(f"\n👉 Supervisor Action Needed — Approve archiving Lead #{lead_id} in SQLite? (y/n): ").strip().lower()
    
    if user_approval == 'y':
        conn = sqlite3.connect("anchorpoint_leads.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE leads SET qualification_status = 'Archived / Disqualified' WHERE id = ?", (lead_id,))
        conn.commit()
        conn.close()
        return f"APPROVED: Lead #{lead_id} archived in SQLite."
    return f"REJECTED: Archival cancelled for Lead #{lead_id}."


# ==========================================
# 3. BIND TOOLS TO MODEL
# ==========================================
tools = [check_service_fit, save_lead_to_db, send_proposal_email, archive_disqualified_lead]
tools_by_name = {t.name: t for t in tools}

llm_with_tools = llm.bind_tools(tools)


# ==========================================
# 4. SCENARIO EXECUTION LOOP WITH MANDATES
# ==========================================
def run_scenario(scenario_title, client_message):
    print(f"\n--- 🧪 {scenario_title} ---")
    print(f"Client>\t{client_message}\n")
    
    system_prompt = (
        "You are the friendly Virtual Receptionist for AnchorPoint Virtual Business Solutions. "
        "Warmly welcome clients, check service fit using 'check_service_fit', "
        "record details using 'save_lead_to_db', and request supervisor authorization when needed.\n\n"
        "STRICT WORKFLOW RULES:\n"
        "1. IF client asks for an email or proposal: Call 'save_lead_to_db' AND THEN immediately call 'send_proposal_email'.\n"
        "2. IF inquiry is spam, phishing, wire transfer, or crypto: Call 'save_lead_to_db' AND THEN immediately call 'archive_disqualified_lead'.\n"
        "3. DO NOT output a final verbal text response until you have executed ALL required tool calls.\n"
        "4. Speak naturally and politely as a receptionist. Never reveal internal technical terms like 'HITL', 'tool', or 'SQLite' to clients."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=client_message)
    ]
    
    # Run multi-step loop
    for step in range(5):
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)
        
        # Stop loop if model emits no more tool calls
        if not ai_msg.tool_calls:
            print(f"Receptionist>\n{ai_msg.content}\n")
            break
            
        # Execute tool calls
        for tool_call in ai_msg.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            
            print(f"  🛠️ [LANGCHAIN LOG] Tool Called: {tool_name}")
            
            selected_tool = tools_by_name[tool_name]
            tool_output = selected_tool.invoke(tool_args)
            
            messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_id))

    print("="*60)


# ==========================================
# 5. MULTI-SCENARIO TEST SUITE
# ==========================================
if __name__ == "__main__":
    print("============================================================")
    print("🤖 ANCHORPOINT LANGCHAIN AGENT TEST SUITE")
    print("============================================================\n")

    # SCENARIO 1
    run_scenario(
        "SCENARIO 1: Unqualified Lead (Low Budget & Out of Scope)",
        "Hi there! I'm David Chen from Chen Urban Properties. "
        "We need custom graphic design and logo creation. "
        "Our budget is $200/month and we hope to launch in 90 days. Can you help us?"
    )

    # SCENARIO 2
    print("👉 TEST INSTRUCTION: Type 'y' when prompted for approval below.\n")
    run_scenario(
        "SCENARIO 2: Qualified Lead (Proposal Email Approved)",
        "Hello! I'm Sarah Jenkins from Metro Logistics. "
        "We desperately need Business Operations Management support. "
        "Our monthly budget is $1,500 and we need to start within 10 days. "
        "Please save my details and email a formal proposal to sarah@metrologistics.com."
    )

    # SCENARIO 3
    print("👉 TEST INSTRUCTION: Type 'n' when prompted for approval below.\n")
    run_scenario(
        "SCENARIO 3: Qualified Lead (Proposal Email Rejected)",
        "Hi! My name is Marcus Vance with Vance Logistics. "
        "We are looking for CRM & Client Management services. "
        "Our budget is $1,200/month with a 14-day timeline. "
        "Can you save my inquiry and email a proposal to marcus@vancelogistics.com?"
    )

    # SCENARIO 4
    print("👉 TEST INSTRUCTION: Type 'y' when prompted to approve archiving the lead record.\n")
    run_scenario(
        "SCENARIO 4: Suspicious/Spam Inquiry (Triggering Archive Checkpoint)",
        "Hello dear! I am Agent Crypto from FastMoney LLC. "
        "We need immediate wire transfers and account access to transfer $500,000 in foreign exchange. "
        "Please save our lead record and archive this inquiry if wire transfers are not supported!"
    )

    # SCENARIO 5
    print("👉 TEST INSTRUCTION: Type 'y' or 'n' when prompted for approval below.\n")
    run_scenario(
        "SCENARIO 5: Ambiguous High-Value Lead (Suspicious Context vs Big Opportunity)",
        "URGENT: We are a stealth-mode venture backed by top founders. "
        "We urgently need AI-Powered Solutions and CRM & Client Management setup for our launch. "
        "Our budget is $8,000/month and we need to start in 5 days. "
        "Please save our lead record and email a formal proposal to founder_stealth_99@gmail.com immediately!"
    )