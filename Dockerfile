# Multi-stage build for all agents
FROM python:3.9-slim as base

# Cache buster - change this value to force rebuild
ARG CACHEBUST=9

WORKDIR /app

# Install nginx for routing
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Copy nginx config (updated with rewrite rules)
COPY nginx.conf /etc/nginx/nginx.conf

# Install Python dependencies for all agents
COPY brainstormer-agent/requirements.txt /app/brainstormer-requirements.txt
COPY critic-agent/requirements.txt /app/critic-requirements.txt
COPY roadmap-agent/requirements.txt /app/roadmap-requirements.txt
COPY task-agent/requirements.txt /app/task-requirements.txt
COPY pitch-deck-agent/requirements.txt /app/pitch-deck-requirements.txt

RUN pip install --no-cache-dir -r /app/brainstormer-requirements.txt \
    && pip install --no-cache-dir -r /app/critic-requirements.txt \
    && pip install --no-cache-dir -r /app/roadmap-requirements.txt \
    && pip install --no-cache-dir -r /app/task-requirements.txt \
    && pip install --no-cache-dir -r /app/pitch-deck-requirements.txt

# Copy all agent code (with direct endpoint support)
COPY brainstormer-agent /app/brainstormer-agent
COPY critic-agent /app/critic-agent
COPY roadmap-agent /app/roadmap-agent
COPY task-agent /app/task-agent
COPY pitch-deck-agent /app/pitch-deck-agent

# Create startup script with proper error handling and PORT environment variable
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Use PORT from environment or default to 8080\n\
export PORT=${PORT:-8080}\n\
echo "Using PORT: $PORT"\n\
\n\
# Update nginx config with the correct port\n\
sed -i "s/listen 8080;/listen $PORT;/" /etc/nginx/nginx.conf\n\
\n\
echo "Starting Brainstormer Agent..."\n\
cd /app/brainstormer-agent && uvicorn main:app --host 0.0.0.0 --port 8001 --log-level info &\n\
sleep 2\n\
echo "Starting Critic Agent..."\n\
cd /app/critic-agent && uvicorn main:app --host 0.0.0.0 --port 8002 --log-level info &\n\
sleep 2\n\
echo "Starting Roadmap Agent..."\n\
cd /app/roadmap-agent && uvicorn main:app --host 0.0.0.0 --port 8003 --log-level info &\n\
sleep 2\n\
echo "Starting Task Agent..."\n\
cd /app/task-agent && uvicorn main:app --host 0.0.0.0 --port 8004 --log-level info &\n\
sleep 2\n\
echo "Starting Pitch Deck Agent..."\n\
cd /app/pitch-deck-agent && uvicorn main:app --host 0.0.0.0 --port 8005 --log-level info &\n\
sleep 3\n\
echo "All agents started. Starting nginx on port $PORT..."\n\
nginx -g "daemon off;"\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8080

CMD ["/bin/bash", "/app/start.sh"]
