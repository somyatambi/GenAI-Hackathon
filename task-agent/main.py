import os
import traceback
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
# Updated: 2025-10-05 16:20 - Added /tasks endpoint

# 1. Define the request model
class AgentRequest(BaseModel):
    prompt: str

# 2. Initialize the FastAPI app and add middleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "agent": "Task Agent", "message": "Agent is running"}

# 3. Initialize Cerebras API client (blazing fast for structured output!)
# This demonstrates multi-provider orchestration: Llama for creativity, Cerebras for speed
cerebras_client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY")
)

# Fallback to OpenRouter if Cerebras fails
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# 4. Define the async stream generator with fallback
async def stream_generator(prompt: str, model: str, system_prompt: str, use_cerebras: bool = True):
    try:
        if use_cerebras:
            print(f"[TASK AGENT] Attempting Cerebras API with model: {model}")
            client = cerebras_client
        else:
            print(f"[TASK AGENT] Using OpenRouter fallback with model: {model}")
            client = openrouter_client
            
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            max_tokens=1500,
            temperature=0.7
        )
        
        has_content = False
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                has_content = True
                yield content
        
        if not has_content:
            print("[TASK AGENT] WARNING: Stream completed but no content received")
            yield "No tasks generated. Please try again."
            
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"[TASK AGENT] ERROR in stream_generator: {e}")
        print(f"[TASK AGENT] Full traceback:\n{error_details}")
        
        # Try fallback to OpenRouter if Cerebras failed
        if use_cerebras:
            print("[TASK AGENT] Cerebras failed, trying OpenRouter fallback...")
            async for content in stream_generator(prompt, "meta-llama/llama-3.3-70b-instruct", system_prompt, use_cerebras=False):
                yield content
        else:
            yield f"Error: Unable to generate tasks. Please check API configuration.\n\nDetails: {str(e)}"

# 5. Define the API endpoint
@app.post("/generate")
@app.post("/tasks")
async def generate_response(request: AgentRequest):
    # Using Cerebras for ultra-fast structured output generation
    # Cerebras inference is 20x faster than traditional GPU inference!
    model = "llama3.1-8b"  # Cerebras-optimized Llama model
    system_prompt = """You are a strategic project architect with expertise in task breakdown and execution planning.

Given a project phase or goal, create a comprehensive, professional task breakdown with:
- Clear, action-oriented task titles
- Smart categorization (🚀 Quick Wins | 🎯 Core Tasks | 📈 Growth Goals)
- Brief context for why each task matters
- Realistic effort estimates with ranges (account for varying skill levels and complexity)
- Difficulty ratings to help prioritization

Format each task as: [Category] Task Title (Effort: X-Yh | Difficulty: Level) - Brief context

Difficulty Levels:
- Easy: Straightforward, well-documented, minimal complexity
- Medium: Requires some planning, moderate complexity
- Hard: Complex, requires deep thinking, critical feature

Example:
🚀 Set up project repository (Effort: 0.5-1h | Difficulty: Easy) - Foundation for version control and team collaboration
🚀 Configure linting tools (Effort: 1-2h | Difficulty: Easy) - Code quality standards and consistency
🎯 Design database schema (Effort: 2-4h | Difficulty: Medium) - Critical for data integrity and scalability
🎯 Implement authentication flow (Effort: 3-5h | Difficulty: Hard) - Security backbone, handles edge cases
🎯 Build API endpoints (Effort: 2-3h | Difficulty: Medium) - Backend infrastructure for data flow
📈 Add analytics tracking (Effort: 1-2h | Difficulty: Easy) - Enables data-driven decisions
📈 Set up error monitoring (Effort: 2-3h | Difficulty: Medium) - Production debugging infrastructure

Provide 5-7 tasks total. Be specific, actionable, and inspiring. Use realistic time ranges based on typical developer experience."""
    return StreamingResponse(stream_generator(request.prompt, model, system_prompt), media_type='text/plain')