# Agora AI Voice Chat with RAG 🎙️🤖

A complete AI voice assistant solution using Agora's Conversational AI, featuring Retrieval-Augmented Generation (RAG) for custom knowledge base integration. Perfect for building intelligent mall guides, customer service bots, or any domain-specific voice assistant.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Agora](https://img.shields.io/badge/Agora-Conversational%20AI-orange.svg)](https://www.agora.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌟 Features

- ✅ **Voice-to-Voice AI Conversations** - Real-time speech-to-speech interaction
- ✅ **RAG Integration** - AI answers based on YOUR custom knowledge base
- ✅ **Web-Based UI** - Simple browser interface, no installation needed
- ✅ **Customizable** - Easy to adapt for any domain (malls, hotels, museums, etc.)
- ✅ **Multiple LLM Support** - Works with Groq, OpenAI, or any OpenAI-compatible API
- ✅ **Production Ready** - Includes diagnostics, testing tools, and deployment guide

---

## 🎯 Use Cases

- 🏬 **Mall/Shopping Center Guides** - Help visitors find stores, restaurants, facilities
- 🏨 **Hotel Concierge** - Answer guest questions about amenities, dining, services
- 🏛️ **Museum Tours** - Provide information about exhibits, artifacts, history
- 🏢 **Corporate Directories** - Help employees/visitors navigate buildings and services
- 📚 **Educational Assistants** - Answer questions based on course materials or documentation

---

## 📁 Project Structure

```
agora-ai-voice-chat/
│
├── config.py              # Central configuration (API keys, settings)
├── join_api.py           # Start the AI agent
├── stop_api.py           # Stop the AI agent
├── rag_server.py         # RAG server with custom LLM endpoint
├── my_city_info.txt      # Your knowledge base (customize this!)
├── index.html            # Web UI for voice chat
├── diagnose_rag.py       # Diagnostic tool for troubleshooting
├── test_rag.py           # Test RAG responses
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- [Agora Account](https://console.agora.io/) (free tier available)
- [Groq API Key](https://console.groq.com/) (free tier available)
- [AssemblyAI API Key](https://www.assemblyai.com/) (for speech recognition)
- Modern web browser (Chrome, Firefox, or Edge)

### Installation

1. **Clone or download this repository**

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure your credentials**

Edit `config.py` with your API keys:
```python
# Agora Credentials
CUSTOMER_KEY = "your_customer_key"
CUSTOMER_SECRET = "your_customer_secret"
APP_ID = "your_app_id"
AGORA_TEMP_TOKEN = "your_token"

# 3rd Party Services
ASSEMBLY_AI_KEY = "your_assemblyai_key"
GROQ_KEY = "your_groq_key"
TTS_GROQ_KEY = "your_tts_groq_key"
```

⚠️ **Never commit real credentials to public repositories!**

---

## 💡 Usage

### Basic Mode (Without RAG)

For simple testing without custom knowledge:

**1. Start the AI Agent**
```bash
python join_api.py
```

Expected output:
```
==================================================
🚀 Starting AI Agent
==================================================
Channel: test
Agent UID: 1001
User UID: 1002
RAG Mode: DISABLED ❌
==================================================

📊 Response:
--------------------------------------------------
Status Code: 200

✅ SUCCESS!
Agent ID: A42AF84CR35WK42LF89KY44XD97RD25R
Status: RUNNING
Created: 1765274979

==================================================
⚠️  SAVE THIS AGENT ID FOR STOPPING:
   A42AF84CR35WK42LF89KY44XD97RD25R
==================================================
```

⚠️ **Important:** Copy and save the `Agent ID`!

**2. Open the Web Interface**
- Double-click `index.html` to open in your browser
- Click **"Start Conversation"**
- Allow microphone access when prompted
- Start talking! 🎤

**3. Stop the Agent**

When finished:
- Click **"Stop Conversation"** in the browser
- Edit `stop_api.py` and paste your Agent ID:
```python
AGENT_ID = "A42AF84CR35WK42LF89KY44XD97RD25R"  # Paste your ID here
```
- Run:
```bash
python stop_api.py
```

---

### RAG Mode (With Custom Knowledge Base)

To use your own knowledge base (recommended for production):

#### Step 1: Customize Your Knowledge Base

Edit `my_city_info.txt` with your information:
```
Your Business Name - Complete Guide

Overview
Welcome to [Your Business]...

Location Information
[Describe locations, services, etc.]

Frequently Asked Questions

Q: Where is [location]?
A: [Clear answer with directions]
```

**Tips for effective knowledge bases:**
- Use clear headings and sections
- Include FAQ format (Q: ... A: ...)
- Provide specific floor/location information
- Include operating hours and contact info
- Use keywords users might search for

#### Step 2: Set Up ngrok (For Cloud Connectivity)

Your RAG server needs to be accessible from Agora's cloud servers:

**Install ngrok:**
- Download from [ngrok.com](https://ngrok.com/download)
- Or use: `brew install ngrok` (Mac) / `choco install ngrok` (Windows)

**Start ngrok tunnel:**
```bash
ngrok http 8000
```

You'll see output like:
```
Forwarding  https://abc123-xyz.ngrok.io -> http://localhost:8000
```

⚠️ **Copy the HTTPS URL!** (e.g., `https://abc123-xyz.ngrok.io`)

#### Step 3: Update RAG Configuration

Edit `join_api.py` (line 35):
```python
# Change from:
RAG_SERVER_URL = "http://localhost:8000/rag/chat/completions"

# To (use YOUR ngrok URL):
RAG_SERVER_URL = "https://abc123-xyz.ngrok.io/rag/chat/completions"
```

Also set:
```python
USE_RAG = True  # Enable RAG mode
```

#### Step 4: Start RAG Server

**Terminal 1 - RAG Server:**
```bash
python rag_server.py
```

Expected output:
```
==================================================
🚀 Starting RAG Server - Mall Guide Edition
==================================================
📚 Knowledge Base: ./my_city_info.txt
✅ Knowledge base found: 6304 bytes
🌐 Endpoints:
   - http://localhost:8000
   - http://localhost:8000/health
   - http://localhost:8000/rag/chat/completions
==================================================
```

**Terminal 2 - ngrok (if using RAG):**
```bash
ngrok http 8000
```

**Terminal 3 - Start Agent:**
```bash
python join_api.py
```

Look for:
```
RAG Mode: ENABLED ✅
RAG Server: https://your-ngrok-url.ngrok.io/rag/chat/completions

💡 RAG is ACTIVE!
   The AI will answer based on my_city_info.txt
```

**Terminal 4 - Open Browser:**
- Open `index.html`
- Click "Start Conversation"
- Ask questions about your knowledge base!

---

## 🧪 Testing

### Test RAG Responses (Without Voice)

```bash
python test_rag.py
```

This will test 12 common queries and show responses.

### Diagnose Issues

```bash
python diagnose_rag.py
```

Checks:
- ✅ Knowledge base file exists
- ✅ RAG server is running
- ✅ Groq API is working
- ✅ Can process queries

---

## 🛠️ Troubleshooting

### Issue: "Wait for a moment" repeats forever

**Cause:** RAG server not accessible from Agora

**Solution:**
1. Make sure ngrok is running: `ngrok http 8000`
2. Update `RAG_SERVER_URL` in `join_api.py` with ngrok HTTPS URL
3. Restart the agent: `python join_api.py`

### Issue: RAG server not receiving requests

**Cause:** Using `localhost` instead of public URL

**Solution:**
- Always use ngrok URL (https://...) in `join_api.py`
- Test with: `curl https://your-ngrok-url.ngrok.io/health`

### Issue: Empty or wrong responses

**Cause:** Knowledge base not loading or search not finding content

**Solution:**
1. Check `my_city_info.txt` exists and has content
2. Run `python diagnose_rag.py` to verify
3. Check RAG server logs for "Retrieved context length: 0"
4. Add more keywords to your knowledge base

### Issue: Groq API errors

**Cause:** Invalid API key or rate limits

**Solution:**
1. Verify API key at [console.groq.com](https://console.groq.com/)
2. Try different model in `config.py`:
```python
LLM_MODEL = "llama-3.3-70b-versatile"  # or "mixtral-8x7b-32768"
```

---


## 📊 Architecture

```
User Voice Input
      ↓
  Agora RTC (Audio Stream)
      ↓
  AssemblyAI (Speech-to-Text)
      ↓
  Your RAG Server (localhost or ngrok/cloud)
      ↓
  Search my_city_info.txt for relevant info
      ↓
  Groq LLM (Generate response with context)
      ↓
  Groq TTS (Text-to-Speech)
      ↓
  Agora RTC (Audio Stream)
      ↓
User Hears AI Response
```

---

## 🔑 Environment Variables (Optional)

For better security, use environment variables:

Create `.env` file:
```bash
AGORA_APP_ID=your_app_id
AGORA_TOKEN=your_token
GROQ_API_KEY=your_groq_key
ASSEMBLYAI_KEY=your_assemblyai_key
```

Update `config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("AGORA_APP_ID")
AGORA_TEMP_TOKEN = os.getenv("AGORA_TOKEN")
# etc...
```

Install python-dotenv:
```bash
pip install python-dotenv
```

---

## 📚 API Keys - Where to Get Them

| Service | Purpose | Free Tier | Get Key |
|---------|---------|-----------|---------|
| **Agora** | Real-time voice | 10,000 mins/month | [console.agora.io](https://console.agora.io/) |
| **Groq** | LLM & TTS | Limited free | [console.groq.com](https://console.groq.com/) |
| **AssemblyAI** | Speech-to-Text | Limited free | [assemblyai.com](https://www.assemblyai.com/) |
| **ngrok** | Public tunnel | Free with limits | [ngrok.com](https://ngrok.com/) |

---

## 🎨 Customization Examples

### Example 1: Hotel Concierge

`my_city_info.txt`:
```
Grand Hotel - Guest Information

Check-in/Check-out
Check-in: 3:00 PM
Check-out: 11:00 AM

Dining
Main Restaurant - Ground Floor
Hours: 6:30 AM - 10:00 PM
Specialty: International cuisine

Room Service
Available 24/7
Dial extension 100 from your room

Frequently Asked Questions

Q: What time is breakfast?
A: Breakfast is served from 6:30 AM to 10:30 AM in the main restaurant on the ground floor.
```

### Example 2: Museum Guide

```
City Museum - Visitor Guide

Permanent Exhibitions

Ancient Artifacts - Second Floor
Featuring pottery, tools, and jewelry from 3000 BC
Hours: 9:00 AM - 5:00 PM

Modern Art Gallery - Third Floor
Contemporary works from local artists
Hours: 9:00 AM - 5:00 PM
```



---

## 🎓 Learning Resources

- [Agora Conversational AI Docs](https://docs.agora.io/en/conversational-ai/overview/product-overview)
- [RAG Implementation Guide](https://docs.agora.io/en/conversational-ai/develop/custom-llm)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Groq Documentation](https://console.groq.com/docs)

---

**Made with ❤️ for building better voice AI experiences**

*Star ⭐ this repo if you found it helpful!*
