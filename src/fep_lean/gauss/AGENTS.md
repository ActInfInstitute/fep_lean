# `fep_lean.gauss` contract

- `cli.py` owns the bounded, isolated local `gauss --version` probe and explicit
  required/advisory behavior. Do not automatically run upstream `doctor` or
  infer provider/session health from CLI availability.
- `client.py` exclusively owns SQLite schema, transactions, sessions, turns,
  artifacts, logs, and cache rows.
- `runner.py` composes Hermes and `LeanVerifier` into per-topic results; it must
  close sessions and preserve error evidence on every exit path.

Full mode is strict. Do not restore the removed
`FEP_LEAN_GAUSS_WORKFLOWS` pseudo-gate or silently downgrade workflows. Offline
behavior belongs to pipeline `catalogue` mode. Provider success, original-body
fallback, refined-body compilation, native compilation, and full result
completion are separate facts.

```python
from fep_lean.gauss import (
    GaussRunner,
    OpenGaussClient,
    SessionRecord,
    TopicRunResult,
    check_gauss_cli,
)
```

Use temporary `GAUSS_HOME` directories in tests. Never contact a provider or a
user database unless a live test or full run explicitly requests it.

See [README.md](README.md), [../llm/AGENTS.md](../llm/AGENTS.md), and
[../verification/AGENTS.md](../verification/AGENTS.md).
