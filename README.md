# ⚓ AnchorPoint Virtual Business Solutions — Lead Qualification Agent

An intelligent, multi-step autonomous AI receptionist and lead qualification system engineered for **AnchorPoint Virtual Business Solutions**.

This system acts as a front-facing website receptionist that greets prospective clients, evaluates whether their requested project aligns with AnchorPoint's official core service lines, gathers lead details, evaluates business qualification rules, records structured lead data into a local SQLite database, and executes **Human-in-the-Loop (HITL)** safeguards for high-risk actions.

---

## 📑 Table of Contents
1. [Business Objective & Overview](#-business-objective--overview)
2. [System Architecture & Features](#-system-architecture--features)
3. [Database Schema (`anchorpoint_leads.db`)](#-database-schema-anchorpoint_leadsdb)
4. [Tool Specifications & Schemas](#-tool-specifications--schemas)
5. [Human-in-the-Loop (HITL) Security Matrix](#-human-in-the-loop-hitl-security-matrix)
6. [Complete Environment Setup & Installation Guide](#-complete-environment-setup--installation-guide)
   - [Phase 1: Prerequisites & System Check](#phase-1-prerequisites--system-check)
   - [Phase 2: Project Setup in VS Code](#phase-2-project-setup-in-vs-code)
   - [Phase 3: Create & Activate Virtual Environment (`.venv`)](#phase-3-create--activate-virtual-environment-venv)
   - [Phase 4: Install Dependencies](#phase-4-install-dependencies)
   - [Phase 5: Configure Environment Variables (`.env`)](#phase-5-configure-environment-variables-env)
   - [Phase 6: Select Python Interpreter in VS Code](#phase-6-select-python-interpreter-in-vs-code)
   - [Phase 7: Run the Agent & Database Inspector](#phase-7-run-the-agent--database-inspector)
7. [Troubleshooting & Beginner Tips](#-troubleshooting--beginner-tips)
8. [Multi-Scenario Test Suite Overview](#-multi-scenario-test-suite-overview)
9. [Inspecting Database Records](#-inspecting-database-records)
10. [Repository Security & Git Hygiene](#-repository-security--git-hygiene)

---

## 🏢 Business Objective & Overview

**AnchorPoint Virtual Business Solutions** provides high-level operational and administrative assistance to businesses. To streamline client intake without overwhelming management, this AI agent handles first-contact lead intake.

### Core Objectives:
* **Service Alignment:** Ensure client requests match AnchorPoint's official service lines (e.g., Executive Support, Operations Management, CRM Setup, AI Solutions).
* **Automated Lead Qualification:** Automatically evaluate lead budget and implementation timelines against internal qualification thresholds (Budget >= $500/month AND Timeline <= 30 days).
* **Database Recording:** Store structured prospective lead records in a persistent local SQLite database.
* **Risk Reduction:** Block unauthorized or unvetted email dispatches and database alterations using terminal-based Human-in-the-Loop (HITL) approval checkpoints.

---

## 🛠️ System Architecture & Features

* **Custom ReAct Execution Loop:** Implemented in pure Python using a `while` loop that follows the ReAct framework (*Reason + Act*).
* **LLM Engine:** Powered by DeepSeek's OpenAI-compatible Chat Completions API (`deepseek-chat`).
* **Persistent Data Layer:** Local SQLite database (`anchorpoint_leads.db`).
* **Console Transparency:** Every model thought, tool call, input argument, and return output is printed in real time to the developer console.
* **Dual Persona Architecture:** Internal technical checkpoints remain visible strictly to developers in the console, while client-facing messages maintain a warm, empathetic, and professional tone free of technical jargon.

---

## 📊 Database Schema (`anchorpoint_leads.db`)

The agent automatically creates and interacts with a SQLite database table named `leads`.

### SQL Table Definition:
```sql
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
);
```

### Database Fields:
| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER` | Auto-incrementing primary key reference number. |
| `client_name` | `TEXT` | Full name of prospective client contact. |
| `company_name` | `TEXT` | Business or organization name. |
| `industry` | `TEXT` | Industry or market sector. |
| `service_requested` | `TEXT` | Core service requested by prospect. |
| `budget` | `INTEGER` | Stated monthly budget in USD. |
| `timeline_days` | `INTEGER` | Desired onboarding timeline in days. |
| `qualification_status` | `TEXT` | Evaluated status (`Qualified`, `Unqualified`, or `Archived / Disqualified`). |
| `created_at` | `TIMESTAMP` | Timestamp of lead insertion. |

---

## 🧰 Tool Specifications & Schemas

The agent is equipped with 4 specialized Python functions mapped to OpenAI-compatible JSON tool schemas:

### 1. `check_service_fit` *(Safe / Read-Only)*
* **Purpose:** Verifies whether a client's requested service matches AnchorPoint's official offerings:
  1. Executive & Administrative Support
  2. Business Operations Management
  3. CRM & Client Management
  4. AI-Powered Solutions
  5. Document & Project Management
  6. Reporting & Insights
* **Parameters:** `requested_service` (`string`)

### 2. `save_lead_to_db` *(Safe / Write)*
* **Purpose:** Inserts extracted lead information into SQLite and evaluates qualification status based on business rules:
  `Qualified` = (budget >= 500) AND (timeline_days <= 30)
* **Parameters:** `client_name` (`string`), `company_name` (`string`), `industry` (`string`), `service_requested` (`string`), `budget` (`integer`), `timeline_days` (`integer`)

### 3. `send_proposal_email` *(High-Risk / HITL Gate)*
* **Purpose:** Requests supervisor authorization via interactive terminal prompt before dispatching an automated proposal email.
* **Parameters:** `client_name` (`string`), `client_email` (`string`), `service` (`string`), `budget` (`integer`)

### 4. `archive_disqualified_lead` *(High-Risk / HITL Gate)*
* **Purpose:** Requests supervisor authorization via interactive terminal prompt before marking a record as `Archived / Disqualified` in SQLite.
* **Parameters:** `lead_id` (`integer`), `reason` (`string`)

---

## 🛡️ Human-in-the-Loop (HITL) Security Matrix

| Action | Risk Level | Execution Rule | HITL Safeguard |
| :--- | :--- | :--- | :--- |
| **Check Service Fit** | Low | Autonomous | Allowed automatically without pause. |
| **Save Lead Record** | Low | Autonomous | Allowed automatically; updates local database. |
| **Dispatch Proposal Email** | High | **Interactive Gate** | Halts execution; displays red alert banner in terminal; requires explicit supervisor entry (`y`/`n`). |
| **Archive / Flag Lead** | High | **Interactive Gate** | Halts execution; displays red alert banner in terminal; requires explicit supervisor entry (`y`/`n`). |

---

## 🚀 Complete Environment Setup & Installation Guide

This step-by-step guide is written for anyone completely new to coding! Follow these instructions to set up your environment, configure your API keys, and run the agent on your computer.

---

### 📋 Phase 1: Prerequisites & System Check

Before starting, ensure you have the necessary tools installed on your computer:

1. **Python (Version 3.10 or higher):**
   * Open your terminal or command prompt and check your Python version:
     * **Windows (PowerShell):** `python --version`
     * **Mac / Linux:** `python3 --version`
   * *If Python is not installed or version is below 3.10:* Download it from the official site: [python.org/downloads](https://www.python.org/downloads/). During Windows installation, **check the box that says "Add Python to PATH"**.

2. **Visual Studio Code (VS Code):**
   * Download and install VS Code if you haven't already: [code.visualstudio.com](https://code.visualstudio.com/).

3. **DeepSeek API Key:**
   * Sign up for an API key at [platform.deepseek.com](https://platform.deepseek.com/). You will need this key to power the AI's natural language understanding.

---

### 📂 Phase 2: Project Setup in VS Code

1. **Download the Project Files:**
   * Download or unzip the project folder (`AnchorPoint_Lead_Qualification_Agent`) to a location on your computer (e.g., your Desktop or Documents folder).

2. **Open the Project in VS Code:**
   * Open VS Code.
   * Click **File > Open Folder...** (or `Ctrl + O` / `Cmd + O`) and select the `AnchorPoint_Lead_Qualification_Agent` folder.

3. **Open the Built-in Terminal:**
   * In VS Code, open the integrated terminal by pressing ``Ctrl + ` `` (or clicking **Terminal > New Terminal** in the top menu).

---

### 📦 Phase 3: Create & Activate a Virtual Environment (`.venv`)

A **Virtual Environment** is a private, isolated container for your project. It ensures that software libraries installed for this project do not interfere with other Python projects on your computer.

1. **Create the Virtual Environment:**
   Run this command in your VS Code terminal:
   * **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     ```
   * **Mac / Linux:**
     ```bash
     python3 -m venv .venv
     ```

2. **Activate the Virtual Environment:**
   * **Windows (PowerShell):**
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
     *(If PowerShell gives an Execution Policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and try activating again).*
   * **Mac / Linux:**
     ```bash
     source .venv/bin/activate
     ```

3. **Verify Activation:**
   Look at the far left side of your terminal command prompt. You should now see **`(.venv)`** highlighted at the beginning of the line:
   ```powershell
   (.venv) PS C:\Users\YourName\AnchorPoint_Lead_Qualification_Agent>
   ```

---

### 🛠️ Phase 4: Install Dependencies

Now that your virtual environment is active, install the required third-party Python packages using `pip` (Python's package manager):

```bash
pip install openai python-dotenv
```

* **`openai`**: Allows Python to communicate with DeepSeek's OpenAI-compatible API.
* **`python-dotenv`**: Automatically loads secret keys from your `.env` file into Python memory.

---

### 🔑 Phase 5: Configure Environment Variables (`.env`)

To protect your secret API key, project credentials are kept in a local file named `.env` that is never uploaded to public code repositories.

1. **Create Your Local `.env` File:**
   * Look at the `.env.example` file in VS Code for reference.
   * Create a brand-new file in the root folder of VS Code named **`.env`** *(make sure it starts with a dot and has no extension!)*.

2. **Add Your API Key:**
   * Open your new `.env` file and add this single line, replacing `your_actual_api_key_here` with your real DeepSeek API key:
     ```env
     DEEPSEEK_API_KEY=your_actual_api_key_here
     ```
   * **Important:** Do *not* put quotation marks around your key or leave spaces around the `=` sign!
3. Save the file (`Ctrl + S` or `Cmd + S`).

---

### 🐍 Phase 6: Select Python Interpreter in VS Code

To make sure VS Code's editor recognizes installed packages and removes red/yellow squiggly lines:

1. Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on Mac) to open the Command Palette.
2. Type **`Python: Select Interpreter`** and press **Enter**.
3. Choose the option that points to your virtual environment: **`(.venv): ./.venv/Scripts/python.exe`** (or `bin/python` on Mac).

---

### 🧪 Phase 7: Run the Agent & Database Inspector

You are ready to run the application!

1. **Run the Main Agent Workflow:**
   In your active terminal, run:
   ```bash
   python anchorpoint_agent.py
   ```
   * *Interactive Prompts:* During Scenarios 2, 3, 4, and 5, execution will pause for your **Human-in-the-Loop (HITL)** input. Follow the instructions on screen by typing `y` (Approve) or `n` (Reject) and pressing **Enter**.

2. **Inspect the Local SQLite Database:**
   To verify that lead records were successfully inserted and categorized in SQLite during the run, execute:
   ```bash
   python check_db.py
   ```

---

## ❓ Troubleshooting & Beginner Tips

* **Issue: `ModuleNotFoundError: No module named 'openai'`**
  * *Fix:* Make sure your virtual environment is active (look for `(.venv)` in your terminal prompt) before running the script. If not active, re-run the activation command from Phase 3.
* **Issue: `AuthenticationError` or Invalid API Key**
  * *Fix:* Check your `.env` file. Ensure there are no trailing spaces or missing characters in your `DEEPSEEK_API_KEY` value.
* **Issue: Terminal input doesn't trigger during test loop**
  * *Fix:* Ensure you are clicking directly inside the PowerShell panel in VS Code before typing `y` or `n`.
* **Issue: Database looks out of sync**
  * *Fix:* If you ever want to reset your database test environment, simply delete the `anchorpoint_leads.db` file in VS Code. The script will automatically recreate a fresh database the next time you run `python anchorpoint_agent.py`!

---

## ⚙️ Multi-Scenario Test Suite Overview

Running `python anchorpoint_agent.py` automatically executes 5 specialized test scenarios designed to validate every path through the ReAct loop:

### 🧪 Scenario 1 — Unqualified Lead (David Chen)
* **Inquiry:** Requests Graphic Design (out-of-scope) with a $200 budget and 90-day timeline.
* **Execution Flow:** Agent calls `check_service_fit` (returns `is_offered: false`) and `save_lead_to_db` (returns `Unqualified`).
* **Outcome:** Record stored as `Unqualified` in SQLite. Receptionist politely explains AnchorPoint's official core offerings without making high-risk tool calls.

### 🧪 Scenario 2 — Qualified Lead with Approved Proposal (Sarah Jenkins)
* **Inquiry:** Requests Business Operations Support ($1,500 budget, 10-day timeline) and asks for a proposal email sent to `sarah@metrologistics.com`.
* **Execution Flow:** Agent validates fit, records lead as `Qualified`, and invokes `send_proposal_email`.
* **HITL Action:** Pause triggered! Type **`y`** in the terminal.
* **Outcome:** Proposal email dispatch logged as `APPROVED`. Agent delivers a warm confirmation to the client.

### 🧪 Scenario 3 — Qualified Lead with Rejected Proposal (Marcus Vance)
* **Inquiry:** Requests CRM Management ($1,200 budget, 14-day timeline) and asks for a proposal email sent to `marcus@vancelogistics.com`.
* **Execution Flow:** Agent records lead as `Qualified` and requests email authorization.
* **HITL Action:** Pause triggered! Type **`n`** in the terminal.
* **Outcome:** Supervisor blocks proposal dispatch. The receptionist gracefully informs the client that their request was saved and a team member will reach out personally—without revealing internal system jargon.

### 🧪 Scenario 4 — Suspicious / Spam Inquiry (Agent Crypto / FastMoney LLC)
* **Inquiry:** Requests immediate $500,000 foreign exchange wire transfers.
* **Execution Flow:** Agent identifies out-of-scope/fraudulent inquiry, records the entry, and invokes `archive_disqualified_lead`.
* **HITL Action:** Pause triggered! Type **`y`** to approve archiving.
* **Outcome:** Database record status updated to `Archived / Disqualified` in SQLite.

### 🧪 Scenario 5 — Ambiguous High-Value Edge Case (Stealth Venture Founder)
* **Inquiry:** Urgent AI & CRM setup request with a massive $8,000/month budget and 5-day timeline, but submitted via `founder_stealth_99@gmail.com`.
* **Execution Flow:** Agent balances high budget against unverified contact credentials, saves the lead as `Qualified`, and forces the `send_proposal_email` HITL checkpoint.
* **HITL Action:** Pause triggered! Type **`y`** or **`n`** to demonstrate supervisor oversight on edge-case revenue opportunities.

---

## 📊 Inspecting Database Records

To view all records created during testing, run the custom inspection script:

```bash
python check_db.py
```

### Example Console Output from `check_db.py`:
```text
============================================================
📊 ANCHORPOINT DATABASE RECORDS:
============================================================
ID: 1 | Name: David Chen | Company: Chen Urban Properties | Industry: Real Estate
    Service: Graphic Design | Budget: $200 | Timeline: 90 days | Status: Unqualified
------------------------------------------------------------
ID: 2 | Name: Sarah Jenkins | Company: Metro Logistics | Industry: Logistics
    Service: Business Operations Management | Budget: $1500 | Timeline: 10 days | Status: Qualified
------------------------------------------------------------
ID: 3 | Name: Marcus Vance | Company: Vance Logistics | Industry: Logistics
    Service: CRM & Client Management | Budget: $1200 | Timeline: 14 days | Status: Qualified
------------------------------------------------------------
ID: 4 | Name: Agent Crypto | Company: FastMoney LLC | Industry: Finance
    Service: Wire Transfers | Budget: $500000 | Timeline: 1 days | Status: Archived / Disqualified
------------------------------------------------------------
ID: 5 | Name: Founder | Company: Stealth Venture | Industry: Technology
    Service: AI Solutions & CRM | Budget: $8000 | Timeline: 5 days | Status: Qualified
------------------------------------------------------------
```

*(Alternatively, open `anchorpoint_leads.db` visually using the **SQLite Viewer** extension in VS Code).*

---

## 🔒 Repository Security & Git Hygiene

This repository enforces strict security and version control hygiene:

1. **Secret Key Isolation:** All API credentials are stored exclusively in `.env` (ignored by Git).
2. **Template Provisioning:** A public `.env.example` file is included to demonstrate configuration requirements without leaking secrets.
3. **Ignored Runtime Artifacts:** Local database binaries (`*.db`), virtual environments (`.venv/`), and compiled bytecode (`__pycache__/`) are excluded via `.gitignore`.

### Included `.gitignore` Rules:
```gitignore
# Environment variables & Secret API Keys
.env

# Virtual Environment
.venv/
venv/

# Database Files
*.db
*.sqlite3

# Python Bytecode Caches
__pycache__/
*.pyc

# VS Code Folder
.vscode/
```
