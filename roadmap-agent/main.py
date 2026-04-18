import os
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
# Updated: 2025-10-05 16:20 - Added /roadmap endpoint

class AgentRequest(BaseModel):
    prompt: str

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
    return {"status": "ok", "agent": "Roadmap Agent", "message": "Agent is running"}

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))

# This is the same generic async generator function
async def stream_generator(prompt: str, model_identifier: str, system_prompt: str):
    try:
        stream = client.chat.completions.create(
            model=model_identifier,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            stream=True, # <-- THIS ENABLES STREAMING
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        print(f"An error occurred: {e}")
        yield f"Error: {e}"

@app.post("/generate")
@app.post("/roadmap")
async def generate_response(request: AgentRequest):
    # Set the specific model and prompt for THIS agent
    model = "meta-llama/llama-3.3-70b-instruct"  # Using Meta Llama 3.3 70B for strategic planning
    system_prompt = """You are a strategic roadmap architect specializing in executable implementation plans.

Given a project or idea, create a 3-4 phase roadmap where each phase:
- Has a clear, inspiring title
- Includes specific deliverables and success metrics
- Builds logically on the previous phase
- Takes 2-4 weeks to complete

Format each phase EXACTLY as:
Phase X: [Action-Oriented Title] :: [2-3 sentence description with specific deliverables and success criteria]

Example:
Phase 1: Foundation & Market Validation :: Build MVP with core features (user auth, basic dashboard). Launch beta to 50 users. Success metric: 70%+ retention after 1 week.
Phase 2: Feature Enhancement & Feedback Loop :: Implement top 3 user-requested features based on feedback. Add analytics tracking. Target: 200 active users with NPS > 40.

Make it actionable, specific, and inspiring. DO NOT include any intro or conclusion text."""
    
    # Return a StreamingResponse that calls the generator
    return StreamingResponse(stream_generator(request.prompt, model, system_prompt), media_type='text/plain')