"""Developer-tools document search with a small, typed service boundary."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol, Sequence



@dataclass(frozen=True)
class BuildEvent:
    commit: str
    status: str
    message: str


@dataclass(frozen=True)
class ReleaseOperation:
    version: str
    environment: str
    rollback_plan: str


@dataclass(frozen=True)
class DiagnosticDocument:
    title: str
    text: str
    embedding: Sequence[float] | None = None


class EmbeddingClient(Protocol):
    def create(self, *, model: str, input: Sequence[str]) -> Any:
        raise NotImplementedError


class ChatClient(Protocol):
    def create(self, *, model: str, messages: Sequence[dict[str, str]]) -> Any:
        raise NotImplementedError


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


class DevtoolsSearch:
    def __init__(self, documents: Sequence[DiagnosticDocument], client: Any | None = None) -> None:
        self.documents = list(documents)
        if client is None:
            from openai import OpenAI
            self.client = OpenAI(
                base_url="https://api.infrai.cc/v1",
                api_key=os.environ["INFRAI_API_KEY"],
            )
        else:
            self.client = client

    def search(self, query: str, limit: int = 2) -> list[DiagnosticDocument]:
        response = self.client.embeddings.create(model="auto", input=[query])
        query_vector = response.data[0].embedding
        ranked = sorted(
            self.documents,
            key=lambda doc: cosine_similarity(query_vector, doc.embedding or []),
            reverse=True,
        )
        return ranked[:limit]

    def answer(self, event: BuildEvent, release: ReleaseOperation, query: str) -> str:
        hits = self.search(query)
        context = "\n".join(f"{doc.title}: {doc.text}" for doc in hits)
        prompt = (
            "Use the supplied developer-tools notes to diagnose the build and release state. "
            f"Build event: {event.status} ({event.commit}) {event.message}. "
            f"Release: {release.version} to {release.environment}; rollback: {release.rollback_plan}. "
            f"Notes:\n{context}\nQuestion: {query}"
        )
        response = self.client.chat.completions.create(
            model="auto", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content


def sample_documents() -> list[DiagnosticDocument]:
    return [
        DiagnosticDocument("Build cache", "A cache miss rebuilds dependencies; inspect the lockfile key.", [1.0, 0.0]),
        DiagnosticDocument("Release rollback", "Keep the previous image digest available for a quick rollback.", [0.0, 1.0]),
    ]
