from pydantic import BaseModel, Field
from app.schemas.search import SearchResultItem

class ChatRequest(BaseModel):
    message: str = Field(..., description="ユーザーからのメッセージ")

class ChatResponse(BaseModel):
    reply: str = Field(..., description="AIからの回答")
    sources: list[SearchResultItem] = Field(..., description="回答の根拠となったドキュメント")