# Multi-stage build for all agents
FROM python:3.9-slim as base

# Cache buster - change this value to force rebuild
ARG CACHEBUST=9

WORKDIR /app

# Install nginx and curl for routing and health checks
RUN apt-get update && apt-get install -y nginx curl && rm -rf /var/lib/apt/lists/*

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

# Copy startup script (replaces the fragile echo-based approach)
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8080

CMD ["/bin/bash", "/app/start.sh"]
