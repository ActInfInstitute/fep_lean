# OpenGauss and SQLite

Full mode requires the `gauss` executable and a successful isolated local
`gauss --version` probe. This establishes CLI availability only. The probe uses
a fresh temporary `GAUSS_HOME`, disabled update checks and disabled dotenv
loading; automatic preflight
does not run `doctor`, which can read or refresh managed account credentials.
Provider configuration, writable session storage and pinned Lean capabilities
remain separate required full-mode checks.
`OpenGaussClient` is the local SQLite persistence layer used for sessions,
turns, response cache entries, artifacts, and operation logs.

State is stored under `GAUSS_HOME` (default `~/.gauss`). Artifact publication is
atomic and database rows include the exported file hash. Use a temporary
`GAUSS_HOME` for isolated development and inspect `get_stats()` before cleanup.
