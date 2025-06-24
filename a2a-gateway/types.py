from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypeAlias

from pydantic import BaseModel, Field

Role: TypeAlias = Literal["memory", "klassist", "tool", "bot"]
Status: TypeAlias = Literal["init", "finish", "error", "terminate"]
Type: TypeAlias = Literal[
    "memory", "thinking", "klassist", "bot", "tool", "final_answer"
]


class UseCount(BaseModel):
    bot: int
    tool: int


class TimeCount(BaseModel):
    bot_time_cost: float
    tool_time_cost: float


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ResponseBody(BaseModel):
    type: str = Field(..., description="type")
    title: Optional[str] = Field(None, description="title")
    text: Optional[str] = Field(None, description="text")
    result: Optional[List[Any]] = Field(None, description="result")
    status: Status = Field("init", description="status")
    card: Optional[Dict[str, Any]] = Field(None, description="card")


class AgentResponse(BaseModel):
    role: Role
    response: ResponseBody
    status: Status
    use_count: Optional[UseCount] = Field(None, description="use_count")
    time_count: Optional[TimeCount] = Field(None, description="time_count")
    usage: Optional[Usage] = Field(None, description="usage")
