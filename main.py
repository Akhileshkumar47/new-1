
from dialogue_manager import DialogueManager

def run():
    print("Bank Chatbot 🤖 — type 'exit' to quit")
    dm = DialogueManager()
    while True:
        try:
            msg = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if msg.lower() in {"exit", "quit"}:
            print("Bye!")
            break
        reply = dm.handle(msg)
        print("Chatbot:", reply["text"])
        # Debug line to show NLU result (comment out for clean demo)
        # print("   NLU:", reply["nlu"])

if __name__ == "__main__":
    run()
