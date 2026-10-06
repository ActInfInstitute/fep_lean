# Release procedure

A versioned release is a tagged, hosted-CI-green `main` commit with one
consistent version. The gate is short on purpose: it checks what a release
actually ships, and it is fully checked by
[`scripts/release_check.py`](../scripts/release_check.py).

## Release gate

| Requirement | Checked by |
| --- | --- |
| One version across `pyproject.toml`, `src/fep_lean/__init__.py`, `CITATION.cff`, `manuscript/config.yaml`, `config/settings.yaml`, `uv.lock` and the release-bundle constants | `release_check.py` |
| One release date across `CITATION.cff`, `manuscript/config.yaml` and the release-bundle constants | `release_check.py` |
| A `## X.Y.Z — YYYY-MM-DD — title` section in `CHANGELOG.md` | `release_check.py` |
| Clean working tree; `HEAD` equals `origin/main` | `release_check.py --hosted` |
| The newest hosted `ci.yml` run on that exact commit succeeded (Python, distribution matrix, Lean, render) | `release_check.py --hosted` |

## What does not block a release

Research and evidence lanes stay in [`TODO.md`](../TODO.md) with their own
acceptance probes. They are reported honestly in release notes, never claimed:

- the frozen H3 study (export, single primary run, outcome reviews);
- full seven-stage publication capture and two-archive parity;
- the installed-wheel runtime matrix and read-only status controls;
- Q7 generated-runner execution and GNN bridge work;
- optional provider (Hermes/OpenGauss) runs;
- the nine-criterion closure audit.

A release changes no scientific claim. Unrun lanes stay described as unrun.

## Steps

1. Bump the version and date in every file listed above, add the dated
   `CHANGELOG.md` section, and run `uv lock`.
2. `uv run python scripts/release_check.py` — fix every reported mismatch.
3. Run the local suite and audits (see [development](development.md)), commit
   and push to `main`.
4. Wait for hosted CI on that commit, then
   `uv run python scripts/release_check.py --hosted --notes /tmp/notes.md`.
5. Build distributions from the same commit: `uv build`.
6. Tag and publish:

   ```bash
   git tag -a vX.Y.Z -m "fep_lean vX.Y.Z" && git push origin vX.Y.Z
   gh release create vX.Y.Z dist/* --title "FEP_Lean vX.Y.Z — title" \
     --notes-file /tmp/notes.md
   ```

7. The Zenodo integration mints the immutable version DOI from the GitHub
   release under the [concept DOI](https://doi.org/10.5281/zenodo.19699233);
   add that DOI to the release notes once the record exists.
