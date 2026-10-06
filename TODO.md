# fep_lean — canonical open backlog

Rescoped on 2026-10-06. Only open work belongs here; completed delivery and
dated acceptance belong in [CHANGELOG.md](CHANGELOG.md) and retained history.
Each linked GitHub Issue contains its owner, detailed scope, dependencies,
positive acceptance, failure controls and claim boundary. Size means
implementation scope, not a version or schedule promise.

## Release gate

Releases follow the short [release procedure](docs/release.md): one version
and date across version-bearing files, a dated changelog section, and a
successful hosted `ci.yml` run on the exact `main` commit, all checked by
`docs/release_check.py`. `v1.5.0` (2026-10-06) is the current release; the
untagged `1.4.0` candidate shipped within it. Nothing below blocks a release.

## Evidence and research lanes

These keep their own acceptance probes and are reported in release notes, not
claimed. Hosted Chrome startup (CUR-01) and the closed production DOM rejection
(CUR-15) remain the entry points for full capture. H3 primary seeds remain
unopened; Q7 generated-runner execution remains unverified. The
[locked protocol](specs/comprehensive-science-improvement/PROTOCOL.md) retains
all nine original criteria; the [execution sequence](specs/comprehensive-science-improvement/NEXT.md)
orders this work.

| Work | Size | Predecessors | Closure probe |
| --- | --- | --- | --- |
| [CUR-01](https://github.com/ActiveInferenceInstitute/fep_formal/issues/46) — Diagnose hosted live Chrome startup and review conditional grouping | Minor | Independent repair | Actual two-Chrome acceptance and meaningful xdist controls; fresh exact-SHA Python passes without retries/skips/cap changes. |
| [CUR-15](https://github.com/ActiveInferenceInstitute/fep_formal/issues/51) — Diagnose noncanonical live DOM rejection in the closed production capture | Minor | Independent repair | Explain and repair the actual noncanonical DOM rejection; real browser receipt passes, with old output hashes kept historical. |
| [CUR-03](https://github.com/ActiveInferenceInstitute/fep_formal/issues/52) — Seal complete approved tests membership in the successor source freeze | Minor | [CUR-01](https://github.com/ActiveInferenceInstitute/fep_formal/issues/46), [CUR-02](https://github.com/ActiveInferenceInstitute/fep_formal/issues/47), [CUR-04](https://github.com/ActiveInferenceInstitute/fep_formal/issues/48), [CUR-15](https://github.com/ActiveInferenceInstitute/fep_formal/issues/51) | Exact approved full tests membership enforced before imports/planning/dispatch and at closure; nonauthor source review passes. |
| [CUR-05](https://github.com/ActiveInferenceInstitute/fep_formal/issues/53) — Accept a fresh full seven-stage capture and identical package archives | Medium | [CUR-01](https://github.com/ActiveInferenceInstitute/fep_formal/issues/46), [CUR-02](https://github.com/ActiveInferenceInstitute/fep_formal/issues/47), [CUR-03](https://github.com/ActiveInferenceInstitute/fep_formal/issues/52), [CUR-04](https://github.com/ActiveInferenceInstitute/fep_formal/issues/48), [CUR-15](https://github.com/ActiveInferenceInstitute/fep_formal/issues/51) | All seven actual stages and closing guards pass; two identical package archives independently claim-ready. |
| [CUR-06](https://github.com/ActiveInferenceInstitute/fep_formal/issues/49) — Accept five local installed-wheel runtimes and read-only status | Medium | [CUR-01](https://github.com/ActiveInferenceInstitute/fep_formal/issues/46), [CUR-02](https://github.com/ActiveInferenceInstitute/fep_formal/issues/47), [CUR-04](https://github.com/ActiveInferenceInstitute/fep_formal/issues/48) | Five actual isolated runtime cells and read-only status controls pass; 184 resources/80 cases and 15 GiB gate preserved. |
| [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54) — Pass every declared check and exact-SHA hosted artifact gate | Medium | [CUR-01](https://github.com/ActiveInferenceInstitute/fep_formal/issues/46), [CUR-02](https://github.com/ActiveInferenceInstitute/fep_formal/issues/47), [CUR-04](https://github.com/ActiveInferenceInstitute/fep_formal/issues/48), [CUR-05](https://github.com/ActiveInferenceInstitute/fep_formal/issues/53), [CUR-06](https://github.com/ActiveInferenceInstitute/fep_formal/issues/49) | Every applicable declared check and all same-SHA hosted jobs/artifacts validate; local and hosted evidence remain separate. |
| [CUR-08](https://github.com/ActiveInferenceInstitute/fep_formal/issues/55) — Refresh H3 native export and three independent proof-role reviews | Medium | [CUR-05](https://github.com/ActiveInferenceInstitute/fep_formal/issues/53), [CUR-06](https://github.com/ActiveInferenceInstitute/fep_formal/issues/49), [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54) | Current 293-source export, 24 roles/33 supplements/12 witnesses and three independent proof-role reviews accepted. |
| [CUR-09](https://github.com/ActiveInferenceInstitute/fep_formal/issues/56) — Execute frozen H3 primary once and replay all 42 arrays | Major | [CUR-08](https://github.com/ActiveInferenceInstitute/fep_formal/issues/55) | Exactly one frozen primary invocation; all 42 arrays/control results retained and replayed, including governed scientific rejection. |
| [CUR-10](https://github.com/ActiveInferenceInstitute/fep_formal/issues/57) — Close outcome claims, study archive parity and clean installed reproduction | Major | [CUR-09](https://github.com/ActiveInferenceInstitute/fep_formal/issues/56) | Three outcome reviews, identical independently valid study archives and clean installed 42-array reproduction complete. |
| [CUR-14](https://github.com/ActiveInferenceInstitute/fep_formal/issues/59) — Audit all nine original criteria and final evidence boundaries | Medium | [CUR-05](https://github.com/ActiveInferenceInstitute/fep_formal/issues/53), [CUR-06](https://github.com/ActiveInferenceInstitute/fep_formal/issues/49), [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54), [CUR-10](https://github.com/ActiveInferenceInstitute/fep_formal/issues/57) | Independent mapping closes all nine criteria and exact FORM-1–FORM-3 semantic/native/axiom boundaries at final source. |

## Separately governed lanes

These remain open and activate only on their stated conditions.
A governed empirical no-go satisfies the frozen current program. Accepted Q7
static proofs do not imply the future runner lane ran. PRs remain substantive
until a verified integration or disposition; they are not removed as legacy.

| Work | Size | Predecessors and activation | Closure probe |
| --- | --- | --- | --- |
| [CUR-12](https://github.com/ActiveInferenceInstitute/fep_formal/issues/50) — Refresh optional strict Hermes/OpenGauss evidence for all 168 topics | Medium | Secure current credential/model route and concrete spend boundary | Complete source-bound strict full-mode report for all 168 topics independently claim-ready; secure preflight and enforcement of the separately authorized spend ceiling remain required. |
| [CUR-13](https://github.com/ActiveInferenceInstitute/fep_formal/issues/58) — Review substantive PR44 against current formal and ownership contracts | Medium | [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54) | Fresh current-base PR44 formal/ownership brief, warning-free native/axiom/projection evidence and independent domain review before integration. |
| [BRIDGE-D1](https://github.com/ActiveInferenceInstitute/fep_formal/issues/61) — Prove actual generated GNN runner execution on an isolated named pair | Medium | [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54) and an explicitly named isolated pair | Actual source-bound generated-runner output and positive/adversarial controls; active GNN work remains untouched. |
| [EMP-J1](https://github.com/ActiveInferenceInstitute/fep_formal/issues/77) — Gate future empirical work on licensed data and new immutable protocol | Major | [CUR-10](https://github.com/ActiveInferenceInstitute/fep_formal/issues/57) and named licensed data/new protocol | Verifiable license/provenance/split and independently reviewed real measurements, or retained governed no-go. |

## Upcoming minor, medium and major scopes

The [maintained research scopes](docs/design/fep-research-program/next-improvements.md)
retain the eleven existing detailed proposals; the additional bounded issues
cover configuration, accessibility, catalogue review and general finite duality.
Use the [work-package contract](docs/design/fep-research-program/research-contract.md)
before activating an implementation. Demonstrate a concrete gap first for
configuration and visualization work. New owners require a coordinated source
roster refresh; new topics are not implicitly reserved by this plan.

| Work | Size | Predecessors | Closure probe |
| --- | --- | --- | --- |
| [CORE-M1](https://github.com/ActiveInferenceInstitute/fep_formal/issues/62) — precise operator contracts | Minor | [CUR-06](https://github.com/ActiveInferenceInstitute/fep_formal/issues/49), [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54) | Parser/API/installed-help agreement on inputs, mutation, platform and exit meanings; operator review. |
| [CORE-M2](https://github.com/ActiveInferenceInstitute/fep_formal/issues/63) — maintain current guidance through dependency review | Minor | [CUR-04](https://github.com/ActiveInferenceInstitute/fep_formal/issues/48) | Current active reading paths, complete retirement caller inventory, strict links/hygiene/xrefs and preserved historical evidence. |
| [CORE-M3](https://github.com/ActiveInferenceInstitute/fep_formal/issues/73) — Audit configurable defaults and thin orchestration across workflows | Minor | [CUR-04](https://github.com/ActiveInferenceInstitute/fep_formal/issues/48), [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54) | Documented configuration/default/precedence matches actual behavior; bounded compatibility changes keep orchestration thin. |
| [FORM-M1](https://github.com/ActiveInferenceInstitute/fep_formal/issues/68) — align primary theorem proxies with the proved information seams | Minor | [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54) | Exact primary types/assumptions/non-vacuity reviewed; stable IDs/signatures and all native/axiom/boundary projections accepted. |
| [CORE-D1](https://github.com/ActiveInferenceInstitute/fep_formal/issues/64) — expose one reusable typed readiness API | Medium | [CUR-05](https://github.com/ActiveInferenceInstitute/fep_formal/issues/53), [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54) | One immutable readiness API and real non-CLI consumer; installed/CLI parity, race/process/mutation controls and infrastructure review. |
| [CORE-D2](https://github.com/ActiveInferenceInstitute/fep_formal/issues/65) — portable semantic and relation queries from one canonical join | Medium | [CUR-06](https://github.com/ActiveInferenceInstitute/fep_formal/issues/49), [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54) | Reviewed generated query schema conserves topics/relations/assumptions/blockers; deterministic isolated-wheel parity and semantic review. |
| [CORE-D3](https://github.com/ActiveInferenceInstitute/fep_formal/issues/74) — Improve accessible offline manuscript, atlas and numerical explanations | Medium | [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54), [CUR-10](https://github.com/ActiveInferenceInstitute/fep_formal/issues/57) | Demonstrated accessibility gap resolved through shared models; deterministic offline SVG/HTML/PDF and actual browser/text alternatives pass. |
| [FORM-D1](https://github.com/ActiveInferenceInstitute/fep_formal/issues/69) — exact fair-Boolean Hamming rate-distortion curve | Medium | [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54) | Derived Boolean Hamming converse/attaining channel/curve, endpoints and interior multiplier with information-theory review. |
| [FORM-D2](https://github.com/ActiveInferenceInstitute/fep_formal/issues/70) — fixed-truth consistency for the continuous static-latent model | Medium | [CUR-10](https://github.com/ActiveInferenceInstitute/fep_formal/issues/57) | Explicit infinite fixed-truth law, prefix/native equality and actual convergence proof; new protocol preserves current H3 seeds. |
| [FORM-D3](https://github.com/ActiveInferenceInstitute/fep_formal/issues/75) — Review all 168 theorem proxies and rank substantive strengthening | Medium | [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54), [FORM-M1](https://github.com/ActiveInferenceInstitute/fep_formal/issues/68) | All 168 proxies receive statement-based semantic review and ranked substantive proof briefs; no automatic disposition promotion. |
| [CORE-J1](https://github.com/ActiveInferenceInstitute/fep_formal/issues/66) — equivalent Windows capture custody and process supervision | Major | [CUR-05](https://github.com/ActiveInferenceInstitute/fep_formal/issues/53), [CUR-06](https://github.com/ActiveInferenceInstitute/fep_formal/issues/49), [CUR-07](https://github.com/ActiveInferenceInstitute/fep_formal/issues/54) | Equivalent Windows no-follow handle custody and descendant containment; actual seven-stage acceptance and identical valid archives. |
| [CORE-J2](https://github.com/ActiveInferenceInstitute/fep_formal/issues/67) — measured incremental capture and bounded resource lifecycle | Major | [CUR-05](https://github.com/ActiveInferenceInstitute/fep_formal/issues/53), [CORE-D1](https://github.com/ActiveInferenceInstitute/fep_formal/issues/64) | Measured full/resumed/edited capture equivalence, exact dependency invalidation and closed-owned resource receipts without weaker budgets. |
| [FORM-J1](https://github.com/ActiveInferenceInstitute/fep_formal/issues/71) — observation-dependent finite-horizon control on one carrier | Major | [CUR-10](https://github.com/ActiveInferenceInstitute/fep_formal/issues/57) | Finite-horizon measurable updates/selectors, Bellman/native cost equality, attainment/moment bounds and exact two-step recovery. |
| [FORM-J2](https://github.com/ActiveInferenceInstitute/fep_formal/issues/72) — generator-to-path lifting with an explicit library stop gate | Major | [CUR-10](https://github.com/ActiveInferenceInstitute/fep_formal/issues/57) | Pinned generator/path API stop gate, semigroup compatibility and actual path construction, or bounded upstream proposal/no-go. |
| [FORM-J3](https://github.com/ActiveInferenceInstitute/fep_formal/issues/76) — Probe general finite rate-distortion strong duality before staged proof | Major | [FORM-D1](https://github.com/ActiveInferenceInstitute/fep_formal/issues/69) | Pinned convexity/support/separation/endpoint seam passes before derived general finite duality, or explicit library no-go. |

## Original requirement coverage and closure

| Original criterion | Required open gates |
| --- | --- |
| 1 — truthful static status | CUR-06, CUR-14 |
| 2 — actual package support | CUR-06, CUR-07 |
| 3 — docs and accepted render | CUR-07 |
| 4 — strict capture/archive parity | CUR-03, CUR-05 |
| 5 — information identity/coarsening | CUR-07, CUR-14 |
| 6 — relative-support/native information | CUR-07, CUR-14 |
| 7 — genuine finite rate-distortion | CUR-07, CUR-14 |
| 8 — frozen H3 full chain | CUR-08, CUR-09, CUR-10 |
| 9 — all checks/source/remote evidence | CUR-07, CUR-14 |

An item leaves TODO and its Issue closes only after its own exact-current-source
acceptance is retained and recorded in changelog/release notes or accepted
history. Missing, historical, partial or indirect evidence keeps it open.
Scientific null/rejection/no-go outcomes remain evidence under their protocol;
they do not authorize retries, changed gates or unsupported success claims.
Source-only approval, installation, local runtime, hosted acceptance and live
publication are separate states. Never close a broad requirement on a subset.
