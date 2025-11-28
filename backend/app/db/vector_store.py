import qdrant_client
from qdrant_client import AsyncQdrantClient, models # 変更
from app.core.config import settings

# グローバル変数
_client = None

def get_qdrant_client() -> AsyncQdrantClient: # 型定義変更
    """
    Qdrantの非同期クライアントを返す (Singleton)
    """
    global _client
    if _client is None:
        _client = AsyncQdrantClient( # ここをAsyncに変更
            url=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            api_key=settings.QDRANT_API_KEY
        )
    return _client

async def init_collection(collection_name: str, vector_size: int = 768): # asyncをつける
    """
    コレクションの初期化 (非同期版)
    """
    client = get_qdrant_client()
    
    # 非同期メソッドなので await が必要
    if not await client.collection_exists(collection_name):
        await client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )
        print(f"Collection '{collection_name}' created.")