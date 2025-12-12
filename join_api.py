# join_api.py
# Start the conversational AI agent with RAG server

import base64
import requests
import json
from config import *

# ==========================
# Encode customer_key:customer_secret → Base64
# ==========================
raw_cred = f"{CUSTOMER_KEY}:{CUSTOMER_SECRET}"
BASIC_AUTH = base64.b64encode(raw_cred.encode()).decode()

# ==========================
# Agora Join URL
# ==========================
url = f"https://api.agora.io/api/conversational-ai-agent/v2/projects/{APP_ID}/join"

# ==========================
# Headers
# ==========================
headers = {
    "Authorization": f"Basic {BASIC_AUTH}",
    "Content-Type": "application/json"
}

# ==========================
# RAG SERVER CONFIGURATION
# ==========================
# Change this to your RAG server URL
# If running locally: http://localhost:8000/rag/chat/completions
# If deployed: https://your-server.com/rag/chat/completions
RAG_SERVER_URL = "https://noncontingently-stotious-edris.ngrok-free.dev/rag/chat/completions"

# Set to True to use RAG, False to use direct Groq
USE_RAG = True

# ==========================
# Request Body
# ==========================
payload = {
    "name": "rag_agent_01",
    "properties": {
        "channel": CHANNEL_NAME,
        "token": AGORA_TEMP_TOKEN,
        "agent_rtc_uid": AGENT_RTC_UID,
        "remote_rtc_uids": [USER_RTC_UID],
        "idle_timeout": IDLE_TIMEOUT,

        "advanced_features": {
            "enable_aivad": True
        },

        # ========= LLM Configuration ==========
        "llm": {
            # Use RAG server if enabled, otherwise use Groq directly
            "url": RAG_SERVER_URL if USE_RAG else "https://api.groq.com/openai/v1/chat/completions",
            "api_key": "" if USE_RAG else GROQ_KEY,  # RAG server handles API key
            "system_messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ],
            "max_history": MAX_HISTORY,
            "greeting_message": GREETING_MESSAGE,
            "failure_message": FAILURE_MESSAGE,
            "params": {
                "model": LLM_MODEL
            }
        },

        # ========= TTS (Groq) =========
        "tts": {
            "vendor": "groq",
            "params": {
                "api_key": TTS_GROQ_KEY,
                "model": TTS_MODEL,
                "voice": TTS_VOICE
            }
        },

        # ========= ASR (AssemblyAI) ========
        "asr": {
            "vendor": "assemblyai",
            "params": {
                "api_key": ASSEMBLY_AI_KEY,
                "language": ASR_LANGUAGE
            }
        }
    }
}

# ==========================
# SEND REQUEST
# ==========================
print("=" * 60)
print("🚀 Starting AI Agent with RAG")
print("=" * 60)
print(f"Channel: {CHANNEL_NAME}")
print(f"Agent UID: {AGENT_RTC_UID}")
print(f"User UID: {USER_RTC_UID}")
print(f"RAG Mode: {'ENABLED ✅' if USE_RAG else 'DISABLED ❌'}")
if USE_RAG:
    print(f"RAG Server: {RAG_SERVER_URL}")
print("=" * 60)

response = requests.post(url, headers=headers, data=json.dumps(payload))

print("\n📊 Response:")
print("-" * 60)
print("Status Code:", response.status_code)

if response.status_code == 200:
    result = response.json()
    print("\n✅ SUCCESS!")
    print(f"Agent ID: {result['agent_id']}")
    print(f"Status: {result['status']}")
    print(f"Created: {result['create_ts']}")
    print("\n" + "=" * 60)
    print("⚠️  SAVE THIS AGENT ID FOR STOPPING:")
    print(f"   {result['agent_id']}")
    print("=" * 60)

    if USE_RAG:
        print("\n💡 RAG is ACTIVE!")
        print("   The AI will answer based on my_city_info.txt")
        print("   Try asking: 'Tell me about Shibuya in Tokyo'")
else:
    print("\n❌ FAILED!")
    try:
        print("Error:", response.json())
    except:
        print("Error:", response.text)

print("\n✨ You can now open index.html and click 'Start Conversation'")
