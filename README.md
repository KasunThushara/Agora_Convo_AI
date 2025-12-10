# Agora_Convo_AI

🚀 How to Use
Step 1: Configure
Edit config.py with your credentials:
pythonAPP_ID = "your_app_id_here"
AGORA_TEMP_TOKEN = "your_token_here"
# ... etc
Step 2: Start AI Agent
bashpython join_api.py
Output:
==================================================
🚀 Starting AI Agent...
==================================================
Channel: test
Agent UID: 1001
User UID: 1002
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

✨ You can now open index.html and click 'Start Conversation'
Step 3: Open Web App

Double-click index.html
(Optional) Click "Show Configuration" to verify settings
(Optional) Click "Test Configuration" to validate
Click "Start Conversation"
Allow microphone access
Start talking!

Step 4: Stop AI Agent

Click "Stop Conversation" in browser
Edit stop_api.py and paste the agent ID:

python   AGENT_ID = "A42AF84CR35WK42LF89KY44XD97RD25R"  # Paste here

Run:

bash   python stop_api.py
