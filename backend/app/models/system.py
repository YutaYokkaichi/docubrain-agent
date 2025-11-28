from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    """
    ヘルスチェック用レスポンスモデル
    """
    status: str = Field(..., description="APIの稼働状況 (例: ok)")
    version: str = Field(..., description="APIのバージョン")
    environment: str = Field("local", description="現在の実行環境")