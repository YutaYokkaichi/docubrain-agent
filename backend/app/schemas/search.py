from pydantic import BaseModel, Field

# 検索リクエスト (ユーザーが送ってくるデータ)
class SearchRequest(BaseModel):
    query: str = Field(..., description="ユーザーの質問")
    limit: int = Field(5, description="取得するドキュメントの数")

# 検索結果の1件分 (AIが見つけたドキュメントの断片)
class SearchResultItem(BaseModel):
    text: str
    filename: str
    score: float # 類似度スコア (0〜1)

# 検索レスポンス全体 (APIが返すデータ)
class SearchResponse(BaseModel):
    results: list[SearchResultItem]