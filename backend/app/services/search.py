import qdrant_client
from app.db.vector_store import get_qdrant_client
from app.services.embeddings import get_embedding
from app.schemas.search import SearchResultItem

COLLECTION_NAME = "docubrain_collection"

async def search_relevant_documents(query: str, limit: int = 5) -> list[SearchResultItem]:
    """
    クエリに関連するドキュメントを検索
    
    Args:
        query: 検索クエリ文字列
        limit: 取得する結果の最大数
        
    Returns:
        SearchResultItemのリスト
        
    Raises:
        Exception: Qdrant検索または埋め込み生成時のエラー
    """
    client = get_qdrant_client()
    
    # 1. クエリをベクトル化
    query_vector = await get_embedding(query)
    
    # 2. Qdrantで類似検索を実行 (AsyncQdrantClient は query_points を使用)
    response = await client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True
    )
    
    # 3. 結果整形
    results = [
        SearchResultItem(
            text=hit.payload.get("text", ""),
            filename=hit.payload.get("filename", "unknown"),
            score=hit.score
        )
        for hit in response.points
    ]
    
    return results