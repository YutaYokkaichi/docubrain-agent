# app/services/extractor.py
from pypdf import PdfReader
from fastapi import UploadFile
import io

async def extract_text_from_pdf(file: UploadFile) -> str:
    """
    アップロードされたPDFファイルからテキストを抽出する
    """
    try:
        # UploadFileは非同期で読み込む必要があります
        content = await file.read()
        
        # メモリ上のバイナリデータとして扱う
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)
        
        text = ""
        # 全ページのテキストを結合
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        
        # 読み込みカーソルをリセット（後続処理のため）
        await file.seek(0)
        
        return text.strip()
    except Exception as e:
        # 実務ではログ出力推奨
        print(f"Error extracting text: {e}")
        return ""