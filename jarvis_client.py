import requests, json, os

SERVER_URL = "https://jarvis-backend-cx62.onrender.com"
HISTORY_FILE = "history.json"


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_history(history):
    trimmed_history = history[-10:]
    with open(HISTORY_FILE, "w") as f:
        json.dump(trimmed_history, f)


def main():
    history = load_history()
    print("=== JARVIS AI ONLINE (Type 'reset' to clear memory, 'exit' to quit) ===")

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print("JARVIS: Goodbye!")
            break

        if user_input.lower() == "reset":
            history = []
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
            print("JARVIS: Conversation memory reset.")
            continue

        payload = {"message": user_input, "history": history}

        try:
            # 60 second timeout allows Render time to wake up from sleep
            response = requests.post(f"{SERVER_URL}/chat", json=payload, timeout=60)
            data = response.json()

            if "reply" in data:
                reply = data["reply"]
                print(f"JARVIS: {reply}")

                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": reply})
                save_history(history)
            else:
                print("Error from server:", data)

        except Exception as e:
            print(f"Connection failed: {str(e)}")


if __name__ == "__main__":
    main()
