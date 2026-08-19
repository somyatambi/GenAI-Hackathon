import os
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import random
import time

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
    return {"status": "ok", "agent": "Brainstormer Agent", "message": "Agent is running"}

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))

# Persona-specific prompts. Personas set feasibility constraints, not domains.
STUDENT_PROMPT = """You generate business ideas for a college student with limited money, time, and experience.

Generate exactly 3 genuinely different ideas. The domain is unrestricted: choose freely from any
industry or human need, including physical-world opportunities, local services, agriculture, crafts,
food, transport, sports, arts, education, accessibility, climate, manufacturing, or technology.
Do not default to student tools, social media, templates, apps, or software.

Every idea must be feasible to start with $0-$200, 10-15 hours per week, and skills that can be
learned quickly. It should have a realistic first customer or first $50-$100 of revenue within a
month. Avoid regulated work, inventory-heavy businesses, dangerous activities, and long enterprise
sales cycles. Do not assume the customer is a student.

Make the three ideas unrelated in customer, problem, and domain. For each, output one numbered line
with a specific name, target customer, what is offered, and why it is feasible in 20-35 words.
Use this format only: 1. ... 2. ... 3. ..."""

ENTREPRENEUR_PROMPT = """You generate venture ideas for an experienced entrepreneur with capital, business skills,
and a network.

Generate exactly 3 genuinely different ideas from any domain. Do not restrict yourself to software,
AI, SaaS, marketplaces, or internet businesses. Consider overlooked opportunities in real-world
industries, supply chains, manufacturing, energy, agriculture, healthcare operations, travel,
housing, professional services, culture, sports, and consumer products as well as technology.

Each idea must solve a specific expensive problem, identify a reachable customer, have a clear
revenue model, and be feasible to validate before building at scale. Favor underserved niches and
defensible insight over generic startup patterns. Avoid saturated ideas, simple templates, and
basic freelancing. Do not force the ideas into different business-model categories.

Make the three ideas unrelated in customer, problem, and domain. For each, output one numbered line
with a specific name, target customer, solution, revenue model, and feasibility signal in 20-35 words.
Use this format only: 1. ... 2. ... 3. ..."""

HACKATHON_PROMPT = """You generate original project ideas for a 24-48 hour hackathon build.

Generate exactly 3 genuinely different ideas from any domain. Technology is optional: a project may
serve a physical-world, community, creative, environmental, accessibility, education, retail,
transport, sports, agriculture, or other real problem. Do not force AI, blockchain, finance,
developer tools, mobile apps, or web apps into the ideas.

Each idea must have a narrow user problem, a convincing three-minute demo, a small demonstrable
prototype using available tools or a simple manual workflow, and a clear reason people would care.
Avoid complex backends, custom model training, hardware dependencies, regulated advice, and projects
that need large datasets or long partnerships.

Make the three ideas unrelated in user, problem, and domain. For each, output one numbered line with
a specific name, user problem, demoable solution, and why it fits 24-48 hours in 20-35 words.
Use this format only: 1. ... 2. ... 3. ..."""

DEFAULT_PROMPT = """You are an exceptionally creative but practical idea generator.

Generate exactly 3 original, feasible ideas. The domain is completely unrestricted: explore any
industry, community, occupation, geography, lifestyle, or physical-world problem. Do not assume the
answer is a startup, software product, AI tool, content channel, marketplace, or online service.
Ideas may involve ordinary businesses, products, processes, events, services, or technology.

Choose three unrelated domains and avoid obvious or saturated concepts. Each idea must identify a
specific underserved customer and painful problem, explain the offering, show a realistic way to
start small, and include a plausible revenue path. Prefer ideas that a small team can validate with
limited resources over ideas that need massive funding, regulation, or a large network on day one.

For each idea, output one numbered line with a memorable name, target customer, solution, and
feasibility signal in 20-35 words. Use this format only: 1. ... 2. ... 3. ..."""

# This is the generic async generator function that yields the AI's response chunks
async def stream_generator(prompt: str, model_identifier: str, system_prompt: str):
    try:
        # Add multiple sources of randomness to force unique generations
        random_seed = int(time.time() * 1000000) % 1000000
        random_variation = random.randint(1000, 9999)
        
        # Add variety triggers to force different thinking patterns
        variety_triggers = [
            "Explore an overlooked everyday problem in an unexpected industry.",
            "Include at least one idea that is not primarily software or online.",
            "Look beyond technology startups: consider physical, local, social, or operational solutions.",
            "Find a small underserved customer group with a problem people usually ignore.",
            "Combine two unrelated fields only when the combination creates practical value.",
            "Prefer a surprising but simple solution over a fashionable technology label.",
            "Consider opportunities in how people make, move, buy, repair, learn, work, or live.",
            "Choose fresh directions across unrelated industries and customer types.",
            "Challenge the default assumption that this should be an app or platform.",
            "Think globally across urban, rural, professional, cultural, and community contexts.",
        ]
        
        random_trigger = random.choice(variety_triggers)
        
        # The frontend supplies prior results so uniqueness survives across requests.
        anti_repeat_note = """CRITICAL UNIQUENESS RULE:
    Do not repeat, lightly rename, or paraphrase any idea in the previous-ideas block.
    If the current concept resembles a previous idea, change the target customer, problem,
    business model, and implementation approach enough to create a genuinely different idea.
    The previous-ideas block is an exclusion list, not inspiration. Never mention it in your output.
    Do not use a previous idea's domain as a shortcut for a new idea. Select a new domain and customer."""
        
        # Create highly varied prompt
        varied_prompt = f"{prompt}\n\n{random_trigger}\n\n{anti_repeat_note}\n\n[Session: {random_seed}-{random_variation}]"
        
        stream = client.chat.completions.create(
            model=model_identifier,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": varied_prompt},
            ],
            stream=True,
            temperature=1.15,
            max_tokens=200,
            top_p=0.95,
            frequency_penalty=1.0,
            presence_penalty=1.0,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        print(f"An error occurred: {e}")
        yield f"Error: {e}"

@app.post("/generate")
@app.post("/brainstorm")
async def generate_response(request: AgentRequest):
    # Extract persona from prompt if present
    persona = None
    user_prompt = request.prompt
    
    if request.prompt.startswith('[PERSONA:'):
        # Extract persona tag
        persona_end = request.prompt.find(']')
        persona = request.prompt[9:persona_end].strip().lower()
        user_prompt = request.prompt[persona_end+1:].strip()
    
    model = "meta-llama/llama-3.3-70b-instruct"
    
    # Select system prompt based on persona
    if persona == 'student':
        system_prompt = STUDENT_PROMPT
    elif persona == 'entrepreneur':
        system_prompt = ENTREPRENEUR_PROMPT
    elif persona == 'hackathon':
        system_prompt = HACKATHON_PROMPT
    else:
        system_prompt = DEFAULT_PROMPT
    
    return StreamingResponse(stream_generator(user_prompt, model, system_prompt), media_type='text/plain')
