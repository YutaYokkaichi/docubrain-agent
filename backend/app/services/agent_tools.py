from app.services.mcp_client import mcp_client
from app.services.search import search_relevant_documents

# === 既存の計算ツール (現状維持) ===
async def add(a: int, b: int) -> int:
    """2つの整数を足し算します。"""
    try:
        print(f"🔧 [Tool] Calling add({a}, {b})")
        result = await mcp_client.call_tool("add", {"a": a, "b": b})
        
        # MCPの結果解析
        for content in result:
            if hasattr(content, 'type') and content.type == "text":
                return int(content.text)
        return int(str(result)) # Fallback
    except Exception as e:
        print(f"❌ [Tool Error] add failed: {e}")
        return 0

async def multiply(a: int, b: int) -> int:
    """2つの整数を掛け算します。"""
    try:
        print(f"🔧 [Tool] Calling multiply({a}, {b})")
        result = await mcp_client.call_tool("multiply", {"a": a, "b": b})
        
        for content in result:
            if hasattr(content, 'type') and content.type == "text":
                return int(content.text)
        return int(str(result))
    except Exception as e:
        print(f"❌ [Tool Error] multiply failed: {e}")
        return 0

# === 【追加】検索ツール (ここが新機能！) ===
async def retrieve_knowledge(query: str) -> str:
    """
    社内ドキュメント（履歴書や職務経歴書など）を検索して情報を取得します。
    ユーザーから候補者のスキル、経歴、経験などに関する質問があった場合にこのツールを使用してください。
    
    Args:
        query: 検索したいキーワードや質問文
    """
    print(f"🔍 [Agent Tool] Searching for knowledge: {query}")
    
    try:
        # 既存のRAG検索を実行 (Top 5)
        results = await search_relevant_documents(query=query, limit=5)
        
        if not results:
            return "関連する情報は見つかりませんでした。"
        
        # 検索結果をLLMが読みやすいテキストに整形
        context_text = "\n\n".join(
            [f"[Source: {r.filename}]\n{r.text}" for r in results]
        )
        return context_text
    except Exception as e:
        print(f"❌ [Tool Error] search failed: {e}")
        return "検索中にエラーが発生しました。"

# === ツール登録 ===
# ここに retrieve_knowledge を追加することで、Geminiが「この機能があるんだ」と認識します
AGENT_TOOLS = [add, multiply, retrieve_knowledge]