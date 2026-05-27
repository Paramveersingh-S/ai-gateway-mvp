from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import engine, Base, get_db
from app.proxy import router as proxy_router
from app.models import PolicyCreate, Policy, AuditLog
import logging
import os

app = FastAPI(title="AI Security Gateway MVP", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database initialized.")

app.include_router(proxy_router, tags=["Proxy"])

@app.post("/v1/admin/policies", tags=["Admin"])
async def create_policy(policy: PolicyCreate, db: AsyncSession = Depends(get_db)):
    if policy.is_active:
        await db.execute(Policy.__table__.update().values(is_active=False))
    new_policy = Policy(**policy.model_dump())
    db.add(new_policy)
    await db.commit()
    return {"message": "Policy created successfully"}

@app.get("/v1/admin/policies/active", tags=["Admin"])
async def get_active_policy(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Policy).where(Policy.is_active == True))
    active_policy = result.scalars().first()
    return active_policy if active_policy else {"name": "None", "content": "No active policy."}

@app.get("/v1/admin/logs", tags=["Admin"])
async def get_logs(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
    )
    logs = result.scalars().all()
    return logs

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("static/index.html")