import subprocess, json, sys


def listen():
    print("\nListening... (Speak now)")
    # Uses Android speech recognition via Termux API
    res = subprocess.run(["termux-speech-to-text"], capture_output=True, text=True)
    text = res.stdout.strip()
    if text:
        print(f"You said: {text}")
        return text
    print("Could not hear anything.")
    return None


def speak(text):
    # Uses Android Text-To-Speech engine
    clean_text = text.replace('"', "").replace("'", "")
    subprocess.run(["termux-tts-speak", clean_text])


def ask_ollama(prompt):
    payload = json.dumps({"model": "jarvis", "prompt": prompt, "stream": False})

    cmd = [
        "curl",
        "-s",
        "-X",
        "POST",
        "http://localhost:11434/api/generate",
        "-d",
        payload,
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(res.stdout)
        return data.get("response", "")
    except Exception as e:
        return f"Error connecting to model: {e}"


def main():
    speak("Jarvis online and ready.")
    while True:
        user_input = listen()
        if not user_input:
            continue

        if "exit" in user_input.lower() or "stop" in user_input.lower():
            speak("Shutting down.")
            break

        print("Thinking...")
        reply = ask_ollama(user_input)
        print(f"JARVIS: {reply}")
        speak(reply)


if __name__ == "__main__":
    main()
