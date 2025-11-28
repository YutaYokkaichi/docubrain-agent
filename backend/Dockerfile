# ---------------------------------------------------------------------
# Stage 1: Builder Stage
# 目的: Poetryをインストールし、requirements.txt を生成する
# ---------------------------------------------------------------------
# 修正: 'as' は大文字 'AS' が推奨されるため修正（警告対応）
FROM python:3.11-slim AS builder

WORKDIR /tmp

# 修正ポイント: poetry本体に加え、exportプラグインを明示的にインストール
RUN pip install poetry poetry-plugin-export

COPY pyproject.toml poetry.lock ./

# requirements.txt を生成
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# ---------------------------------------------------------------------
# Stage 2: Runner Stage
# 目的: アプリケーションを動かすための最小限の環境を構築する
# ---------------------------------------------------------------------
FROM python:3.11-slim AS runner

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Stage 1 (builder) で生成した requirements.txt をコピー
COPY --from=builder /tmp/requirements.txt .

# 依存関係のインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# コンテナのポートを公開
EXPOSE 8000

# 実行コマンド
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]