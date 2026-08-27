## Task Overview

This project is a recruiting assistant that answers questions about candidates using resumes and interview guides stored in a pgvector-backed knowledge base. The current workflow can return confident answers from weak or incorrectly scoped evidence, which makes recruiter-facing summaries risky. Repeated source updates can also make retrieval quality worse over time, and sensitive contact details may appear in stored or returned content. Your work is to improve the RAG flow so candidate answers remain grounded, private, and operationally reliable.

## Objectives

- Keep repeated document updates from degrading retrieval quality.
- Return grounded answers when supporting candidate evidence exists.
- Avoid exposing sensitive source content in user-facing responses.
- Refuse answers when the knowledge base lacks reliable evidence.

## Helpful Tips

- Review how source text moves from documents into retrieved answer context.
- Analyze whether recruiter constraints survive every stage of retrieval.
- Consider how repeated updates affect stored evidence and ranking behavior.
- Think about what should happen when the best evidence is weak or unrelated.
- Explore how citations and public responses should reflect retrieved sources.

## How to Verify

> [!NOTE]
> Copy `.env.example` to `.env` and set your provider key. The invariant tests run offline and need no key; only the end-to-end run does.

- Run the invariant tests and confirm repeated ingestion keeps stable evidence counts.
- Verify scoped candidate questions retrieve only evidence for the requested candidate.
- Check unsupported questions return the documented refusal shape with no citations.
- Confirm public answers and stored chunks do not expose raw contact details.
- Run an end-to-end question and inspect that citations match the retrieved evidence.
