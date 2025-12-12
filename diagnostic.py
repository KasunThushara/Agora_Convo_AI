"""
Diagnostic tool for RAG server
Helps identify issues with the RAG setup
"""

import requests
import json
import os
import sys


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def check_file(filepath):
    """Check if file exists and is readable"""
    print(f"\n📁 Checking file: {filepath}")

    if not os.path.exists(filepath):
        print(f"❌ File NOT found!")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Files in current directory:")
        for f in os.listdir('.'):
            print(f"     - {f}")
        return False

    print(f"✅ File exists")

    try:
        size = os.path.getsize(filepath)
        print(f"✅ File size: {size} bytes")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ File readable: {len(content)} characters")
        print(f"\nFirst 200 characters:")
        print("-" * 60)
        print(content[:200])
        print("-" * 60)
        return True
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False


def check_server():
    """Check if RAG server is running"""
    print("\n🌐 Checking RAG server...")

    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is running!")
            print(f"   Status: {data.get('status')}")
            print(f"   Knowledge base loaded: {data.get('knowledge_base_loaded')}")
            print(f"   Knowledge base size: {data.get('knowledge_base_size')} bytes")
            print(f"   Groq API configured: {data.get('groq_api_configured')}")
            return True
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("   Make sure to run: python rag_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_simple_query():
    """Test a simple query"""
    print("\n🧪 Testing simple query...")

    query = "Where is the coffee shop?"
    print(f"Question: {query}")

    try:
        response = requests.post(
            "http://localhost:8000/rag/chat/completions",
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": query}],
                "stream": True
            },
            stream=True,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Server returned status: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        print("\n📡 Streaming response:")
        print("-" * 60)

        full_answer = ""
        chunk_count = 0

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]

                    if data_str == '[DONE]':
                        break

                    try:
                        chunk = json.loads(data_str)
                        chunk_count += 1

                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                print(content, end='', flush=True)
                                full_answer += content
                    except json.JSONDecodeError as e:
                        print(f"\n⚠️ JSON decode error: {e}")
                        print(f"   Data: {data_str[:100]}")

        print("\n" + "-" * 60)
        print(f"\n✅ Received {chunk_count} chunks")
        print(f"✅ Total response length: {len(full_answer)} characters")

        if not full_answer or len(full_answer) < 10:
            print("⚠️ WARNING: Response is very short or empty!")
            return False

        return True

    except requests.exceptions.Timeout:
        print("❌ Request timeout! Server is taking too long to respond.")
        print("   This might indicate:")
        print("   1. Groq API key is invalid")
        print("   2. Network issues")
        print("   3. Server is stuck")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_groq_key():
    """Check if Groq API key is valid"""
    print("\n🔑 Checking Groq API key...")

    # Read from rag_server.py
    try:
        with open('rag_server.py', 'r') as f:
            content = f.read()
            if 'GROQ_API_KEY' in content:
                print("✅ GROQ_API_KEY found in rag_server.py")

                # Extract key (simple check)
                if 'gsk_' in content:
                    print("✅ Key starts with 'gsk_' (correct format)")
                else:
                    print("❌ Key doesn't start with 'gsk_'")
                    return False
            else:
                print("❌ GROQ_API_KEY not found in rag_server.py")
                return False
    except Exception as e:
        print(f"❌ Error reading rag_server.py: {e}")
        return False

    # Try a direct test
    try:
        from openai import AsyncOpenAI
        import asyncio

        async def test_groq():
            client = AsyncOpenAI(
                api_key="xxxxxxxxxxx",
                base_url="https://api.groq.com/openai/v1"
            )

            response = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Say 'test'"}],
                stream=False,
                max_tokens=10
            )
            return response

        print("🧪 Testing Groq API directly...")
        result = asyncio.run(test_groq())
        print("✅ Groq API is working!")
        return True

    except Exception as e:
        print(f"❌ Groq API test failed: {e}")
        print("   Your API key might be invalid or expired")
        return False


def main():
    print("\n" + "=" * 60)
    print("🔍 RAG SERVER DIAGNOSTIC TOOL")
    print("=" * 60)

    issues = []

    # Check 1: File exists
    print_section("Check 1: Knowledge Base File")
    if not check_file("my_city_info.txt"):
        issues.append("Knowledge base file missing or unreadable")

    # Check 2: Server running
    print_section("Check 2: RAG Server Status")
    if not check_server():
        issues.append("RAG server not running or not responding")
        print("\n⚠️ Cannot continue without server. Start it with:")
        print("   python rag_server.py")
        sys.exit(1)

    # Check 3: Groq API key
    print_section("Check 3: Groq API Key")
    if not check_groq_key():
        issues.append("Groq API key issue")

    # Check 4: Test query
    print_section("Check 4: Test Query")
    if not test_simple_query():
        issues.append("Query test failed")

    # Summary
    print("\n" + "=" * 60)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 60)

    if not issues:
        print("\n✅ ALL CHECKS PASSED!")
        print("Your RAG server appears to be working correctly.")
    else:
        print("\n⚠️ ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")

        print("\n💡 SOLUTIONS:")
        if "Knowledge base file" in str(issues):
            print("   - Make sure my_city_info.txt is in the same folder as rag_server.py")
        if "RAG server" in str(issues):
            print("   - Run: python rag_server.py")
        if "Groq API key" in str(issues):
            print("   - Check your Groq API key is valid")
            print("   - Get a new key from: https://console.groq.com")
        if "Query test" in str(issues):
            print("   - Check the RAG server terminal for error messages")
            print("   - Make sure Groq API key is working")

    print("=" * 60)


if __name__ == "__main__":
    main()
