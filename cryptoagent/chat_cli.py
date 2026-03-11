from __future__ import annotations

from .chat import ChatSession


def main() -> None:
    session = ChatSession()
    print("CryptoAgent Chat (종료: /exit)")
    while True:
        try:
            query = input("\nYou> ").strip()
        except EOFError:
            break

        if not query:
            continue
        if query.lower() in {"/exit", "exit", "quit"}:
            print("Bye.")
            break

        answer = session.ask(query)
        print(f"\nAgent>\n{answer}")


if __name__ == "__main__":
    main()
