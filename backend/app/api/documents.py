from fastapi import APIRouter, UploadFile, File, HTTPException, status, BackgroundTasks
from app.schemas.document import UploadResponse
from app.services.extractor import extract_text_from_pdf
from app.services.ingestion import process_and_save_document

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    # PDF以外は拒否
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed."
        )

    # テキスト抽出ロジックの呼び出し
    text_content = await extract_text_from_pdf(file)

    if not text_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to extract text from PDF."
        )

    # RAGパイプラインへの投入 (バックグラウンド処理)
    # ユーザーにはすぐにレスポンスを返しつつ、裏でベクトル化・保存を行う
    background_tasks.add_task(
        process_and_save_document, 
        filename=file.filename, 
        text=text_content
    )

    # レスポンス返却
    return UploadResponse(
        filename=file.filename,
        content_type=file.content_type,
        extracted_text_preview=text_content[:100] + "...",
        message="Successfully uploaded. Processing for search in background." # メッセージを少し変更
    )