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
