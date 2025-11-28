import google.generativeai as genai
from app.core.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

# Geminiの設定 (APIキーはすでに設定済みのはず)
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

# 高速で安価なモデルを選択 (gemini-2.5-flash - 最新のFlashモデル)
# Note: 古いライブラリバージョンでは generate_content_async がサポートされていない可能性があるため
# 同期版を asyncio.to_thread でラップします
MODEL_NAME = "gemini-2.5-flash"

def _generate_sync(prompt: str) -> str:
    """
    同期的にGeminiで回答を生成する内部関数
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error during generation: {e}", exc_info=True)
        # APIキーが設定されていない場合のメッセージ
        if "API_KEY" in str(e).upper() or not settings.GEMINI_API_KEY:
            return "エラー: Gemini APIキーが設定されていません。環境変数を確認してください。"
        raise

async def generate_answer(query: str, context_texts: list[str]) -> str:
    """
    検索されたコンテキストを元に、Geminiで回答を生成する
    """
    if not context_texts:
        return "申し訳ありません。関連する情報が見つかりませんでした。"

    # コンテキストを結合してプロンプトに埋め込む
    context_str = "\n\n".join(context_texts)
    
    # システムプロンプトの構築 (ここが回答の質を決めます)
    prompt = f"""
    あなたは優秀なアシスタントです。以下の「参考情報」のみに基づいて、ユーザーの質問に答えてください。
    もし参考情報に答えが含まれていない場合は、「提供された情報からは分かりません」と正直に答えてください。
    
    --- 参考情報 (Context) ---
    {context_str}
    ------------------------
    
    ユーザーの質問: {query}
    """

    try:
        # 同期関数を非同期で実行 (ブロッキングを防ぐ)
        answer = await asyncio.to_thread(_generate_sync, prompt)
        return answer
    except Exception as e:
        logger.error(f"Error in generate_answer: {e}", exc_info=True)
        return f"回答生成中にエラーが発生しました: {str(e)}"