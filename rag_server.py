"""
RAG Server for Agora AI Voice Chat
This server provides a custom LLM endpoint with RAG capabilities
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
import os
import json
import asyncio
import random
from openai import AsyncOpenAI
import logging

# Setup logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# ==========================
# CONFIGURATION
# ==========================
GROQ_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
KNOWLEDGE_BASE_PATH = "./my_city_info.txt"

# ==========================
# MODELS
# ==========================
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "llama-3.3-70b-versatile"
    messages: List[ChatMessage]
    stream: bool = True
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

# ==========================
# RAG FUNCTIONS
# ==========================
def load_knowledge_base(file_path: str) -> str:
    """Load the knowledge base from a text file"""
    try:
        if not os.path.exists(file_path):
            logger.error(f"❌ Knowledge base file not found: {file_path}")
            logger.error(f"Current directory: {os.getcwd()}")
            logger.error(f"Files in directory: {os.listdir('.')}")
            return ""

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.info(f"✅ Loaded knowledge base: {len(content)} characters")
        return content
    except Exception as e:
        logger.error(f"❌ Error loading knowledge base: {e}")
        return ""

def search_knowledge_base(query: str, knowledge_base: str) -> str:
    """
    Enhanced keyword-based search with Q&A format support
    Works well for location-based queries
    """
    logger.info(f"🔍 Searching for: '{query}'")

    if not knowledge_base:
        logger.error("❌ Knowledge base is empty!")
        return ""

    query_lower = query.lower()

    # Define location keywords
    location_keywords = {
        'coffee': ['coffee', 'café', 'cafe', 'breeze'],
        'chinese': ['chinese', 'dragon', 'wok', 'china'],
        'sri lankan': ['sri lankan', 'ceylon', 'spice', 'srilankan', 'sri'],
        'washroom': ['washroom', 'toilet', 'restroom', 'bathroom', 'loo', 'wc'],
        'conference': ['conference', 'hall', 'meeting', 'event'],
        'subway': ['subway', 'metro', 'train', 'underground'],
        'parking': ['parking', 'park', 'car'],
        'food': ['food', 'eat', 'restaurant', 'dining', 'meal'],
        'shop': ['shop', 'store', 'shopping', 'buy'],
        'atm': ['atm', 'cash', 'money', 'bank'],
        'wifi': ['wifi', 'wi-fi', 'internet', 'wireless'],
        'entrance': ['entrance', 'entry', 'door'],
        'information': ['information', 'info', 'help', 'desk'],
        'supermarket': ['supermarket', 'grocery', 'groceries'],
        'entertainment': ['entertainment', 'movie', 'cinema', 'arcade', 'play'],
        'second floor': ['second floor', '2nd floor', 'floor 2'],
        'third floor': ['third floor', '3rd floor', 'floor 3'],
        'ground floor': ['ground floor', 'first floor', 'floor 1'],
    }

    # Split knowledge base into sections
    sections = knowledge_base.split('\n\n')
    logger.info(f"📑 Split knowledge base into {len(sections)} sections")

    # Score each section
    scored_chunks = []
    for section in sections:
        if not section.strip():
            continue

        section_lower = section.lower()
        score = 0

        # Check for direct keyword matches
        for category, keywords in location_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                if any(keyword in section_lower for keyword in keywords):
                    score += 10
                    logger.debug(f"✓ Category match '{category}' in section starting: {section[:50]}")

        # Check for word overlap
        query_words = [w for w in query_lower.split() if len(w) > 3]
        for word in query_words:
            if word in section_lower:
                score += 1

        # Boost FAQ sections
        if section.strip().startswith('Q:') or section.strip().startswith('Where') or section.strip().startswith('How'):
            score += 5
            logger.debug(f"✓ FAQ boost for section: {section[:50]}")

        if score > 0:
            scored_chunks.append((score, section))
            logger.debug(f"Section score: {score}")

    # Sort by relevance and take top 4
    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    top_chunks = [chunk for _, chunk in scored_chunks[:4]]

    if top_chunks:
        result = "\n\n".join(top_chunks)
        logger.info(f"✅ Found {len(top_chunks)} relevant sections, total length: {len(result)}")
        logger.debug(f"First 200 chars of result: {result[:200]}")
        return result

    # If no matches, return overview and first sections
    logger.warning("⚠️ No specific matches, returning overview")
    return "\n\n".join(sections[:3])

def create_rag_enhanced_messages(
    original_messages: List[ChatMessage],
    retrieved_context: str
) -> List[Dict]:
    """
    Enhance messages with retrieved context
    """
    enhanced_messages = []

    # Add system message with context
    if retrieved_context:
        context_message = {
            "role": "system",
            "content": f"""You are a helpful tour guide assistant for Central City Mall. You have access to specific information about the mall.

Based on the following information:

{retrieved_context}

Instructions:
- Answer the user's questions clearly and concisely in 2-3 sentences maximum
- If asked about a location, provide specific floor and landmark information
- If the question is about directions, give step-by-step guidance
- Keep responses friendly and helpful
- If the information is not in the provided context, say "I don't have that specific information, but you can ask at the information desk on the ground floor"
- Always be welcoming and professional as a mall guide"""
        }
        enhanced_messages.append(context_message)
        logger.info(f"✅ Created system message with {len(retrieved_context)} chars of context")
    else:
        logger.warning("⚠️ No context retrieved, using default message")
        enhanced_messages.append({
            "role": "system",
            "content": "You are a helpful tour guide for Central City Mall. Answer briefly and clearly."
        })

    # Add original messages
    for msg in original_messages:
        if msg.role != "system":
            enhanced_messages.append({
                "role": msg.role,
                "content": msg.content
            })

    logger.info(f"📝 Total messages sent to LLM: {len(enhanced_messages)}")
    return enhanced_messages

# ==========================
# WAITING MESSAGES
# ==========================
WAITING_MESSAGES = [
    "Just a moment, checking the mall directory...",
    "Let me look that up for you...",
    "Good question, finding the information...",
]

# ==========================
# ENDPOINTS
# ==========================
@app.get("/")
async def root():
    return {
        "message": "RAG Server for Agora AI Voice Chat - Mall Guide Edition",
        "endpoints": {
            "/chat/completions": "Standard chat completions",
            "/rag/chat/completions": "RAG-enhanced chat completions",
            "/health": "Health check"
        },
        "status": "running"
    }

@app.get("/health")
async def health():
    kb_exists = os.path.exists(KNOWLEDGE_BASE_PATH)
    kb_size = os.path.getsize(KNOWLEDGE_BASE_PATH) if kb_exists else 0
    return {
        "status": "healthy",
        "knowledge_base_loaded": kb_exists,
        "knowledge_base_size": kb_size,
        "groq_api_configured": bool(GROQ_API_KEY)
    }

@app.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Standard OpenAI-compatible chat completions endpoint"""
    try:
        logger.info("📨 Received standard chat completion request")

        if not request.stream:
            raise HTTPException(status_code=400, detail="Chat completions require streaming")

        async def generate():
            try:
                client = AsyncOpenAI(
                    api_key=GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1"
                )

                messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

                response = await client.chat.completions.create(
                    model=request.model,
                    messages=messages,
                    stream=True,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature
                )

                async for chunk in response:
                    yield f"data: {json.dumps(chunk.model_dump())}\n\n"

                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"❌ Error in chat completion: {e}")
                error_msg = {"error": str(e)}
                yield f"data: {json.dumps(error_msg)}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"❌ Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/chat/completions")
async def rag_chat_completions(request: ChatCompletionRequest):
    """RAG-enhanced chat completions endpoint"""
    try:
        logger.info("=" * 60)
        logger.info("📨 NEW RAG CHAT COMPLETION REQUEST")
        logger.info("=" * 60)

        if not request.stream:
            raise HTTPException(status_code=400, detail="Chat completions require streaming")

        async def generate():
            try:
                # Step 1: Send waiting message
                logger.info("⏳ Step 1: Sending waiting message...")
                waiting_msg = {
                    "id": "waiting_msg",
                    "object": "chat.completion.chunk",
                    "created": 1234567890,
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": {
                            "role": "assistant",
                            "content": random.choice(WAITING_MESSAGES)
                        },
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(waiting_msg)}\n\n"

                # Step 2: Load knowledge base
                logger.info("📚 Step 2: Loading knowledge base...")
                knowledge_base = load_knowledge_base(KNOWLEDGE_BASE_PATH)
                if not knowledge_base:
                    logger.error("❌ Knowledge base is empty! Check file path.")
                    raise Exception("Knowledge base could not be loaded")

                # Step 3: Get the last user message
                logger.info("💬 Step 3: Extracting user query...")
                user_messages = [msg for msg in request.messages if msg.role == "user"]
                last_user_message = user_messages[-1].content if user_messages else ""
                logger.info(f"User query: '{last_user_message}'")

                # Step 4: Search knowledge base
                logger.info("🔍 Step 4: Searching knowledge base...")
                retrieved_context = search_knowledge_base(last_user_message, knowledge_base)
                logger.info(f"Retrieved context length: {len(retrieved_context)} characters")

                if not retrieved_context:
                    logger.warning("⚠️ No context retrieved! Using fallback.")
                    retrieved_context = knowledge_base[:500]  # Use first 500 chars as fallback

                # Step 5: Create enhanced messages
                logger.info("🔧 Step 5: Creating enhanced messages...")
                enhanced_messages = create_rag_enhanced_messages(request.messages, retrieved_context)

                # Step 6: Call LLM
                logger.info("🤖 Step 6: Calling Groq API...")
                client = AsyncOpenAI(
                    api_key=GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1"
                )

                response = await client.chat.completions.create(
                    model=request.model,
                    messages=enhanced_messages,
                    stream=True,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature
                )

                # Step 7: Stream the response
                logger.info("📡 Step 7: Streaming response...")
                chunk_count = 0
                async for chunk in response:
                    chunk_count += 1
                    yield f"data: {json.dumps(chunk.model_dump())}\n\n"

                logger.info(f"✅ Streamed {chunk_count} chunks successfully")
                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"❌ ERROR in RAG pipeline: {str(e)}", exc_info=True)
                error_msg = {
                    "id": "error_msg",
                    "object": "chat.completion.chunk",
                    "created": 1234567890,
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": {
                            "role": "assistant",
                            "content": "I apologize, I'm having trouble accessing the information right now. Please ask at the information desk on the ground floor."
                        },
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(error_msg)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"❌ RAG chat completion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ==========================
# RUN SERVER
# ==========================
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("🚀 Starting RAG Server - Mall Guide Edition")
    print("=" * 60)
    print(f"📚 Knowledge Base: {KNOWLEDGE_BASE_PATH}")

    # Check if knowledge base exists
    if os.path.exists(KNOWLEDGE_BASE_PATH):
        size = os.path.getsize(KNOWLEDGE_BASE_PATH)
        print(f"✅ Knowledge base found: {size} bytes")
    else:
        print(f"❌ WARNING: Knowledge base not found!")
        print(f"   Expected at: {os.path.abspath(KNOWLEDGE_BASE_PATH)}")
        print(f"   Current dir: {os.getcwd()}")

    print("🌐 Endpoints:")
    print("   - http://localhost:8000")
    print("   - http://localhost:8000/health")
    print("   - http://localhost:8000/rag/chat/completions")
    print("=" * 60)
    print("📝 Logging level: DEBUG (verbose)")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
