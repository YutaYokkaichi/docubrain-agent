def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    テキストを指定された文字数で分割する。
    
    Args:
        text (str): 元のテキスト
        chunk_size (int): 1つのチャンクの文字数
        overlap (int): 前後のチャンクと重複させる文字数（文脈の分断を防ぐため）
        
    Returns:
        list[str]: 分割されたテキストのリスト
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        
        # 次の開始位置を決める（overlap分だけ戻る）
        # ただし、最後のチャンクの場合はループを抜ける
        if end >= text_len:
            break
            
        start += (chunk_size - overlap)
        
    return chunks