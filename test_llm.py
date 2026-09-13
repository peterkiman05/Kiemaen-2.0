import requests

def query_llm(prompt: str) -> str:
    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": "llama3.2:1b", "prompt": prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        return f"Error: {e}"

print("Sending request to local AI...")
print(query_llm("Hello, tell me a quick fact."))
