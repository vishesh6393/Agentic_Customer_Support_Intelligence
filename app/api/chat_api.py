from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import ToolMessage
from app.agent.agent import build_agent, RISKY_TOOLS

state = {}

@asynccontextmanager
async def lifespan(app):
    state["agent"] = await build_agent()   # start MCP + agent once
    yield

app = FastAPI(title="Support Chat API", lifespan=lifespan)

class ChatIn(BaseModel):
    thread_id: str
    message: str

class ApproveIn(BaseModel):
    thread_id: str
    approve: bool

async def run(cfg, inp):
    agent = state["agent"]
    await agent.ainvoke(inp, cfg)
    while True:
        snap = await agent.aget_state(cfg)
        if not snap.next:                       # finished
            return {"reply": snap.values["messages"][-1].content}
        calls = snap.values["messages"][-1].tool_calls
        if any(c["name"] in RISKY_TOOLS for c in calls):
            return {"pending_approval": calls}  # wait for a human
        await agent.ainvoke(None, cfg)          # safe tool: continue

@app.post("/chat")
async def chat(body: ChatIn):
    cfg = {"configurable": {"thread_id": body.thread_id}}
    return await run(cfg, {"messages": [("user", body.message)]})

@app.post("/approve")
async def approve(body: ApproveIn):
    cfg = {"configurable": {"thread_id": body.thread_id}}
    agent = state["agent"]
    if not body.approve:
        snap = await agent.aget_state(cfg)
        msgs = [ToolMessage(content="Rejected by human reviewer.", tool_call_id=c["id"])
                for c in snap.values["messages"][-1].tool_calls]
        await agent.aupdate_state(cfg, {"messages": msgs}, as_node="tools")
    return await run(cfg, None)