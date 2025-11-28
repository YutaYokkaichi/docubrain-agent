from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.search import search_relevant_documents
from app.services.generation import generate_answer
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_docs(request: ChatRequest):
    """
    RAG完全版: 検索(Retrieve) -> 生成(Generate)
    """
    try:
        # 1. Retrieve: 質問に関連するドキュメントを検索 (Top 5)
        logger.info(f"Searching documents for query: {request.message[:100]}")
        search_results = await search_relevant_documents(query=request.message, limit=5)
        
        if not search_results:
            logger.warning("No documents found for query")
            # 検索結果がない場合でも回答は試みる
        
        # 検索結果からテキスト部分だけをリストにする
        context_texts = [item.text for item in search_results]
        
        # 2. Generate: 検索結果をコンテキストとしてLLMに渡す
        logger.info(f"Generating answer with {len(context_texts)} context documents")
        answer = await generate_answer(query=request.message, context_texts=context_texts)
        
        # 3. Response: 回答と、根拠となったソースを返す
        return ChatResponse(
            reply=answer,
            sources=search_results
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"チャット処理中にエラーが発生しました: {str(e)}"
        )