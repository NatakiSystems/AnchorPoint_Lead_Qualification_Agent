import json
import logging
import os
import sqlite3
import sys
from dotenv import load_dotenv
from openai import OpenAI

# ==========================================
# 1. LOGGING & ENVIRONMENT SETUP
# ==========================================

# Configure clear console logging for developer transparency
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Load environment variables from .env
load_dotenv()

# Initialize DeepSeek client
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


# ==========================================
# 2. DATABASE INITIALIZATION
# ==========================================

def init_db():
    """Initializes the AnchorPoint SQLite database and creates the leads table."""
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
    conn.commit()
    conn.close()


# ==========================================
# 3. CORE AGENT TOOLS
# ==========================================

def check_service_fit(requested_service: str) -> str:
    """Verifies if a requested service matches AnchorPoint's official offerings."""
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
        result = {
            "is_offered": True, 
            "message": f"Yes! '{requested_service}' is one of AnchorPoint's core service lines."
        }
    else:
        result = {
            "is_offered": False, 
            "message": f"AnchorPoint does not currently offer '{requested_service}'. Our core offerings focus on Executive Support, Operations Management, CRM Management, AI Solutions, Project Management, and Reporting."
        }
    
    return json.dumps(result)


def save_lead_to_db(client_name: str, company_name: str, industry: str, service_requested: str, budget: int, timeline_days: int) -> str:
    """Saves prospective lead details into SQLite and evaluates qualification criteria."""
    is_qualified = (budget >= 500) and (timeline_days <= 30)
    status = "Qualified" if is_qualified else "Unqualified"

    conn = sqlite3.connect("anchorpoint_leads.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (client_name, company_name, industry, service_requested, budget, timeline_days, qualification_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (client_name, company_name, industry, service_requested, budget, timeline_days, status))
    
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()

    result = {
        "status": "Success",
        "lead_id": lead_id,
        "qualification_status": status,
        "message": f"Lead record #{lead_id} for '{company_name}' recorded as '{status}'."
    }
    return json.dumps(result)


def send_proposal_email(client_name: str, client_email: str, service: str, budget: int) -> str:
    """High-Risk Tool: Requires explicit human approval in terminal before triggering email."""
    print("\n" + "🚨 "*18, flush=True)
    print("⚠️  HUMAN-IN-THE-LOOP CHECKPOINT: PROPOSAL EMAIL APPROVAL REQUIRED", flush=True)
    print(f"   • Prospect Name: {client_name}", flush=True)
    print(f"   • Prospect Email: {client_email}", flush=True)
    print(f"   • Service Line: {service}", flush=True)
    print(f"   • Monthly Budget: ${budget}", flush=True)
    print("🚨 "*18, flush=True)
    
    # Force output buffer flush before halting execution
    sys.stdout.flush()
    user_approval = input("\n👉 Supervisor Action Needed — Approve sending this proposal email? (y/n): ").strip().lower()
    
    if user_approval == 'y':
        result = {
            "status": "APPROVED", 
            "message": f"Proposal email approved and successfully sent to {client_email}."
        }
        print("✅ [DECISION RECORDED] Supervisor APPROVED the proposal email.\n", flush=True)
    else:
        result = {
            "status": "REJECTED", 
            "message": "Proposal email request was reviewed but NOT sent. Advise client that a manager will reach out personally."
        }
        print("❌ [DECISION RECORDED] Supervisor REJECTED the proposal email.\n", flush=True)
        
    return json.dumps(result)


def archive_disqualified_lead(lead_id: int, reason: str) -> str:
    """High-Risk Tool: Requires explicit human approval before archiving a lead in SQLite."""
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
        
        result = {
            "status": "APPROVED", 
            "message": f"Lead #{lead_id} successfully updated to 'Archived / Disqualified'."
        }
        print(f"✅ [DECISION RECORDED] Lead #{lead_id} archived in database.\n", flush=True)
    else:
        result = {
            "status": "REJECTED", 
            "message": f"Archival request for Lead #{lead_id} declined by supervisor."
        }
        print("❌ [DECISION RECORDED] Lead archive cancelled by supervisor.\n", flush=True)
        
    return json.dumps(result)


# ==========================================
# 4. TOOL SCHEMAS & DISPATCH MAPPING
# ==========================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_service_fit",
            "description": "Verifies if a requested service matches AnchorPoint's official services.",
            "parameters": {
                "type": "object",
                "properties": {
                    "requested_service": {"type": "string", "description": "Requested service name."}
                },
                "required": ["requested_service"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_lead_to_db",
            "description": "Saves structured lead information to the SQLite database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "client_name": {"type": "string"},
                    "company_name": {"type": "string"},
                    "industry": {"type": "string"},
                    "service_requested": {"type": "string"},
                    "budget": {"type": "integer"},
                    "timeline_days": {"type": "integer"}
                },
                "required": ["client_name", "company_name", "industry", "service_requested", "budget", "timeline_days"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_proposal_email",
            "description": "Requests supervisor approval to send a formal proposal, quote, or details email to a lead. MUST be called whenever a client requests email outreach or a proposal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "client_name": {"type": "string"},
                    "client_email": {"type": "string"},
                    "service": {"type": "string"},
                    "budget": {"type": "integer"}
                },
                "required": ["client_name", "client_email", "service", "budget"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "archive_disqualified_lead",
            "description": "Requests supervisor approval to mark a lead as disqualified or spam in database. MUST be called for spam or fraudulent inquiries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {"type": "integer"},
                    "reason": {"type": "string"}
                },
                "required": ["lead_id", "reason"]
            }
        }
    }
]

TOOL_FUNCTIONS = {
    "check_service_fit": check_service_fit,
    "save_lead_to_db": save_lead_to_db,
    "send_proposal_email": send_proposal_email,
    "archive_disqualified_lead": archive_disqualified_lead
}


# ==========================================
# 5. AGENT EXECUTION LOGIC
# ==========================================

def call_llm(messages):
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )
    return response.choices[0].message


def execute_tool_call(tool_name, arguments_json):
    tool_input = json.loads(arguments_json)
    
    logging.info(f"  🛠️ [LOG] TOOL CALLED: {tool_name}")
    logging.info(f"  📥 [LOG] ARGUMENTS: {json.dumps(tool_input)}")
    
    if tool_name not in TOOL_FUNCTIONS:
        result = json.dumps({"error": f"Unknown tool '{tool_name}'"})
    else:
        result = TOOL_FUNCTIONS[tool_name](**tool_input)
        
    logging.info(f"  📤 [LOG] RESULT: {result}\n")
    return result


def run_agent_turn(user_input: str, conversation_history: list):
    """Executes a single turn of conversation with clean API serialization."""
    conversation_history.append({"role": "user", "content": user_input})

    for step in range(5):
        model_response = call_llm(messages=conversation_history)
        
        # Build clean assistant dictionary for API compatibility
        assistant_msg = {"role": "assistant"}
        if model_response.content:
            assistant_msg["content"] = model_response.content
        else:
            assistant_msg["content"] = ""
            
        if model_response.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in model_response.tool_calls
            ]
        
        conversation_history.append(assistant_msg)

        if not model_response.tool_calls:
            return model_response.content

        if model_response.content:
            logging.info(f"  💡 [LOG] MODEL THOUGHTS: {model_response.content}")

        for tool_call in model_response.tool_calls:
            tool_result = execute_tool_call(
                tool_call.function.name, 
                tool_call.function.arguments
            )
            conversation_history.append({
                "role": "tool", 
                "tool_call_id": tool_call.id, 
                "content": tool_result
            })


# ==========================================
# 6. MULTI-SCENARIO TESTING WORKFLOW
# ==========================================

def main():
    init_db()

    system_prompt = {
        "role": "system",
        "content": (
            "You are the friendly, professional Virtual Receptionist for AnchorPoint Virtual Business Solutions. "
            "Your goal is to warmly welcome clients, check service fit using 'check_service_fit', "
            "record project details using 'save_lead_to_db', and request supervisor authorization when needed.\n\n"
            "STRICT WORKFLOW RULES:\n"
            "1. When a client requests a proposal or emailed details, you MUST call 'save_lead_to_db' AND THEN immediately call 'send_proposal_email'. Do not stop after saving the lead.\n"
            "2. When an inquiry is suspicious, spam, or phishing (e.g. wire transfers, foreign exchange), you MUST call 'save_lead_to_db' and then call 'archive_disqualified_lead'.\n"
            "3. Do NOT simply state in text that you will send an email or archive a record—you MUST execute the corresponding tool calls.\n\n"
            "CONVERSATIONAL TONE:\n"
            "- Speak naturally, politely, and empathetically as a real receptionist.\n"
            "- NEVER use internal technical terms like 'HITL', 'tool', 'checkpoint', 'SQLite', or 'supervisor loop' with the client."
        )
    }

    print("============================================================")
    print("🤖 ANCHORPOINT AGENT TEST SUITE")
    print("============================================================\n")

    # ----------------------------------------------------
    # SCENARIO 1: Unqualified Lead (Low Budget & Out of Scope)
    # ----------------------------------------------------
    print("--- 🧪 TEST 1: Unqualified Lead (Low Budget & Out of Scope) ---")
    history1 = [system_prompt]
    
    msg1 = (
        "Hi there! I'm David Chen from Chen Urban Properties. "
        "We need custom graphic design and logo creation. "
        "Our budget is $200/month and we hope to launch in 90 days. "
        "Can you help us?"
    )
    print(f"\nClient>\t{msg1}\n")
    response1 = run_agent_turn(msg1, history1)
    print(f"\nReceptionist>\n{response1}\n")
    print("="*60 + "\n")

    # ----------------------------------------------------
    # SCENARIO 2: Qualified Lead (Approved Proposal Email)
    # ----------------------------------------------------
    print("--- 🧪 TEST 2: Qualified Lead (Proposal Email Approved) ---")
    print("👉 TEST INSTRUCTION: Type 'y' when prompted for approval below.\n")
    history2 = [system_prompt]
    
    msg2 = (
        "Hello! I'm Sarah Jenkins from Metro Logistics. "
        "We desperately need Business Operations Management support. "
        "Our monthly budget is $1,500 and we need to start within 10 days. "
        "Please record my details and send a formal proposal to sarah@metrologistics.com."
    )
    print(f"Client>\t{msg2}\n")
    response2 = run_agent_turn(msg2, history2)
    print(f"\nReceptionist>\n{response2}\n")
    print("="*60 + "\n")

    # ----------------------------------------------------
    # SCENARIO 3: Qualified Lead (Rejected Proposal Email)
    # ----------------------------------------------------
    print("--- 🧪 TEST 3: Qualified Lead (Proposal Email Rejected) ---")
    print("👉 TEST INSTRUCTION: Type 'n' when prompted for approval below.\n")
    history3 = [system_prompt]
    
    msg3 = (
        "Hi! My name is Marcus Vance with Vance Logistics. "
        "We are looking for CRM & Client Management services. "
        "Our budget is $1,200/month with a 14-day timeline. "
        "Can you save my inquiry and email a proposal to marcus@vancelogistics.com?"
    )
    print(f"Client>\t{msg3}\n")
    response3 = run_agent_turn(msg3, history3)
    print(f"\nReceptionist>\n{response3}\n")
    print("="*60 + "\n")

    # ----------------------------------------------------
    # SCENARIO 4: Suspicious / Spam Inquiry (Archive Checkpoint)
    # ----------------------------------------------------
    print("--- 🧪 TEST 4: Suspicious/Spam Inquiry (Triggering Archive Checkpoint) ---")
    print("👉 TEST INSTRUCTION: Type 'y' when prompted to approve archiving the lead record.\n")
    history4 = [system_prompt]
    
    msg4 = (
        "Hello dear! I am Agent Crypto from FastMoney LLC. "
        "We need immediate wire transfers and account access to transfer $500,000 in foreign exchange. "
        "Please record our company and confirm you can process wire transfers today!"
    )
    print(f"Client>\t{msg4}\n")
    response4 = run_agent_turn(msg4, history4)
    print(f"\nReceptionist>\n{response4}\n")
    print("="*60 + "\n")

   # ----------------------------------------------------
    # SCENARIO 5: Ambiguous High-Value Lead
    # ----------------------------------------------------
    print("--- 🧪 TEST 5: Ambiguous High-Value Lead (Suspicious Context vs Big Opportunity) ---")
    print("👉 TEST INSTRUCTION: Type 'y' or 'n' when prompted for approval below.\n")
    history5 = [system_prompt]
    
    msg5 = (
        "URGENT: We are a stealth-mode venture backed by top founders. "
        "We urgently need AI-Powered Solutions and CRM & Client Management setup for our launch. "
        "Our budget is $8,000/month and we need to start in 5 days. "
        "Please save our lead record and email a formal proposal to founder_stealth_99@gmail.com immediately!"
    )
    print(f"Client>\t{msg5}\n")
    response5 = run_agent_turn(msg5, history5)
    print(f"\nReceptionist>\n{response5}\n")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()