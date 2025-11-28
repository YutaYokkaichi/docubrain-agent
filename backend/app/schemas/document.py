# app/schemas/document.py
from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename: str
    content_type: str
    extracted_text_preview: str  # 全文ではなく先頭100文字などを返す想定
    message: str