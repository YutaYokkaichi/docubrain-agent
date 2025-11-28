from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.mcp_client import mcp_client
from app.services.agent_runner import run_agent_chat

router = APIRouter()

class ToolCallRequest(BaseModel):
    name: str
    arguments: dict

class AgentChatRequest(BaseModel):
    message: str

@router.get("/tools")
async def get_tools():
    """利用可能なMCPツール一覧を返す"""
    try:
        tools = await mcp_client.list_tools()
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/call")
async def call_tool(request: ToolCallRequest):
    """指定されたMCPツールを実行する"""
    try:
        result = await mcp_client.call_tool(request.name, request.arguments)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_agent(request: AgentChatRequest):
    """MCPツールを使用できるAIエージェントと会話する"""
    try:
        response = await run_agent_chat(request.message)
        return {"reply": response}
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ [ERROR] Agent chat failed:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")