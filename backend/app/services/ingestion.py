import uuid
from qdrant_client.http import models
from app.db.vector_store import get_qdrant_client
from app.services.embeddings import get_embedding
from app.services.chunking import split_text

COLLECTION_NAME = "docubrain_collection"

async def process_and_save_document(filename: str, text: str):
    client = get_qdrant_client()
    
    # ... (チャンク分割処理はそのまま) ...
    chunks = split_text(text) # ここは同期関数のままでOK
    print(f"Processing {len(chunks)} chunks for {filename}...")

    points = []
    # ... (forループ内のベクトル化処理はそのまま) ...
    for i, chunk_text in enumerate(chunks):
        embedding = await get_embedding(chunk_text)
        point = models.PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "filename": filename,
                "text": chunk_text,
                "chunk_index": i
            }
        )
        points.append(point)

    # 【変更点】 upsert に await をつける
    if points:
        await client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print(f"Successfully saved {len(points)} chunks to Qdrant.")
    
    return len(points)