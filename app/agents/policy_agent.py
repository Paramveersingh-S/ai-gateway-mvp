from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.models import AgentResult
from app.config import settings

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a compliance agent. Check if the prompt violates the active policy. Risk score 0.0 (safe) to 1.0 (violation).\n\nPOLICY:\n{policy}"),
    ("human", "{prompt}")
])

async def policy_agent(prompt_text: str, policy_text: str) -> dict:
    if not policy_text or policy_text == "No active policy.":
        return {"risk_score": 0.0, "explanation": "No policy to enforce."}
    llm = ChatGroq(model=settings.agent_model, api_key=settings.groq_api_key, temperature=0).with_structured_output(AgentResult)
    chain = prompt | llm
    result = await chain.ainvoke({"prompt": prompt_text, "policy": policy_text})
    return {"risk_score": result.risk_score, "explanation": result.explanation}