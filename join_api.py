# join_api.py
# Start the conversational AI agent

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
# Request Body
# ==========================
payload = {
    "name": "test_agent_01",
    "properties": {
        "channel": CHANNEL_NAME,
        "token": AGORA_TEMP_TOKEN,
        "agent_rtc_uid": AGENT_RTC_UID,
        "remote_rtc_uids": [USER_RTC_UID],
        "idle_timeout": IDLE_TIMEOUT,

        "advanced_features": {
            "enable_aivad": True
        },

        # ========= LLM (Groq) ==========
        "llm": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "api_key": GROQ_KEY,
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
print("=" * 50)
print("🚀 Starting AI Agent...")
print("=" * 50)
print(f"Channel: {CHANNEL_NAME}")
print(f"Agent UID: {AGENT_RTC_UID}")
print(f"User UID: {USER_RTC_UID}")
print("=" * 50)

response = requests.post(url, headers=headers, data=json.dumps(payload))

print("\n📊 Response:")
print("-" * 50)
print("Status Code:", response.status_code)

if response.status_code == 200:
    result = response.json()
    print("\n✅ SUCCESS!")
    print(f"Agent ID: {result['agent_id']}")
    print(f"Status: {result['status']}")
    print(f"Created: {result['create_ts']}")
    print("\n" + "=" * 50)
    print("⚠️  SAVE THIS AGENT ID FOR STOPPING:")
    print(f"   {result['agent_id']}")
    print("=" * 50)
else:
    print("\n❌ FAILED!")
    try:
        print("Error:", response.json())
    except:
        print("Error:", response.text)

print("\n✨ You can now open index.html and click 'Start Conversation'")
