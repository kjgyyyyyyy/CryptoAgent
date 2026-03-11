from __future__ import annotations

import argparse

from .pipeline import run_agent


def main() -> None:
    parser = argparse.ArgumentParser(description="ETH/BMNR CryptoAgent MVP")
    parser.add_argument("query", help="사용자 요청 문장")
    args = parser.parse_args()

    print(run_agent(args.query))


if __name__ == "__main__":
    main()
