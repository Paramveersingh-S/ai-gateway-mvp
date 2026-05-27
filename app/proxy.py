import time
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import httpx
from loguru import logger

from app.db import get_db
from app.models import ChatCompletionRequest, AuditLog, Policy
from app.agents.coordinator import security_graph
from app.config import settings

router = APIRouter()

async def verify_auth(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or auth != f"Bearer {settings.gateway_api_key}":
        raise HTTPException(status_code=401, detail="Unauthorized gateway access")
    return auth

@router.post("/v1/chat/completions")
async def chat_completions(
    body: ChatCompletionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: str = Depends(verify_auth)
):
    start_time = time.time()
    
    if not body.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty")
    prompt = body.messages[-1].content

    result = await db.execute(select(Policy).where(Policy.is_active == True))
    active_policy = result.scalars().first()
    policy_text = active_policy.content if active_policy else "No active policy."

    try:
        graph_result = await security_graph.ainvoke(
            {"prompt": prompt, "policy_text": policy_text, "agents_results": []}
        )
    except Exception as e:
        logger.error(f"Graph execution failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Security Gateway Error")

    decision = graph_result.get("final_decision", "allow")
    reason = graph_result.get("final_reason", "Passed")
    agents_results = json.dumps(graph_result.get("agents_results", []))
    latency = (time.time() - start_time) * 1000
    client_id = request.client.host if request.client else "unknown"

    upstream_response_text = None
    response_payload = None

    if decision == "block":
        response_payload = {
            "error": {
                "message": f"Blocked by AI Security Gateway: {reason}",
                "type": "security_block",
                "code": "403"
            }
        }
        upstream_response_text = "BLOCKED"
    else:
        # Override the requested model to use our free upstream model
        body.model = settings.upstream_model
        
        # Call Groq's API instead of OpenAI
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {settings.groq_api_key}"}
            try:
                upstream_resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json=body.model_dump(exclude_unset=True),
                    headers=headers,
                    timeout=30.0
                )
                response_payload = upstream_resp.json()
                upstream_response_text = json.dumps(response_payload)[:500]
            except Exception as e:
                logger.error(f"Upstream API error: {e}")
                raise HTTPException(status_code=502, detail="Upstream LLM Error")
                
        if decision == "flag":
            logger.warning(f"Flagged Prompt: {prompt} Reason: {reason}")

    log_entry = AuditLog(
        client_id=client_id,
        prompt=prompt[:1000], 
        response=upstream_response_text,
        decision=decision,
        reason=reason,
        agents_results=agents_results,
        latency_ms=latency
    )
    db.add(log_entry)
    await db.commit()

    if decision == "block":
        return JSONResponse(status_code=403, content=response_payload)
    
    return JSONResponse(status_code=200, content=response_payload)