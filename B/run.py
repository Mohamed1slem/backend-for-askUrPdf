import argparse
from src.chatbot import answer_query
from src.ingest import main as ingest_main

def run_ingest():
    ingest_main()

def run_chat():
    print("RAG Chatbot (DeepSeek). Type your question (Ctrl+C to exit).")
    try:
        while True:
            q = input("\n> ").strip()
            if not q:
                continue
            ans = answer_query(q)
            print(f"\n{ans}")
    except KeyboardInterrupt:
        print("\nBye.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG Chatbot with DeepSeek")
    parser.add_argument("--ingest", action="store_true", help="Build embeddings index from cleaned_docs")
    args = parser.parse_args()

    if args.ingest:
        run_ingest()
    else:
        run_chat()
