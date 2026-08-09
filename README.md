# ⚓ AnchorPoint Virtual Business Solutions — Lead Qualification Agent

An intelligent, autonomous AI receptionist and lead qualification system designed for **AnchorPoint Virtual Business Solutions**. 

This AI agent greets incoming website visitors, evaluates whether their requested service aligns with AnchorPoint's core offerings, captures lead details, calculates qualification status, and saves records to a local SQLite database. It incorporates **Human-in-the-Loop (HITL)** safeguards for high-risk actions like dispatching automated proposal emails or archiving client records in SQLite.

---

## 🛠️ System Architecture & Features

* **Data Source:** Persistent local SQLite database (`anchorpoint_leads.db`).
* **Handwritten Agent Loop:** Built using a pure Python `while` loop implementing the ReAct framework (*Reason + Act*).
* **DeepSeek API Integration:** Utilizes DeepSeek's OpenAI-compatible API (`deepseek-chat`) for natural language understanding and function calling.
* **Console Logging:** Full transparency of tool calls, arguments passed, and returned results.
* **Human-in-the-Loop (HITL) Checkpoints:** Interactive terminal approval gates requiring explicit supervisor (`y/n`) authorization before executing high-risk tools.
* **Repository Hygiene:** Protected by a `.gitignore` configuration ensuring secret API keys (`.env`), database binaries (`*.db`), virtual environments (`.venv/`), and compiled bytecode (`__pycache__/`) are never committed.

---

## 🧰 Defined Tools & Schemas

1. **`check_service_fit`** *(Safe)*: Compares client service requests against AnchorPoint's 6 core service lines (Executive Support, Business Operations, CRM Management, AI Solutions, Project Management, Reporting & Insights).
2. **`save_lead_to_db`** *(Safe)*: Inserts structured client lead data into SQLite. Automatically classifies leads as `Qualified` or `Unqualified` based on business criteria ($\text{Budget} \ge \$500/\text{month}$ AND $\text{Timeline} \le 30\text{ days}$).
3. **`send_proposal_email`** *(High-Risk / HITL)*: Triggers an internal supervisor approval gate (`y/n`) in the terminal before dispatching an automated proposal email.
4. **`archive_disqualified_lead`** *(High-Risk / HITL)*: Triggers an internal supervisor approval gate (`y/n`) before updating a lead's status to `Archived / Disqualified` in SQLite.

---

## 📋 Prerequisites

* **Python:** 3.10 or higher
* **VS Code** (or preferred IDE / PowerShell terminal)
* **DeepSeek API Key**

---

## 🚀 Environment Setup & Installation Guide

### 1. Clone or Extract Project Folder
Navigate to the project root directory in your terminal:
```bash
cd AnchorPoint_Lead_Qualification_Agent