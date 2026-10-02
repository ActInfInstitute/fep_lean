# fep_lean — canonical backlog

Only open work belongs here. Completed work and dated closure evidence belong
in [CHANGELOG.md](CHANGELOG.md) and repository history.

| ID | Open work | Acceptance probe |
| --- | --- | --- |
| FEP-FULL-CURRENT | Refresh optional Hermes/OpenGauss full-mode evidence for the live sealed roster, currently 168 topics. Historical provider reports remain historical. | Under an explicitly authorized credential and spend boundary, every live topic passes and `validate_report_receipt(..., require_complete=True, project_root=...)` reports `valid`, `source_bound`, and `claim_ready` with no validation errors. |
| FEP-RELEASE-NEXT | Assemble and publish the next source-bound release. Source metadata and the existing tag are 1.3.0; the latest published GitHub release is 1.2.0. Recover the validated same-SHA CI native/audit receipts, reconcile local build and manuscript products, and complete the remaining Python/browser/render/bundle evidence. Choose the release version and immutable DOI for the final roster before publication. | All applicable receipt validators pass against the final source, two bundle builds are byte-identical, `scripts/build_release_bundle.py --check --output PATH` is claim-ready, version/DOI references agree, and separately authorized publication verifies remote commit and artifact hashes. |
| FEP-H3-SCIENCE | Implement the independently reviewed and [frozen continuous protocol](specs/h3-reference-study/preregistration.yaml), then complete the formal/export/synthetic/claim chain. H2/G0 prerequisite and H3.0 freeze are retained evidence. | Current native and axiom evidence binds both H3 resources and their exact carrier; frozen synthetic gates, failures/controls, independent claim review and bundle reproduction are retained. Empirical execution requires its own licensed-data gate; a documented no-go/null outcome is valid. |

Daniel authorized the full [scientific improvement program](specs/comprehensive-science-improvement/PROTOCOL.md)
on 2026-09-30. Its original scope remains binding through implementation and
acceptance. The [status review](SCOPE-2026-09-30.md) records the baseline before
that implementation; dated counts and receipt verdicts there are baseline evidence.

| ID | Authorized implementation and remaining acceptance |
| --- | --- |
| PKG-2 | Real isolated wheel API/resources/help across Python 3.10–3.14 and Ubuntu/macOS/Windows; retain 3.14 as the evidence-validator runtime. Repair observed floor failures, run local available targets, and obtain hosted matrix evidence. |
| PKG-3 | Appropriate documentation PR gates plus exact-SHA accepted PDF/render/font/renderer/source artifacts; independent infrastructure review and positive/negative workflow probes. |
| PKG-4 | Typed readiness with separate evidence planes; strict bounded capture/resume; source-race invalidation; current receipts; two identical independently accepted bundles. Publication remains separately governed. |
| FORM-4 | Full H3 mathematical, preregistered synthetic and independently reviewed claim chain through H3.7. Accepted H2/G0 custody and immutable protocol freeze precede the current H3 source epoch; complete final-source export/review, frozen outcomes, claim reviews and reproduction. Unavailable licensed data produce the governed empirical no-go. |
| FEP-ACTIVE-GUIDANCE | Remove superseded root planning ledgers and stale live instructions/counts after dependency review; preserve scientific no-go, immutable receipts and historical evidence in repository history. Strict links/hygiene/xrefs must pass. |

## Closure rule

An item leaves this backlog only when its acceptance probe passes in the current
checkout, the evidence is retained in a test/report/documentation change where
appropriate, and the result is recorded in the repository's changelog or
release notes. Until then, the row remains open even if a partial local probe
looks promising.
