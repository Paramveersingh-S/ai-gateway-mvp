<div align="center">
  <img src="https://img.shields.io/badge/AI_Security-Gateway-0F172A?style=for-the-badge&logo=shield" alt="Logo">
  
  # 🛡️ Enterprise AI Security Gateway
  
  **An ultra-fast, LangGraph-powered proxy to secure LLM inference traffic.**
  <br/>
  Detect Prompt Injections, Prevent Data Leaks, and Dynamically Enforce Business Policies—all before the prompt ever reaches the upstream LLM.

  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain)](https://python.langchain.com/v0.1/docs/langgraph/)
  [![Vue.js](https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D)](https://vuejs.org/)
  [![Groq](https://img.shields.io/badge/Groq_Llama_3.1-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)
  
  [Overview](#-architecture) •
  [Key Features](#-core-capabilities) •
  [Getting Started](#-quick-start) •
  [Admin Dashboard](#-the-dashboard)
</div>

---

## ⚡ The Problem
Deploying Large Language Models (LLMs) in production introduces severe security risks: **Prompt Injections**, **Jailbreaks**, and the accidental leakage of **PII/Secrets**. Relying on the upstream model (like OpenAI or Anthropic) to police itself is a critical security vulnerability.

## 🚀 The Solution
This project implements an **Agentic Hybrid-Proxy Architecture**. By acting as a drop-in replacement for the OpenAI API `v1/chat/completions` endpoint, it sits transparently between your user applications and your LLM provider.

Traffic is first routed through an ultra-low latency **Triage Layer**. Suspicious traffic is then fanned out via a **LangGraph StateGraph** to a swarm of parallel, specialized LLM security agents.

<br/>

## 🧠 Architecture

```mermaid
graph TD
    Client([User Application]) -->|POST /v1/chat/completions| Proxy(FastAPI Gateway)
    Proxy --> Triage{Fast Triage Layer}
    
    Triage -->|Safe| Upstream((Upstream LLM))
    Triage -->|Suspicious| Agents[LangGraph Fan-out]
    
    Agents --> Inject[Prompt Injection Agent]
    Agents --> Leak[Data Leakage & PII Agent]
    Agents --> Policy[Custom Policy Agent]
    
    Inject --> Orch((Orchestrator Agent))
    Leak --> Orch
    Policy --> Orch
    
    Orch -->|ALLOW| Upstream
    Orch -->|BLOCK| Proxy
    
    Upstream --> Proxy
    Proxy -->|Response / 403 Forbidden| Client
🛡️ Core Capabilities
<details open>
<summary><b>1. Concurrent Multi-Agent Swarm (LangGraph)</b></summary>
<br/>
Instead of relying on a single bloated prompt to catch all security issues, the gateway utilizes LangGraph's <code>Send</code> API to map traffic to highly specialized nodes concurrently.
<br/><br/>
</details>
<details open>
<summary><b>2. Zero-Trust Policy Enforcement</b></summary>
<br/>
Administrators can inject natural language business rules (e.g., <i>"Do not provide financial advice"</i> or <i>"Do not discuss competitor products"</i>) dynamically without restarting the server. The <b>Policy Agent</b> verifies compliance in real-time.
<br/><br/>
</details>
<details open>
<summary><b>3. PII & Secret Redaction (Presidio + Regex)</b></summary>
<br/>
The <b>Data Leakage Agent</b> is equipped with tool-calling capabilities. It utilizes Microsoft Presidio and Regex pattern matching to scan payloads for Credit Cards, API Keys, and internal corporate emails before they are transmitted to external APIs.
<br/><br/>
</details>
<details open>
<summary><b>4. Immutable Audit Logging</b></summary>
<br/>
Every request is asynchronously logged to SQLite using SQLAlchemy. Logs include granular latency metrics, the Orchestrator's natural language reasoning for the block, and truncated prompt traces.
<br/><br/>
</details>
💻 Tech Stack
Component	Technology	Description
API Proxy	FastAPI & Uvicorn	High-performance async ASGI server
Orchestration	LangGraph	State-machine based LLM multi-agent framework
Inference Engine	Groq (Llama-3.1)	Sub-second LPU inference for real-time agent execution
Frontend UI	Vue 3 & TailwindCSS	Reactive SPA served directly from the FastAPI backend
Database	SQLite + SQLAlchemy	Async DB operations (aiosqlite)
🛠️ Quick Start
Prerequisites
Python 3.11+
A Free Groq API Key (For Llama 3.1)
1. Clone & Install
code
Bash
git clone https://github.com/YOUR_GITHUB_USERNAME/ai-gateway-mvp.git
cd ai-gateway-mvp

# Install dependencies
pip install -r requirements.txt

# (Optional) Download Spacy model for advanced PII detection
python -m spacy download en_core_web_lg
2. Configure Environment
Create a .env file in the root directory:
code
Env
GATEWAY_API_KEY=my-secret-gateway-key
GROQ_API_KEY=gsk_your_real_groq_key_here
AGENT_MODEL=llama-3.1-8b-instant
UPSTREAM_MODEL=llama-3.1-8b-instant
TRIAGE_MODE=rule
DATABASE_URL=sqlite+aiosqlite:///./gateway.db
LOG_LEVEL=INFO
3. Run the Server
code
Bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
Navigate to http://127.0.0.1:8000 in your browser.
📊 The Dashboard
The project includes a built-in Vue.js SPA frontend to manage and visualize the gateway.
💬 Test Chat: A built-in LLM simulator. Send prompts through the gateway and watch the Security Shield block injections and policy violations in real time.
📈 Live Audit Logs: View total traffic, Security Block Rates, average latency, and the Orchestrator's natural language reasoning for every decision.
📜 Policy Manager: Deploy new enterprise rules instantly without dropping connections.
🌍 Client Integration (Drop-in Replacement)
Because this gateway mimics the OpenAI specification, integrating it into your existing LLM applications requires changing only two lines of code: the base_url and the api_key.
code
Python
from openai import OpenAI

client = OpenAI(
    # Point traffic to your custom AI Gateway
    base_url="http://127.0.0.1:8000/v1", 
    
    # Use the GATEWAY_API_KEY you set in your .env
    api_key="my-secret-gateway-key" 
)

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "What is the capital of France?"}]
)

print(response.choices[0].message.content)
<div align="center">
<i>Built with ❤️ for secure AI deployments.</i>
</div>
```
