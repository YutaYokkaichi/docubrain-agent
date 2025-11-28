from fastapi import APIRouter, HTTPException
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search import search_relevant_documents

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    RAGの検索パート: 質問に関連するドキュメントを取得する
    """
    try:
        results = await search_relevant_documents(
            query=request.query, 
            limit=request.limit
        )
        return SearchResponse(results=results)
        
    except Exception as e:
        print(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search processing failed")