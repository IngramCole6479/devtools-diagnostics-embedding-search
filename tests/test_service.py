from types import SimpleNamespace

from src.devtools_service import DiagnosticDocument, DevtoolsSearch, cosine_similarity


class FakeEmbeddings:
    def create(self, *, model, input):
        return SimpleNamespace(data=[SimpleNamespace(embedding=[1.0, 0.0])])


class FakeClient:
    embeddings = FakeEmbeddings()


def test_search_prefers_build_note_for_build_query():
    docs = [
        DiagnosticDocument("build", "cache", [1.0, 0.0]),
        DiagnosticDocument("release", "rollback", [0.0, 1.0]),
    ]
    result = DevtoolsSearch(docs, FakeClient()).search("why did the build fail")
    assert result[0].title == "build"
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0
