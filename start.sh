#!/bin/bash
set -e

# Render injects PORT automatically — do NOT set PORT manually in env vars
export PORT=${PORT:-8080}
echo "==> Using PORT: $PORT"

# Update nginx to listen on the correct port
sed -i "s/listen 8080;/listen $PORT;/" /etc/nginx/nginx.conf

echo "==> Starting Brainstormer Agent on port 8001..."
cd /app/brainstormer-agent && uvicorn main:app --host 0.0.0.0 --port 8001 --log-level info &

echo "==> Starting Critic Agent on port 8002..."
cd /app/critic-agent && uvicorn main:app --host 0.0.0.0 --port 8002 --log-level info &

echo "==> Starting Roadmap Agent on port 8003..."
cd /app/roadmap-agent && uvicorn main:app --host 0.0.0.0 --port 8003 --log-level info &

echo "==> Starting Task Agent on port 8004..."
cd /app/task-agent && uvicorn main:app --host 0.0.0.0 --port 8004 --log-level info &

echo "==> Starting Pitch Deck Agent on port 8005..."
cd /app/pitch-deck-agent && uvicorn main:app --host 0.0.0.0 --port 8005 --log-level info &

# Wait for all 5 agents to be ready before starting nginx
echo "==> Waiting for all agents to be ready..."
for PORT_NUM in 8001 8002 8003 8004 8005; do
  echo -n "    Waiting for port $PORT_NUM..."
  for i in $(seq 1 30); do
    if curl -sf "http://localhost:$PORT_NUM/" > /dev/null 2>&1; then
      echo " ready!"
      break
    fi
    if [ $i -eq 30 ]; then
      echo " TIMEOUT after 30s — check agent logs above"
    fi
    sleep 1
  done
done

echo "==> All agents ready. Starting nginx on port $PORT..."
nginx -g "daemon off;"
