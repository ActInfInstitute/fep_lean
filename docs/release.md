# Release procedure

A versioned release is a tagged, hosted-CI-green `main` commit with one
consistent version. The gate is short on purpose: it checks what a release
actually ships, and it is fully checked by
[`docs/release_check.py`](release_check.py).

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
2. `uv run python docs/release_check.py` — fix every reported mismatch.
3. Run the local suite and audits (see [development](development.md)), commit
   and push to `main`.
4. Wait for hosted CI on that commit, then
   `uv run python docs/release_check.py --hosted --notes /tmp/notes.md`.
5. Build distributions from the same commit: `uv build`.
6. Tag and publish:

   ```bash
   git tag -a vX.Y.Z -m "fep_lean vX.Y.Z" && git push origin vX.Y.Z
   gh release create vX.Y.Z dist/* --title "FEP_Lean vX.Y.Z — title" \
     --notes-file /tmp/notes.md
   ```

7. Verify that the GitHub release was archived under the
   [software concept DOI](https://doi.org/10.5281/zenodo.23196891). The v1.5.0
   software version is [23196892](https://doi.org/10.5281/zenodo.23196892).
   The GitHub integration archives the tagged repository ZIP; it does not
   automatically include the PDF, wheel, sdist or release assets. Add the
   immutable software version DOI to the release notes only after checking
   the published record and its tagged source identity.
8. Publish a new version of the separate
   [scholarly concept](https://doi.org/10.5281/zenodo.19699233) from its latest
   manuscript record in the owner's Zenodo account. At the v1.6.0 preparation
   date, that latest record is [22072956](https://zenodo.org/records/22072956),
   version 1.1.0. Preserve this concept's existing version history. Upload the
   accepted PDF, offline companion, wheel, sdist, exact tagged source archive
   and SHA-256 checksums. The offline companion must preserve the PDF's
   relative explorer link: `pdf/fep_lean_combined.pdf` beside
   `manuscript/assets/mathematical-map.html` and its referenced assets.
   Keep workstation paths, account information and private execution logs
   out of public files. Link the scholarly and software records, then verify
   the published version, author, ORCID, license, file bytes and DOI resolution.

`CITATION.cff` distinguishes software citation from its preferred scholarly
citation. The manuscript's DOI identifies the scholarly concept; do not replace
it with the software concept or describe the two histories as one version chain.
