# Configuration

The runtime source is [`config/settings.yaml`](../config/settings.yaml).
Environment variables override secrets and operational limits.

| Setting | Purpose |
| --- | --- |
| `gauss.home` / `GAUSS_HOME` | SQLite state, exported artifacts, and logs |
| `gauss.default_model` | Not read at runtime: `docs/pin_audit.py` cross-checks it against `hermes.model` |
| Lean verification | Not settings-driven: a fixed full-mode pipeline stage (`Gauss Sessions`); catalogue mode never verifies. `FEP_LEAN_VERIFY_TIMEOUT` bounds it |
| `output.root` | Generated figures and reports root |
| `hermes.model` | Primary Hermes model (`HERMES_MODEL` env overrides it; `GAUSS_DEFAULT_MODEL` env is the fallback when the yaml has no `model:` — `HermesConfig.from_settings`, `src/fep_lean/llm/hermes.py:308-311`) |
| `hermes.fallback_models` | Ordered configured model chain; `HERMES_FALLBACK_MODELS` supplies a strict nonempty JSON list of exact model names |
| `hermes.timeout_s` | Request deadline |
| `hermes.cache_ttl_hours` | SQLite response-cache lifetime |

Important environment variables include `OPENROUTER_API_KEY`,
`ANTHROPIC_API_KEY`, `HERMES_API_BASE`, `HERMES_MODEL`, `HERMES_FALLBACK_MODELS`,
`FEP_LEAN_LAKE_EXE`, `FEP_LEAN_LEAN_EXE`, `FEP_LEAN_VERIFY_TIMEOUT`,
`FEP_LEAN_MAX_TOPICS`, and `FEP_LEAN_OUTPUT_ROOT`.

`fep-lean preflight` performs no download, build, database write, or report
write. Use `fep-lean setup` when dependency acquisition is required.

For primary-only execution, set `HERMES_FALLBACK_MODELS` to a JSON list
containing only the primary model. An absent override preserves the configured
chain; an empty or malformed list rejects. `HermesConfig.runtime_policy()`
projects a safe allowlist of configured nonsecret settings. It does not freeze
retry/attempt limits; record `HERMES_NETWORK_MAX_RETRIES`,
`HERMES_429_MAX_RETRIES` and `HERMES_MAX_MODEL_ATTEMPTS` separately when capturing
an execution policy. OpenRouter batch variants require the asynchronous Batch
API and must not be treated as synchronous fallback completions.
