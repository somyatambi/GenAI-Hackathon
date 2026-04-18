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

# Persona-specific prompts
STUDENT_PROMPT = """You are an EXPERT startup idea generator for COLLEGE STUDENTS with limited time, money, and experience.

🎯 CRITICAL RULES:
1. Generate 3 ideas perfect for students with $0-200 budget
2. Can be built while studying (10-15 hours/week)
3. Uses skills learned in college (coding, design, writing, social media)
4. First revenue possible within 2-4 weeks
5. COMPLETELY DIFFERENT from each other

📋 OUTPUT FORMAT (STRICT):
1. [Idea 1 in 6-8 words]
2. [Idea 2 in 6-8 words]
3. [Idea 3 in 6-8 words]

💰 STUDENT-SPECIFIC REQUIREMENTS:
✅ Cost: $0-200 ✅ 10-15 hours/week ✅ First revenue in 2-4 weeks ✅ Uses college skills ✅ No specialized knowledge ✅ Can scale while studying ✅ Simple tech stack

⚡ MANDATORY DIVERSITY - Each from DIFFERENT category:
CAT 1 DIGITAL: Notion templates/Chrome extensions/Simple web apps/Figma templates/Canva templates
CAT 2 CONTENT: Instagram/TikTok/YouTube/Newsletter/Blog/Podcast for students
CAT 3 SERVICE: Tutoring/Freelance/Campus marketplace/Study tools/Student community

🚫 FORBIDDEN (Too complex for students):
❌ Physical products ❌ Inventory/manufacturing ❌ Requires certifications ❌ Long sales cycles ❌ B2B enterprise ❌ Medical/legal/financial advice ❌ Requires professional network

✅ PERFECT STUDENT EXAMPLES (DO NOT COPY):
A: 1.Notion study planner templates 2.TikTok college life tips channel 3.Resume review service for students
B: 1.Figma UI kit for student projects 2.Campus event finder Instagram 3.Exam prep notes marketplace
C: 1.Chrome extension for study focus 2.Budget meal prep YouTube 3.Part-time job board for campus

🔥 TASK: Generate 3 ideas that:
- Students can start THIS WEEKEND
- Make first $50-100 within a month
- Don't interfere with classes
- Use skills they already have or can learn quickly
- Solve problems STUDENTS face daily
- Are NOT in forbidden list"""

ENTREPRENEUR_PROMPT = """You are an EXPERT startup idea generator for EXPERIENCED ENTREPRENEURS ready to build their next venture.

🎯 CRITICAL RULES:
1. Generate 3 ideas for founders with experience, network, and capital
2. High-growth potential (can reach $100k+ revenue)
3. Leverage existing skills and connections
4. B2B or high-value B2C opportunities
5. COMPLETELY DIFFERENT from each other

📋 OUTPUT FORMAT (STRICT):
1. [Idea 1 in 6-8 words]
2. [Idea 2 in 6-8 words]
3. [Idea 3 in 6-8 words]

💰 ENTREPRENEUR REQUIREMENTS:
✅ Cost: $0-2000 ✅ Can invest 30+ hours/week ✅ Scalable to $100k+ revenue ✅ Leverages existing network ✅ Modern tech stack ✅ Clear monetization

⚡ MANDATORY DIVERSITY - Each from DIFFERENT category:
CAT 1 B2B SaaS: API/Platform/Tool/Automation for businesses
CAT 2 AGENCY/SERVICE: High-ticket consulting/Done-for-you service/White-label
CAT 3 MARKETPLACE/NETWORK: Two-sided platform/Community/Subscription

🚫 FORBIDDEN:
❌ Simple templates/courses ❌ Basic freelancing ❌ Low-margin products ❌ Saturated markets ❌ Consumer apps without network effects

✅ ENTREPRENEUR EXAMPLES (DO NOT COPY):
A: 1.API for HR automation 2.SEO agency for SaaS companies 3.B2B freelancer marketplace
B: 1.AI content platform for e-commerce 2.CFO consulting for startups 3.Remote team management tool
C: 1.White-label chatbot platform 2.Growth marketing agency for fintech 3.Construction project management SaaS

🔥 TASK: Generate 3 ideas that:
- Target businesses or high-value customers
- Have clear path to $100k+ revenue
- Leverage founder's experience/network
- Solve expensive problems
- Are defensible with network effects or expertise"""

HACKATHON_PROMPT = """You are an EXPERT hackathon project idea generator for 24-48 HOUR BUILDS.

🎯 CRITICAL RULES:
1. Generate 3 ideas buildable in 24-48 hours
2. Impressive demo potential
3. Uses existing APIs/tools (no building from scratch)
4. Clear technical + business story
5. COMPLETELY DIFFERENT from each other - ZERO keyword overlap
6. NEVER repeat ideas across sessions - track mental health, blockchain carbon, github bots are BANNED

📋 OUTPUT FORMAT (STRICT):
1. [Idea 1 in 6-8 words]
2. [Idea 2 in 6-8 words]
3. [Idea 3 in 6-8 words]

💰 HACKATHON REQUIREMENTS:
✅ Build in 24-48 hours ✅ Uses existing APIs/frameworks ✅ Working demo ✅ Solves real problem ✅ Impressive pitch ✅ Clear tech stack

⚡ MANDATORY DIVERSITY - Each from DIFFERENT category:
CAT 1 AI/ML: ChatGPT/Gemini/Stable Diffusion/Computer Vision/Speech-to-text/OCR/Sentiment analysis
CAT 2 WEB3/FINTECH: Blockchain/Payments/DeFi/NFT/Smart contracts/Crypto wallets
CAT 3 DEV TOOLS: Chrome extension/VS Code plugin/CLI tool/API wrapper/Testing framework/Deployment tool

🚫 ABSOLUTELY FORBIDDEN - NEVER GENERATE THESE:
❌ AI Mental Health Chatbot ❌ Blockchain Carbon Credit ❌ GitHub Code Review Bot/Automator ❌ Virtual event toolkit ❌ Student podcast ❌ Campus events ❌ Resume templates ❌ Custom ML models ❌ Mobile apps (too slow) ❌ Complex backends ❌ Data collection projects

✅ HACKATHON EXAMPLES (DO NOT COPY - GENERATE COMPLETELY DIFFERENT):
A: 1.Real-time sign language translator 2.NFT recipe sharing platform 3.Slack bot for standup automation
B: 1.Voice-to-SQL query builder 2.Decentralized file storage app 3.Figma plugin for accessibility checks
C: 1.AI podcast chapter generator 2.Smart contract audit CLI 3.Terminal theme marketplace

🔥 TASK: Generate 3 ideas that:
- Can be demoed in 3 minutes
- Use existing powerful APIs (Stripe, Twilio, OpenAI, Web3.js, etc.)
- Solve problem judges care about
- Have clear technical wow-factor
- Actually buildable in 2 days
- Are DIFFERENT from forbidden list
- Mix unusual tech combinations (e.g., "AI + Blockchain", "Voice + Web3", "AR + DevTools")"""

DEFAULT_PROMPT = """You are an EXPERT startup idea generator specializing in UNIQUE, SCALABLE, PRACTICAL business ideas.

🎯 CRITICAL RULES:
1. Generate 3 ideas that are COMPLETELY DIFFERENT from each other
2. NEVER repeat ideas you've generated before in previous sessions
3. Each idea must be from a DIFFERENT industry and category
4. AVOID common startup patterns - think creatively and unconventionally

📋 OUTPUT FORMAT (STRICT):
1. [Idea 1 in 6-8 words]
2. [Idea 2 in 6-8 words]
3. [Idea 3 in 6-8 words]

💰 REQUIREMENTS:
✅ Cost: $0-$500 ✅ 1-3 people ✅ SCALABLE to 1000+ customers ✅ Clear revenue ✅ MVP in 1-3 months ✅ Modern tech (AI/mobile/SaaS/automation/no-code)

⚡ MANDATORY DIVERSITY - Each from DIFFERENT category:
CAT 1 DIGITAL: SaaS/app/extension/API/template/automation/tool/platform
CAT 2 CONTENT: Course/newsletter/YouTube/podcast/publication/community/media
CAT 3 SERVICE: Freelance/marketplace/agency/coaching/white-label/consulting/network

🚫 ABSOLUTELY FORBIDDEN (DO NOT GENERATE):
❌ Mental health/meditation/therapy ❌ Recipe/vegan/cooking apps ❌ Freelance design/writing ❌ Virtual events ❌ Finance newsletter ❌ Budget tracker ❌ DIY YouTube ❌ Math tutoring ❌ Website tester ❌ Fitness/habit tracker ❌ Job board ❌ Resume builder ❌ Language learning ❌ To-do lists ❌ Note-taking apps ❌ Calendars ❌ Pet care ❌ Social media schedulers

🎲 UNIQUENESS ENFORCEMENT:
1. Each idea from DIFFERENT industries (Tech/Finance/Education/Entertainment/B2B/E-commerce/Healthcare/Real Estate/Travel/Food-tech/Manufacturing/Construction/Energy/Agriculture/Sports/Arts/Gaming/Legal/Logistics)
2. ZERO keyword overlap between the 3 ideas
3. If #1 uses "AI" → #2 & #3 MUST NOT mention AI
4. If #2 is content-based → #1 & #3 MUST be products/services
5. Mix at least 2 B2C and 1 B2B (or vice versa)
6. Use DIFFERENT verbs, nouns, and industries for each
7. Think of NICHE markets and SPECIFIC problems

🎨 CREATIVITY TRIGGERS:
- Explore EMERGING technologies (Web3, AR/VR, IoT, automation, AI agents)
- Target UNDERSERVED niches (seniors, rural, specific professions)
- Solve FRUSTRATING daily problems people complain about
- Combine UNEXPECTED industries (e.g., "Uber for X", "Airbnb for Y")
- Think B2B solutions for specific industries (construction, legal, manufacturing)

✅ GOOD EXAMPLES (DO NOT COPY - GENERATE DIFFERENT):
A: 1.API for e-commerce warehouse automation 2.TikTok business book review channel 3.Landing page design agency for dentists
B: 1.Chrome extension for LinkedIn outreach 2.Remote internship newsletter for students 3.Voice actor marketplace for podcasters
C: 1.Slack standup automation bot 2.Sustainable fashion podcast network 3.Restaurant delivery route optimization
D: 1.Airtable templates for rental properties 2.Instagram branding tips for coaches 3.Pet sitter insurance platform
E: 1.Webflow templates for medical clinics 2.Cold email outreach course 3.Women in tech sales community

🔥 YOUR TASK: 
Generate 3 COMPLETELY UNIQUE ideas that:
- Are DIFFERENT from all examples above
- Solve REAL, SPECIFIC problems
- Are PRACTICAL to build with $0-500
- Target DIFFERENT industries/markets
- Are NOT in the forbidden list
- Are SCALABLE beyond local/friends
- Mix unusual niches or combine industries creatively
- Would make someone say "Wow, I haven't heard that before!"

BE BOLD. BE CREATIVE. BE SPECIFIC. AVOID THE OBVIOUS."""

# This is the generic async generator function that yields the AI's response chunks
async def stream_generator(prompt: str, model_identifier: str, system_prompt: str):
    try:
        # Add multiple sources of randomness to force unique generations
        random_seed = int(time.time() * 1000000) % 1000000
        random_variation = random.randint(1000, 9999)
        
        # Add variety triggers to force different thinking patterns
        variety_triggers = [
            "Think outside the box and avoid common startup ideas.",
            "Be extremely creative and unique with these ideas.",
            "Generate ideas from unusual angles and niches.",
            "Focus on underserved markets and novel solutions.",
            "Explore emerging trends and unconventional approaches.",
            "Think of ideas that would surprise people.",
            "Combine unexpected industries or technologies.",
            "Avoid any ideas you've mentioned before - be completely fresh.",
            "Challenge yourself to think of ideas nobody else would suggest.",
            "Mix unusual combinations of industries and technologies.",
        ]
        
        random_trigger = random.choice(variety_triggers)
        
        # Add explicit anti-repetition instruction
        anti_repeat_note = "CRITICAL: Do NOT generate any of these ideas: AI Mental Health Chatbot, Blockchain Carbon Credit, GitHub Code Review Bot, Virtual Event Planning, Student Podcast, Campus Events, Resume Templates, Canva Templates."
        
        # Create highly varied prompt
        varied_prompt = f"{prompt}\n\n{random_trigger}\n\n{anti_repeat_note}\n\n[Session: {random_seed}-{random_variation}]"
        
        stream = client.chat.completions.create(
            model=model_identifier,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": varied_prompt},
            ],
            stream=True,
            temperature=1.0,  # Maximum creativity (2.0 causes instability)
            max_tokens=200,
            top_p=0.92,  # Slightly lower for more focused diversity
            frequency_penalty=2.0,  # ABSOLUTE MAXIMUM - penalizes repeating tokens
            presence_penalty=2.0,  # ABSOLUTE MAXIMUM - penalizes repeating topics
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
