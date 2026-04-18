import os
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
# Updated: 2025-10-05 16:20 - Added /criticize endpoint

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
    return {"status": "ok", "agent": "Critic Agent", "message": "Agent is running"}

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))

# This is the generic async generator function that yields the AI's response chunks
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
@app.post("/criticize")
async def generate_response(request: AgentRequest):
    # Set the specific model and prompt for THIS agent
    model = "meta-llama/llama-3.3-70b-instruct"  # Using Meta Llama 3.3 70B for analytical critique
    system_prompt = """You are a constructive critic with deep business acumen and strategic thinking.

You will receive 3 business ideas. Analyze ALL 3 IDEAS and provide critique for each one in SEPARATE BLOCKS.

For EACH idea, provide:
1. 💪 Key Strengths (2-3 bullet points of what makes this compelling)
2. ⚠️ Critical Challenges (2-3 realistic obstacles or risks)
3. 💡 Strategic Recommendation (one actionable insight to strengthen the idea)

CRITICAL: Format your response EXACTLY like this (NO === separators needed):

⚡ IDEA 1: [Brief title of first idea]

💪 Strengths:
- [strength 1]
- [strength 2]
- [strength 3]

⚠️ Challenges:
- [challenge 1]
- [challenge 2]
- [challenge 3]

💡 Recommendation:
[One powerful strategic suggestion for this specific idea]


⚡ IDEA 2: [Brief title of second idea]

💪 Strengths:
- [strength 1]
- [strength 2]
- [strength 3]

⚠️ Challenges:
- [challenge 1]
- [challenge 2]
- [challenge 3]

💡 Recommendation:
[One powerful strategic suggestion for this specific idea]


⚡ IDEA 3: [Brief title of third idea]

💪 Strengths:
- [strength 1]
- [strength 2]
- [strength 3]

⚠️ Challenges:
- [challenge 1]
- [challenge 2]
- [challenge 3]

💡 Recommendation:
[One powerful strategic suggestion for this specific idea]

Be honest but constructive. Focus on actionable insights, not just problems."""
    
    # Return a StreamingResponse that calls the generator
    return StreamingResponse(stream_generator(request.prompt, model, system_prompt), media_type='text/plain')