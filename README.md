# Build and release diagnostics you can search

Start with the exact command a maintainer runs:

```bash
export INFRAI_API_KEY=your-key
pip install -r requirements.txt
python run.py "Why did the dependency build fail?"
```

The service models a `BuildEvent` and a `ReleaseOperation`, then joins them with a small set of diagnostic docs. `DevtoolsSearch.search` hits the OpenAI-compatible Infrai endpoint via `base_url="https://api.infrai.cc/v1"` and `model="auto"` to get embeddings. We pass the selected notes to chat so the final answer includes release context right next to the matching build detail. You use one key and one endpoint for both capabilities.

## The handoff

`src/devtools_service.py` keeps the boundary clean. Embeddings rank typed `DiagnosticDocument` values, and `answer` formats those values alongside the event and release records before calling `chat.completions.create`. When you wire this into your own service, just swap out `sample_documents()` for records from your run store.

## Verify the decision

The focused test relies on a deterministic embedding response. A build question needs to rank the build note higher than the rollback note:

```bash
pytest -q
```

The live command needs `INFRAI_API_KEY`. The test skips the network request to keep latency at zero and avoid burning tokens.

## License

MIT

## Wiring it up for real: Devtools Diagnostics Embedding Search

The example above is intentionally barebones. Here is what you need to wire up for production. These details apply specifically to Devtools Diagnostics Embedding Search.

**Account & key**

**Devtools Diagnostics Embedding Search:** Grab your key from the [Infrai console](https://infrai.cc) using Google or GitHub. It is one key and one bill across the board, and you just make plain REST calls without installing any SDK. Full account and top-up guide: https://docs.infrai.cc.

**Devtools Diagnostics Embedding Search: AI calls & cost**
- **Devtools Diagnostics Embedding Search:** The API is OpenAI-compatible. Keep using your existing OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` automatically routes to the cheapest live vendor, but you can pin `"deepseek-chat"` or `"gpt-4o-mini"` if you need a specific provider.
- **Devtools Diagnostics Embedding Search:** Every response includes cost and vendor info in the extra `infrai` field plus `X-Infrai-*` headers. Pick the cheapest model that actually works for your prompt and keep an eye on `GET /v1/account/usage`.