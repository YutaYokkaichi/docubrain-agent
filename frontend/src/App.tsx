import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, FileText, Loader2, PlusCircle, MessageSquare, Trash2, Menu } from 'lucide-react';
import { sendMessage } from './api';
import type { ChatSession } from './types'; // types.ts からインポート

function App() {
  // === State Management ===
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true); // モバイル用メニュー開閉

  // 自動スクロール用
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // === 初期化 & LocalStorage ===
  useEffect(() => {
    // 起動時にLocalStorageから履歴を読み込む
    const saved = localStorage.getItem('docubrain_sessions');
    if (saved) {
      try {
        const parsedSessions: ChatSession[] = JSON.parse(saved);
        setSessions(parsedSessions);
        if (parsedSessions.length > 0) {
          // 最新の会話（リストの先頭）を開く
          setCurrentSessionId(parsedSessions[0].id);
        } else {
          createNewSession();
        }
      } catch (e) {
        console.error("Failed to parse sessions", e);
        createNewSession();
      }
    } else {
      createNewSession();
    }
  }, []);

  // セッションが更新されたらLocalStorageに保存
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem('docubrain_sessions', JSON.stringify(sessions));
    }
  }, [sessions]);

  // メッセージ追加時やセッション切り替え時にスクロール
  useEffect(() => {
    scrollToBottom();
  }, [sessions, currentSessionId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // === アクション ===

  // 新しいチャットを開始
  const createNewSession = () => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: '新しいチャット',
      messages: [{ role: 'assistant', content: 'こんにちは！私はDocuBrain Agentです。ドキュメントについて何でも聞いてください。' }],
      createdAt: Date.now(),
    };
    // 新しいセッションを先頭に追加
    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);

    // モバイルならサイドバーを閉じる
    if (window.innerWidth < 768) setIsSidebarOpen(false);
  };

  // チャット削除
  const deleteSession = (e: React.MouseEvent, id: string) => {
    e.stopPropagation(); // 親のonClickを発火させない

    const newSessions = sessions.filter(s => s.id !== id);
    setSessions(newSessions);
    localStorage.setItem('docubrain_sessions', JSON.stringify(newSessions));

    // 削除したのが現在開いているセッションなら、別のセッションを開くか新規作成
    if (id === currentSessionId) {
      if (newSessions.length > 0) {
        setCurrentSessionId(newSessions[0].id);
      } else {
        createNewSession();
      }
    }
  };

  // 送信処理
  const handleSend = async () => {
    if (!input.trim() || isLoading || !currentSessionId) return;

    const userText = input;
    setInput('');
    setIsLoading(true);

    // 1. ユーザーメッセージを追加 & タイトル更新（初回のみ）
    setSessions(prev => prev.map(session => {
      if (session.id === currentSessionId) {
        // 最初の質問をタイトルにする
        const isFirstUserMessage = session.messages.length === 1;
        const newTitle = isFirstUserMessage
          ? (userText.length > 15 ? userText.slice(0, 15) + '...' : userText)
          : session.title;

        return {
          ...session,
          title: newTitle,
          messages: [...session.messages, { role: 'user', content: userText }]
        };
      }
      return session;
    }));

    try {
      // 2. APIコール
      const response = await sendMessage(userText);

      // 3. AI応答を追加
      setSessions(prev => prev.map(session => {
        if (session.id === currentSessionId) {
          return {
            ...session,
            messages: [...session.messages, {
              role: 'assistant',
              content: response.reply,
              sources: response.sources
            }]
          };
        }
        return session;
      }));

    } catch (error) {
      console.error(error);
      setSessions(prev => prev.map(session => {
        if (session.id === currentSessionId) {
          return {
            ...session,
            messages: [...session.messages, { role: 'assistant', content: '申し訳ありません。エラーが発生しました。もう一度お試しください。' }]
          };
        }
        return session;
      }));
    } finally {
      setIsLoading(false);
    }
  };

  // Enterキー制御 (IME変換中は送信しない)
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.nativeEvent.isComposing) return;
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 現在表示中のメッセージリスト取得
  const currentSession = sessions.find(s => s.id === currentSessionId);
  const currentMessages = currentSession?.messages || [];

  return (
    <div className="flex h-screen bg-gray-100 font-sans overflow-hidden">

      {/* Sidebar (履歴リスト) */}
      <aside className={`
        fixed inset-y-0 left-0 z-20 w-64 bg-gray-900 text-gray-100 transform transition-transform duration-200 ease-in-out
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        md:relative md:translate-x-0 flex flex-col border-r border-gray-800
      `}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-800 flex justify-between items-center">
          <h2 className="font-bold text-lg flex items-center tracking-tight">
            <Bot className="w-5 h-5 mr-2 text-blue-400" /> DocuBrain
          </h2>
          <button onClick={() => setIsSidebarOpen(false)} className="md:hidden p-1 hover:bg-gray-800 rounded">
            <Menu className="w-5 h-5" />
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-4">
          <button
            onClick={createNewSession}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg transition-all shadow-md active:scale-95 font-medium"
          >
            <PlusCircle className="w-5 h-5" /> 新しいチャット
          </button>
        </div>

        {/* Session List */}
        <div className="flex-1 overflow-y-auto px-2 space-y-1 pb-4 scrollbar-thin scrollbar-thumb-gray-700">
          {sessions.map(session => (
            <div
              key={session.id}
              onClick={() => {
                setCurrentSessionId(session.id);
                if (window.innerWidth < 768) setIsSidebarOpen(false);
              }}
              className={`
                group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all duration-200
                ${currentSessionId === session.id
                  ? 'bg-gray-800 text-white border-l-4 border-blue-500 shadow-sm'
                  : 'hover:bg-gray-800/50 text-gray-400 hover:text-gray-200 border-l-4 border-transparent'}
              `}
            >
              <div className="flex items-center gap-3 overflow-hidden flex-1">
                <MessageSquare className={`w-4 h-4 flex-shrink-0 ${currentSessionId === session.id ? 'text-blue-400' : 'text-gray-500'}`} />
                <span className="truncate text-sm font-medium">{session.title}</span>
              </div>
              <button
                onClick={(e) => deleteSession(e, session.id)}
                className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-500/20 hover:text-red-400 rounded transition-all"
                title="削除"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Content (チャットエリア) */}
      <div className="flex-1 flex flex-col h-full w-full bg-white relative">

        {/* Mobile Header (ハンバーガーメニュー) */}
        <header className="md:hidden bg-white border-b p-4 flex items-center z-10 shadow-sm">
          <button onClick={() => setIsSidebarOpen(true)} className="mr-4 p-2 -ml-2 hover:bg-gray-100 rounded-lg">
            <Menu className="w-6 h-6 text-gray-600" />
          </button>
          <span className="font-bold text-gray-800 flex items-center">
            <Bot className="w-5 h-5 mr-2 text-blue-600" /> DocuBrain Agent
          </span>
        </header>

        {/* Chat Messages Area */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-gray-50/50">
          <div className="max-w-3xl mx-auto space-y-6 pb-4">
            {currentMessages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex max-w-[90%] md:max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>

                  {/* Icon */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mx-2 shadow-sm mt-1
                    ${msg.role === 'user' ? 'bg-blue-600' : 'bg-green-600'}`}>
                    {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
                  </div>

                  {/* Message Body */}
                  <div className={`p-4 rounded-2xl shadow-sm whitespace-pre-wrap leading-relaxed text-sm md:text-base
                    ${msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-tr-none'
                      : 'bg-white text-gray-800 rounded-tl-none border border-gray-200'}`}>
                    {msg.content}

                    {/* Sources Display */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-gray-100 text-xs md:text-sm">
                        <p className="font-semibold text-gray-500 mb-2 flex items-center">
                          <FileText className="w-4 h-4 mr-1" /> 参考ドキュメント:
                        </p>
                        <ul className="space-y-2">
                          {msg.sources.map((src, i) => (
                            <li key={i} className="bg-gray-50 p-3 rounded-lg border border-gray-100 text-gray-600 hover:bg-gray-100 transition-colors">
                              <span className="font-bold text-blue-600 block mb-1 flex items-center">
                                <span className="truncate flex-1">{src.filename}</span>
                                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full ml-2">
                                  {(src.score * 100).toFixed(0)}% match
                                </span>
                              </span>
                              <p className="line-clamp-2 text-xs opacity-80">{src.text}</p>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Loading State */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white p-4 rounded-2xl rounded-tl-none border border-gray-200 ml-12 shadow-sm flex items-center gap-2 text-gray-500 text-sm">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                  AIが考え中...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </main>

        {/* Input Area */}
        <footer className="bg-white border-t p-4 pb-6 md:pb-6">
          <div className="max-w-3xl mx-auto flex gap-2">
            <input
              type="text"
              className="flex-1 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50 transition-all placeholder-gray-400"
              placeholder="質問を入力してください... (Shift+Enterで改行)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="bg-blue-600 text-white px-5 py-3 rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm flex items-center justify-center active:scale-95"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;