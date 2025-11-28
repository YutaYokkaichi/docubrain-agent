import google.generativeai as genai
from app.core.config import settings

# 初期設定: APIキーを読み込む
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

async def get_embedding(text: str) -> list[float]:
    """
    Gemini API (text-embedding-004) を使用してテキストをベクトル化する。
    
    Args:
        text (str): ベクトル化したいテキスト
        
    Returns:
        list[float]: 768次元のベクトルリスト
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")

    try:
        # 改行コードは埋め込み精度に悪影響を与えることがあるため置換するのが定石です
        clean_text = text.replace("\n", " ")
        
        # 実務ポイント: 最新モデルを指定します
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=clean_text,
            task_type="retrieval_document" # 用途を指定（検索用ドキュメント）
        )
        
        return result['embedding']
        
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # リトライ処理などを入れる場所ですが、まずはエラーを送出
        raise e