from __future__ import annotations

import argparse
import json

from app.db import ensure_database_ready
from app.generation import answer_question
from app.ingestion import ingest_documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the recruiter RAG assistant")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("ingest")

    ask_parser = subparsers.add_parser("ask")
    ask_parser.add_argument("question")
    ask_parser.add_argument("--candidate-id")
    ask_parser.add_argument("--document-type")

    args = parser.parse_args()
    ensure_database_ready()

    if args.command == "ingest":
        count = ingest_documents()
        print(json.dumps({"chunks_ingested": count}, indent=2))
        return

    filters = {}
    if args.candidate_id:
        filters["candidate_id"] = args.candidate_id
    if args.document_type:
        filters["document_type"] = args.document_type
    print(json.dumps(answer_question(args.question, filters=filters), indent=2))


if __name__ == "__main__":
    main()
