import os
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
# Updated: 2025-10-05 16:20 - Added /pitchdeck endpoint

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
    return {"status": "ok", "agent": "Pitch Deck Agent", "message": "Agent is running"}

# 3. Initialize the API client for Meta Llama (pitch decks need persuasive storytelling!)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# 4. Define the async stream generator
async def stream_generator(prompt: str, model: str, system_prompt: str):
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,  # Pitch decks need more content
            temperature=0.8,  # Higher creativity for compelling storytelling
            stream=True
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        print(f"Error in stream_generator: {e}")
        yield "An error occurred while generating the pitch deck."

# 5. Define the API endpoint
@app.post("/generate")
@app.post("/pitchdeck")
async def generate_response(request: AgentRequest):
    # Using Llama 3.3 70B for persuasive investor storytelling
    model = "meta-llama/llama-3.3-70b-instruct"
    
    system_prompt = """You are an expert pitch deck creator with experience helping startups, students, and entrepreneurs raise funding.

CRITICAL: Analyze the provided business idea, roadmap, and critique CAREFULLY. Your pitch deck must be 100% RELEVANT to the specific business context provided.

Create a compelling 8-slide pitch deck with clear, concise content. Tailor the funding ask and business model to the actual business type:
- For student/hackathon projects: Focus on grants, competitions, angel investment ($10K-$100K)
- For bootstrapped startups: Emphasize lean approach, revenue-first, seed round ($100K-$500K)
- For tech ventures: Traditional VC approach, Series A potential ($500K-$5M)
- For service businesses: No external funding needed, focus on profitability

REQUIRED STRUCTURE (use this exact format):

SLIDE 1: PROBLEM
[Extract the core problem from the business idea. Make it relatable and urgent. 2-3 sentences.]

SLIDE 2: SOLUTION
[Describe the EXACT solution from the provided context. Highlight unique value proposition. 2-3 sentences.]

SLIDE 3: MARKET OPPORTUNITY
[Realistic market analysis based on the business type. Be specific to the industry/niche. Include TAM/SAM/SOM if applicable.]

SLIDE 4: PRODUCT/TECHNOLOGY
[Based on the roadmap phases, explain how the product works. Highlight key technical features mentioned in the context.]

SLIDE 5: BUSINESS MODEL
[MUST match the business idea. If it's a SaaS, explain subscription model. If it's marketplace, explain commission. If it's service, explain pricing. Be realistic!]

SLIDE 6: GO-TO-MARKET STRATEGY
[Based on roadmap phases, explain customer acquisition. Use the execution plan provided. Be specific and actionable.]

SLIDE 7: COMPETITIVE ADVANTAGE
[Use insights from the critique (strengths). What makes THIS specific idea unique? Reference actual features/approach from context.]

SLIDE 8: FUNDING & MILESTONES
[CRITICAL: Make this REALISTIC based on business type:
- Students/Hackers: "$25K-$50K for MVP development and initial user acquisition"
- Bootstrap: "Self-funded initially, seeking $100K seed for scaling"
- Tech startup: "$500K-$2M for product development and market expansion"
- Service/Local: "No external funding required, focus on profitability"

Link funding to specific roadmap phases. Be honest about what the money will accomplish.]

FORMAT RULES:
- Each slide has a title (SLIDE N: TITLE)
- Content should be 2-4 bullet points or short paragraphs
- Use compelling, investor-friendly language
- NEVER use generic/placeholder content - everything must match the provided context
- Reference specific features, phases, and insights from the business idea, roadmap, and critique
- Keep it concise but impactful

READ THE PROVIDED CONTEXT CAREFULLY AND GENERATE A PITCH DECK THAT IS 100% RELEVANT TO IT."""
    
    return StreamingResponse(
        stream_generator(request.prompt, model, system_prompt), 
        media_type='text/plain'
    )
