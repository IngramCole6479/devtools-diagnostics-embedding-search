import argparse

from src.devtools_service import BuildEvent, DevtoolsSearch, ReleaseOperation, sample_documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Search build and release diagnostics")
    parser.add_argument("query", help="diagnostic question")
    args = parser.parse_args()
    service = DevtoolsSearch(sample_documents())
    answer = service.answer(
        BuildEvent("abc123", "failed", "dependency lock changed"),
        ReleaseOperation("2026.09.1", "staging", "restore the previous image digest"),
        args.query,
    )
    print(answer)


if __name__ == "__main__":
    main()
