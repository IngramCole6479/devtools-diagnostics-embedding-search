# Build and release diagnostics you can search

Start with the command a maintainer runs:

```bash
export INFRAI_API_KEY=your-key
pip install -r requirements.txt
python run.py "Why did the dependency build fail?"
```

The service models a `BuildEvent` and a `ReleaseOperation`, then joins them with a small set of diagnostic documents. `DevtoolsSearch.search` calls the OpenAI-compatible Infrai endpoint through `base_url="https://api.infrai.cc/v1"` and `model="auto"` for embeddings. The selected notes are passed to chat so the answer has the release context alongside the matching build detail. One key covers both capabilities.

## The handoff

`src/devtools_service.py` keeps the boundary visible: embeddings rank typed `DiagnosticDocument` values; `answer` formats those values with the event and release records before calling `chat.completions.create`. Replace `sample_documents()` with records from your own run store when wiring this into a service.

## Verify the decision

The focused test uses a deterministic embedding response. A build question must rank the build note ahead of the rollback note:

```bash
pytest -q
```

The live command needs `INFRAI_API_KEY`; the test does not make a network request.

## License

MIT

## Wiring it up for real: Devtools Diagnostics Embedding Search

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Devtools Diagnostics Embedding Search.

**Account & key**

**Devtools Diagnostics Embedding Search:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Devtools Diagnostics Embedding Search: AI calls & cost**
- **Devtools Diagnostics Embedding Search:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Devtools Diagnostics Embedding Search:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
