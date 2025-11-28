import traceback
import logging
import google.generativeai as genai
from google.generativeai.types import content_types
from collections.abc import Iterable
from app.core.config import settings
from app.services.agent_tools import AGENT_TOOLS, add, multiply, retrieve_knowledge

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# APIキー設定
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

# ツール名と実際の関数を紐付けるマップ
TOOL_MAP = {
    "add": add,
    "multiply": multiply,
    "retrieve_knowledge": retrieve_knowledge
}

# 無限ループ防止のための最大反復回数
MAX_ITERATIONS = 10

async def run_agent_chat(user_message: str) -> str:
    """
    Function Callingを使ってツールを実行しながら回答するエージェント
    複数のツール呼び出しをループで処理します。
    """
    try:
        logger.info(f"🚀 [Agent] Starting chat with message: {user_message[:100]}")
        
        # ツールを登録してモデルを初期化
        logger.info(f"🔧 [Agent] Initializing model with {len(AGENT_TOOLS)} tools")
        
        # 【修正】ユーザー指定の gemini-2.5-flash に変更
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=AGENT_TOOLS
        )
        
        # チャットセッション開始 (手動で関数呼び出しを処理)
        chat = model.start_chat(enable_automatic_function_calling=False)
        logger.info("✅ [Agent] Chat session started")
        
        # 1. ユーザーの入力を送信
        logger.info("📤 [Agent] Sending user message to Gemini...")
        response = await chat.send_message_async(user_message)
        logger.info("📥 [Agent] Received response from Gemini")
        
        # 2. ループ処理: AIが「関数を使いたい」と言っている間は繰り返す
        iteration = 0
        while iteration < MAX_ITERATIONS:
            iteration += 1
            logger.info(f"🔄 [Agent] Iteration {iteration}/{MAX_ITERATIONS}")
            
            # responseの構造を確認
            if not response.candidates:
                logger.warning("⚠️ [Agent] No candidates in response")
                return "すみません、応答を生成できませんでした。"
            
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                logger.warning("⚠️ [Agent] No content parts in response")
                return "すみません、応答を生成できませんでした。"
            
            part = candidate.content.parts[0]
            
            # function_callが含まれているか確認
            if hasattr(part, 'function_call') and part.function_call:
                fc = part.function_call
                tool_name = fc.name
                args = dict(fc.args)  # Mapをdictに変換
                
                logger.info(f"🤖 [Agent] AI wants to call: {tool_name} with args={args}")
                
                # 実際にツールを実行
                if tool_name in TOOL_MAP:
                    try:
                        tool_func = TOOL_MAP[tool_name]
                        logger.info(f"🔧 [Agent] Executing tool: {tool_name}")
                        
                        # 引数を展開して実行
                        tool_result = await tool_func(**args)
                        logger.info(f"✅ [Agent] Tool result: {str(tool_result)[:200]}...")
                        
                        # 3. 結果をAIに送り返す
                        # FunctionResponseを使って結果を構築
                        try:
                            from google.generativeai import protos
                            
                            function_response_part = protos.Part(
                                function_response=protos.FunctionResponse(
                                    name=tool_name,
                                    response={"result": tool_result}
                                )
                            )
                        except ImportError:
                            logger.info("🔄 [Agent] Using alternative FunctionResponse construction")
                            function_response_part = content_types.to_part({
                                "function_response": {
                                    "name": tool_name,
                                    "response": {"result": tool_result}
                                }
                            })
                        
                        # AIに結果を渡して、次の応答を生成させる
                        logger.info("📤 [Agent] Sending tool result back to Gemini...")
                        response = await chat.send_message_async([function_response_part])
                        logger.info("📥 [Agent] Received next response from Gemini")
                        
                        # ループを継続して次の関数呼び出しをチェック
                        continue
                        
                    except Exception as tool_error:
                        error_trace = traceback.format_exc()
                        logger.error(f"❌ [Agent] Tool execution failed:\n{error_trace}")
                        return f"ツール '{tool_name}' の実行中にエラーが発生しました: {str(tool_error)}"
                else:
                    logger.error(f"❌ [Agent] Unknown tool requested: {tool_name}")
                    return f"すみません、ツール '{tool_name}' は利用できません。"
            else:
                # 関数呼び出しがなければ、テキスト応答を返す
                logger.info("💬 [Agent] No function call, returning text response")
                if hasattr(response, 'text'):
                    text_content = response.text
                    if text_content:
                        logger.info(f"✅ [Agent] Final response: {text_content[:100]}...")
                        return text_content
                    else:
                        logger.warning("⚠️ [Agent] Response object has text attribute but it is empty.")
                        return "すみません、空の応答が返されました。"
                else:
                    logger.warning("⚠️ [Agent] No text in response")
                    return "すみません、応答を生成できませんでした。"
        
        # 最大反復回数に達した場合
        logger.warning(f"⚠️ [Agent] Reached max iterations ({MAX_ITERATIONS})")
        if hasattr(response, 'text') and response.text:
            return response.text
        return "処理が複雑すぎるため、完了できませんでした。"

    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"❌ [Agent] Fatal error in run_agent_chat:\n{error_trace}")
        return f"すみません、処理中にエラーが発生しました: {str(e)}"