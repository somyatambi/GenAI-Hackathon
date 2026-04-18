# 🏗️ Cognitive Canvas - Technical Architecture

> Deep dive into the multi-agent system design, streaming architecture, and technical decisions.

## Table of Contents
1. [System Overview](#system-overview)
2. [Multi-Agent Architecture](#multi-agent-architecture)
3. [Docker Microservices Gateway Design](#docker-microservices-gateway-design)
4. [Frontend Architecture](#frontend-architecture)
5. [Streaming Response Pipeline](#streaming-response-pipeline)
6. [Security Considerations](#security-considerations)

---

## System Overview

Cognitive Canvas is a **distributed multi-agent system** built on microservices architecture. Each component is isolated, scalable, and communicates via HTTP streaming.

### High-Level Flow
```
User Input → Frontend → Gateway → Specialized Agent → Stream Response → Update Canvas
```

### Key Design Principles
1. **Agent Specialization**: Each agent has a single, well-defined responsibility
2. **Async Streaming**: Non-blocking real-time responses for better UX
3. **Model Diversity**: Match AI model to task requirements
4. **Visual First**: Canvas-based UI for spatial thinking

---

## Multi-Agent Architecture

### Agent Specialization Matrix

| Agent | Model | Provider | Use Case |
|-------|-------|----------|----------|
| **Brainstormer** | Llama 3.3 70B | OpenRouter | Generate 3 focused startup ideas |
| **Critic** | Llama 3.3 70B | OpenRouter | Provide constructive critique with strengths/weaknesses |
| **Roadmap** | Llama 3.3 70B | OpenRouter | Create phased development roadmaps |
| **Task** | Llama 3.1 8B | Cerebras | Generate actionable task lists (20x faster) |
| **Pitch Deck** | Llama 3.3 70B | OpenRouter | Generate investor-ready pitch deck content |

### Agent Communication Pattern

```python
# Each agent is a FastAPI microservice with a clear per-agent endpoint
# e.g. POST /brainstorm, /criticize, /roadmap, /tasks, /pitchdeck
@app.post("/brainstorm")
async def brainstorm(request: AgentRequest):
    return StreamingResponse(stream_generator(request.prompt, model, system_prompt), media_type='text/plain')

@app.get("/")
async def health():
    return {"status": "ok", "agent": "brainstormer"}
```

---

## Docker Microservices Design

### Deployment Modes

**1. Single Container (Render/Production)**
- All 5 agents + Nginx in one container
- Agents run on localhost:8001-8005
- Nginx gateway on port 8080 (configurable via PORT env var)

**2. Multi-Container (Local Development)**
- Each agent in separate Docker container
- Orchestrated via docker-compose.yml
- Nginx uses service names (e.g., `brainstormer-agent:8000`)

### Nginx Gateway Configuration

```nginx
# Production (single container): uses localhost
location = /brainstorm {
  proxy_pass http://localhost:8001/brainstorm;
  proxy_buffering off;
  chunked_transfer_encoding on;
}
```

**Key Features**:
- Streaming support: `proxy_buffering off`
- Dynamic port binding: Reads `PORT` env var (Render compatibility)
- CORS enabled: All agents allow cross-origin requests

Notes:
- The repository includes a `Dockerfile` for single-container deployment (convenient for platforms that accept a single image).
- For multi-container setups you can split agents into separate services and use Docker Compose or Kubernetes; not required for local testing.

---

## Frontend Architecture

### React Flow Integration

```tsx
// Dynamic node creation from streaming responses
const addNode = (content: string, type: string, parentId?: string) => {
  const newNode = {
  id: `node-${Date.now()}`,
  type: 'custom',
  data: { label: content, icon, color, agentName },
  position: calculatePosition(parentId)
  };
  setNodes([...nodes, newNode]);
};
```

### Streaming Response Handling

```tsx
// Real-time UI updates
const response = await axios.post(url, { prompt }, {
  responseType: 'stream',
  onDownloadProgress: (progressEvent) => {
  const text = progressEvent.event.target.responseText;
  updateNodeContent(text);
  }
});
```

---

## Streaming Response Pipeline

### End-to-End Flow

```
1. User clicks agent button
   ↓
2. Frontend → http://localhost:8080/{agent}/generate
   ↓
3. Nginx routes to agent container
   ↓
4. FastAPI streams OpenAI response
   ↓
5. Frontend receives chunks in real-time
   ↓
6. React Flow updates canvas progressively
```

### Implementation

**Backend (FastAPI)**
```python
async def stream_generator(prompt, model, system_prompt):
  stream = client.chat.completions.create(..., stream=True)
  for chunk in stream:
    if content := chunk.choices[0].delta.content:
      yield content
```

**Frontend (Axios)**
```tsx
onDownloadProgress: (event) => {
  fullText = event.target.responseText;
  setStreamingText(fullText);
}
```

---

## Security Considerations

### API Key Management
```bash
# Environment variables (never committed)
OPENROUTER_API_KEY=sk-or-v1-xxx
CEREBRAS_API_KEY=csk-xxx
```

### CORS Configuration
```python
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  # Development only
)
```

### Input Validation
```python
class AgentRequest(BaseModel):
  prompt: str

  @validator('prompt')
  def validate_prompt(cls, v):
    if len(v) > 1000:
      raise ValueError('Prompt too long')
    return v
```

---

## Technical Achievements

✅ **5 Specialized AI Agents** (Brainstormer, Critic, Roadmap, Task, Pitch Deck)  
✅ **Multi-Provider Orchestration** (OpenRouter + Cerebras)  
✅ **Real-Time Streaming** (Sub-second first-byte response)  
✅ **Docker Microservices** (Nginx gateway + isolated containers)  
✅ **React Flow Canvas** (Visual spatial thinking interface)

**Built with ❤️ for WeMakeDevs Fullstack GenAI Hackathon**

[← Back to README](./README.md)
