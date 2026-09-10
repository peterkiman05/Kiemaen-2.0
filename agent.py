import os, math, time, requests

API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable is not set.")
    exit(1)

# 1. Fetch available models from Google API
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
res = requests.get(list_url)

if res.status_code != 200:
    print(f"Error listing models ({res.status_code}): {res.text}")
    exit(1)

models_data = res.json().get('models', [])
target_model = None

# Find the first model that supports content generation
for m in models_data:
    if "generateContent" in m.get("supportedGenerationMethods", []):
        target_model = m['name'] # Format: models/model-name
        break

if not target_model:
    print("No generateContent models found for this API key.")
    exit(1)

print(f"--> Using detected model: {target_model}")

# 2. Build Payload
LOCAL_KNOWLEDGE = {
    "Project Pegasus": "Server IP: 192.168.1.150, Port: 8080",
    "Database Config": "Primary DB: PostgreSQL, Secret Key: HYDRA_8891_SEC"
}

ip_data = LOCAL_KNOWLEDGE["Project Pegasus"]
number = 150
sqrt_val = math.sqrt(number)

prompt = (
    f"Private Docs Check: {ip_data}.\n"
    f"Calculated square root of target value ({number}): {sqrt_val:.4f}.\n"
    f"Summarize this system data cleanly."
)

# 3. Call Model with Automatic Quota Retry
url = f"https://generativelanguage.googleapis.com/v1beta/{target_model}:generateContent?key={API_KEY}"
headers = {"Content-Type": "application/json"}
payload = {"contents": [{"parts": [{"text": prompt}]}]}

max_retries = 3
for attempt in range(max_retries):
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        res_json = response.json()
        print("\nAI Agent Response:\n" + "="*40)
        print(res_json['candidates'][0]['content']['parts'][0]['text'])
        break
    elif response.status_code == 429:
        print(f"Rate limit hit (429). Waiting 35s for free tier cooldown... (Attempt {attempt + 1}/{max_retries})")
        time.sleep(35)
    else:
        print(f"\nError {response.status_code}: {response.text}")
        break
