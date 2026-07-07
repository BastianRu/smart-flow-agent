import time
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.agent import init_building_agent, query_building_agent
from core.session_context import get_tool_trace, reset_session

app = FastAPI(
    title="SmartFlow Demo Agent API v1.0.0",
    version="1.0.0",
    description="Demo Agent API.",
)


class AgentRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    response: str
    tool_trace_length: int
    response_time_seconds: float
    token_usage: dict[str, Any] | None = None


class ResetResponse(BaseModel):
    status: str
    message: str


@app.on_event("startup")
def startup_event():
    init_building_agent()


@app.post("/agent/query", response_model=AgentResponse)
def query_agent(request: AgentRequest):
    try:
        start = time.perf_counter()
        agent_response = query_building_agent(request.message)
        elapsed = time.perf_counter() - start

        usage: dict[str, Any] | None = None
        try:
            summary = agent_response.metrics.get_summary()
            last_usage = summary["agent_invocations"][-1]["usage"]
            usage = last_usage
        except Exception:
            usage = None

        return AgentResponse(
            response=str(agent_response),
            tool_trace_length=len(get_tool_trace()),
            response_time_seconds=elapsed,
            token_usage=usage,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}")


@app.post("/agent/reset", response_model=ResetResponse)
def reset_agent():
    reset_session()
    init_building_agent()
    return ResetResponse(
        status="ok",
        message="Agent session restarted.",
    )


@app.get("/agent/tool-trace")
def tool_trace():
    return {"tool_trace": get_tool_trace(), "length": len(get_tool_trace())}
