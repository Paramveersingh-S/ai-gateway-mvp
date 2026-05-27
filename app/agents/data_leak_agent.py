from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.models import AgentResult
from app.config import settings
from app.agents.tools import scan_pii_and_secrets
import json

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a data leakage detector. Review the prompt and tool findings. Decide actual risk of exposing PII/secrets. Risk score 0.0 to 1.0."),
    ("human", "Prompt:\n{prompt}\n\nTool Findings:\n{findings}")
])

async def data_leak_agent(prompt_text: str) -> dict:
    findings = scan_pii_and_secrets(prompt_text)
    llm = ChatGroq(model=settings.agent_model, api_key=settings.groq_api_key, temperature=0).with_structured_output(AgentResult)
    chain = prompt | llm
    result = await chain.ainvoke({"prompt": prompt_text, "findings": json.dumps(findings)})
    return {"risk_score": result.risk_score, "explanation": result.explanation}