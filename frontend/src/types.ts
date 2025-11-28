// 検索結果の1件分（引用元）
export interface Source {
    text: string;
    filename: string;
    score: number;
}

// チャットのレスポンス
export interface ChatResponse {
    reply: string;
    sources: Source[];
}

// 画面表示用のメッセージ型
export interface Message {
    role: 'user' | 'assistant';
    content: string;
    sources?: Source[];
}

// チャットセッション（履歴1つ分）
export interface ChatSession {
    id: string;
    title: string;
    messages: Message[];
    createdAt: number;
}