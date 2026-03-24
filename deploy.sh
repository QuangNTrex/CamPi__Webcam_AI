#!/bin/bash

echo "📥 Pull code..."
cd ~/your-project
git pull

echo "🐍 Update backend..."
cd backend
source venv/bin/activate
pip install -r requirements.txt

echo "♻️ Restart server..."
pkill -f uvicorn

nohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

echo "✅ Done!"