from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from app.api import documents, search, chat
from app.core.config import settings
from app.db.vector_store import init_collection
from app.api import documents, search, chat, agent
from app.services.mcp_client import mcp_client


# ライフサイクルイベント
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時
    try:
        print("🚀 Starting up DocuBrain-Agent...")
        await init_collection("docubrain_collection", vector_size=768)
        print("✅ Connected to Qdrant successfully!")

        try:
            await mcp_client.connect()
        except Exception as e:
            print(f"❌ Failed to connect to MCP Server: {e}")

    except Exception as e:
        print(f"❌ Failed to connect to Qdrant: {e}")
    
    yield
    
    # 終了時
    print("🛑 Shutting down...")
    await mcp_client.close()

app = FastAPI(
    title=settings.PROJECT_NAME, 
    version="0.1.0", 
    lifespan=lifespan
)

# CORS設定 (フロントエンドからのアクセスを許可)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 本番ではドメインを指定すべきですが、一旦全許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(documents.router, prefix="/api", tags=["Documents"])
app.include_router(search.router, prefix="/api", tags=["Search"])
# app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(agent.router, prefix="/api", tags=["Agent"])

@app.get("/health")
def health_check():
    return {"status": "ok", "app_name": settings.PROJECT_NAME}