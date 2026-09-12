if __name__ == "__main__":
    print("=" * 40)
    print("JARVIS AGENT READY. Type your query below.")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 40)

    while True:
        try:
            user_input = input("\nYou: ")
            if not user_input.strip():
                continue
            if user_input.lower().strip() in ["exit", "quit"]:
                print("JARVIS: Goodbye!")
                break

            run_agent(user_input)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
