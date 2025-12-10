
# Agora_Convo_AI

A simple project to create and manage an AI voice agent using Agora and a browser-based conversation UI.

---

## 🚀 How to Use

### Step 1: Configure

Edit `config.py` and add your credentials:

```python
APP_ID = "your_app_id_here"
AGORA_TEMP_TOKEN = "your_token_here"
# ... other settings
````

---

### Step 2: Start AI Agent

Run the join API script:

```bash
python join_api.py
```

You should see output like this:

```
==================================================
🚀 Starting AI Agent...
==================================================
Channel: test
Agent UID: 1001
User UID: 1002
==================================================

✅ SUCCESS!
Agent ID: A42AF84CR35WK42LF89KY44XD97RD25R
Status: RUNNING
```

⚠️ **Important:** Save the `Agent ID` — you will need it to stop the agent later.

---

### Step 3: Open the Web App

1. Double-click `index.html`
2. (Optional) Click **Show Configuration** to check settings
3. (Optional) Click **Test Configuration** to validate
4. Click **Start Conversation**
5. Allow microphone access
6. Start talking 🎤

---

### Step 4: Stop the AI Agent

1. Click **Stop Conversation** in the browser
2. Edit `stop_api.py` and paste your Agent ID:

```python
AGENT_ID = "A42AF84CR35WK42LF89KY44XD97RD25R"
```

3. Run:

```bash
python stop_api.py
```

---

## 📁 Project Structure

```
.
├── config.py
├── join_api.py
├── stop_api.py
├── index.html
└── README.md
```

---

## ✅ Requirements

* Python 3.8+
* An Agora App ID and Token
* A modern web browser (Chrome, Edge, Firefox)

---

## 📝 Notes

* Always keep your App ID and Token private.
* Do not commit real credentials to public repositories.

---

