# SourceCheck implementation plan

Date: 2026-09-24. Status: local implementation underway; checked boxes below have
recorded evidence in [RESULTS.md](docs/RESULTS.md). Live Jev and later pilot gates
remain open.
Read [PRODUCT.md](PRODUCT.md) for the customer hypothesis and
[DATASETS.md](docs/DATASETS.md) for the investigated sources.

## Release contract

Deliver a local single-user application that compares original invoice evidence
with actual importer output under an explicit destination contract. The user can
review findings, save a reference case, rerun it and export a reproducible report.

The local MVP includes a genuine Mustang import adapter plus uploaded JSON/CSV.
Odoo is a later integration gate. A mock destination is useful for functional tests
but cannot establish that any importer loses information.

The historical routing taxonomy, queue mapping, archive organization and RVL-CDIP
evaluation are superseded. Retain reusable engineering from those projects without
carrying their country/type metrics into this task.

## Responsibilities

| Component | Responsibility |
|---|---|
| Intake | Preserve source/output bytes, validate formats and allocate stable IDs |
| Source reader | Extract declared XML facts, native PDF text or local OCR with provenance |
| Importer adapter | Capture genuine importer output and execution identity |
| Mapping profile | Declare expected facts, destination paths and observable coverage |
| Deterministic comparator | Compare exact facts with explicit normalization rules |
| Jev adapter | Suggest semantic relationships for bounded text pairs |
| Review | Record human dispositions and accepted reference cases |
| Regression | Compare immutable runs while identifying changed dependencies |
| Export | Produce a verifiable report from one immutable snapshot |

No model authorizes payments or production writes. Compliance checks and preservation
checks are different result dimensions. Keep their denominators and UI badges separate.

## Source and destination contracts

### Independent source evidence

- Read raw XML with a safe parser independently of the importer under test.
  Preserve the declared string, namespace-aware path and document hash.
- Native PDF text and OCR are separate observations with page/region references.
  Record page dimensions, orientation, rendering parameters and OCR model hashes.
- For hybrid invoices retain PDF and embedded XML as separate representations.
  If they disagree, record source conflict. Do not silently designate one as truth
  for every business question. The profile specifies which representation a check uses.
- Numerical reference facts can come from independently parsed XML or reviewed source
  evidence. Jev output and the tested importer's own values cannot supply expected facts.
- Missing coordinates are legitimate for some extraction paths. Never invent a box.
  Manually edited text creates a new observation; it does not inherit unsupported boxes.

### Destination capture

Each adapter/export declares:

- Tool/version or commit, extraction command, settings and output hash.
- Whether the output is actual importer execution, actual ERP snapshot, user-uploaded
  output with unverified provenance, or an authored simulation.
- Entity identity, supported fields, paths and coverage: complete, partial or unknown.
- Missing/null/empty semantics and whether a missing path establishes absence.
- Known transformations, limitations and line-item identifiers.
- For an ERP snapshot, export/query definition, observation time and accessible fields.
  Fields not exposed by that query are unobserved, even if the user expected them.

Start with JSON. For CSV, require a reviewed column mapping, explicit row/entity
grouping, decimal/locale configuration and coverage contract. Guessing column names
may produce a draft profile, never a silently accepted mapping.

The Mustang adapter must call the actual pinned Java library or supported CLI
operations and capture the available fields. Do not assume the CLI already exports
our desired JSON. Implement a small Java bridge if needed and test its coverage.
Record any fields the bridge cannot expose; do not count them as importer losses.

### Versioned profile

Include profile ID/hash, source selectors, destination selectors, required-for-this-
integration flags, normalization rules, line alignment and coverage declarations.

A fact can be required by a client's integration without being required by a standard.
The UI must say which requirement is being tested. Profile changes create new versions.
The user previews their affected checks before accepting them.

Use decimal arithmetic and explicit currency, units, signs and tolerances.
Do not apply a universal one-cent tolerance or case folding to every identifier.
Separate invoice total, outstanding amount, due date and service period.
Preserve raw values alongside normalized values.

Align line items first by declared stable identifiers, then by explicitly configured
rules. Repeated descriptions or amounts alone may be ambiguous. Preserve one-to-many
relationships; do not compare unrelated lines just to achieve complete coverage.

## Findings and review model

Represent independent dimensions rather than one overloaded status:

| Dimension | Examples |
|---|---|
| Job | queued, running, complete, failed, delivery_unknown |
| Source observation | available, uncertain, conflicting, unsupported |
| Destination coverage | observable, unobserved, ambiguous |
| Check result | equal, different, missing, semantic_review, not_checkable |
| Semantic suggestion | equivalent, contradictory, partially_preserved, insufficient_evidence |
| Human disposition | pending, confirmed_issue, accepted_transformation, dismissed, unresolved |
| Requirement | configured_required, informational, not_applicable |

Only emit missing when a usable source observation and complete relevant destination
coverage establish absence. An OCR omission is not evidence of source absence.
Unknown export coverage is not evidence of data loss.

Every finding references exact source observations, destination observations, profile,
comparator version and optional inference run. A dismissal needs a reason and reviewer.
A passed check states its scope; never show a universal "safe to import" badge.

Preserve prior runs and review decisions. Rerunning creates a new immutable result;
it does not inherit approval on changed evidence. If source/output/profile changes,
show which findings are new, resolved, changed or no longer comparable. Carry a prior
disposition only as a visible historical reference, not current approval.

A reviewed reference case records expected outcomes with annotation origin and scope.
Only an explicit action promotes reviewed facts to reference labels. Keep evaluation
test labels inaccessible to the inference services.

## Jev integration

Reuse the typed client after verifying the current official API contract.

- Input: relevant source text, corresponding destination text and a narrow criterion.
- Exclude expected labels, issue names, mutation IDs and revealing file paths.
- Use Choice for mutually exclusive semantic relations defined above.
- Optional Noul questions must be independent, specific propositions. Questions in
  one request cannot consume one another's answers.
- Equivalence concerns the configured fact, not arbitrary overall document similarity.
- Missing/ambiguous alignment and unavailable evidence should be handled before inference.
- The model returns suggestions and probabilities, not generated explanations or boxes.
  Use templates linked to actual observations for explanatory UI text.
- Display confidence as provider output, not measured accuracy or a correctness guarantee.
- No automatic acceptance of semantic findings in the MVP.
- Compare deterministic-only and deterministic-plus-Jev on the same observable pairs.
  Another model is optional only within the evaluation budget and a concrete question.

Cache identity includes endpoint, pinned model, exact state, question/criteria hashes
and relevant normalization version. Mark cache hits and distinguish fresh timings.
Do not automatically resend requests with unknown delivery/billing status after a crash.

## Architecture

Preferred starting point: Python 3.12, FastAPI, SQLite and vanilla HTML/CSS/JavaScript.
Use the Python namespace sourcecheck, avoiding trace-it's generic app namespace.
Inspect dependency compatibility and pin a reproducible installation.

Use a single-command server/worker launcher with a persistent job queue, bounded
worker concurrency and explicit shutdown/recovery. A dedicated worker process is
acceptable if the launcher supervises it. Use migrations, transactions and foreign keys.

Persist workspaces, artifacts, observations, destination captures, profile versions,
comparison runs, job attempts, semantic runs, findings, review events, reference cases,
regression comparisons and exports. Large private payloads belong in runtime storage.

Claim jobs with leases or equivalent recovery. Reuse completed extraction after restart.
Keep partial failures per case. Expose retryable failure, unsupported format and unknown
provider delivery separately. A retry creates a recorded attempt.

## Browser workflow

- Create a case or batch; upload source and destination or select the supported adapter.
- Preview detected representations and mapping/coverage before comparing.
- Show source page/text/XML, destination paths and findings together.
- Click a finding to locate its source region and destination value. Support page
  navigation, zoom and fit; allow accessible text navigation without coordinates.
- Filter by requirement, result, coverage and human disposition. Keep empty/error
  states and unsupported cases visible.
- Show semantic suggestion, provenance, raw/normalized values and execution details.
  Keep prompt experiments out of the primary user workflow.
- Record individual decisions and reasons; batch review is optional after core delivery.
- Save a reference case and run a selected importer version again.
- Diff runs and profile changes with explicit comparability warnings.
- Export and delete cases through the UI with clear content-retention behavior.

Verify actual viewport widths 360, 768, 1280 and 1920 pixels at 100% zoom, and desktop
125%/200% zoom. No clipped text, hidden controls or page-wide horizontal overflow.
Use stacked details on small screens and accessible scrolling inside genuinely wide
data panels. Users must not need to zoom out to reach a field.

## Boundaries and storage

- Bind to 127.0.0.1:8770; validate host/origin and protect local mutation endpoints.
- Keep keys server-side. Local OCR is compatible with external Jev text transmission;
  show the live-processing choice before a job sends selected text.
- Default intake limits: 25 MiB per source/output file, 20 PDF pages, 18 MP per decoded
  image and 50 cases per batch. Benchmark large XML separately under a bounded profile.
- Parse XML without DTD/entity expansion, external schemas or network access. Apply
  byte/depth/time limits to XML/JSON and document renderers.
- Inspect embedded files with count/size limits. User ZIP intake is outside the MVP;
  dataset download archives need safe extraction and decompression budgets.
- Use bounded subprocess execution and controlled arguments for Java/PDF tools.
  Uploaded content never selects commands or host paths.
- Originals live outside static serving. Validate artifact IDs; escape document text,
  HTML and formula-leading CSV values without altering the archived raw evidence.
- Deletion removes original/derived content and associated provider caches as documented.
  Explain that already downloaded exports are outside the server's control.

## Report export

Create a ZIP from an immutable run/review snapshot with summary.json, findings.csv,
a self-contained report.html, provenance and a SHA-256 manifest. Report observed,
unobserved, uncertain, failed and unresolved counts separately.

Default export omits originals, raw OCR bodies and provider responses. Including
source content is a separate explicit option with a content preview. Paths must be
safe and generated. A plain report contains escaped data and no remote resources.

Verify archive integrity before offering it. Provide an offline verifier. Hashes
establish file integrity, not correctness or authenticity of the business facts.
If review changes during export, finish against the identified snapshot.

## Acquisition and evaluation controls

Follow docs/DATASETS.md and docs/EVALUATION.md.

- At most 1 GiB of dataset transfers and 4 GiB total new bootstrap transfers by default.
  Account for retries, Git history, binaries and container pulls. Cache reuse costs zero
  new transfer bytes but still counts toward storage reporting.
- Odoo is optional later work; do not pull its images during the initial MVP by default.
- Prepare manifests and a byte estimate before acquisition, then record actual bytes.
  Exceeding a cap requires an explicit configured budget change; no silent fallback.
- Live API estimate budget: USD 1.00 total across development/smoke/final runs. Verify
  current prices, include bounded in-flight reservations and stop new requests at the cap.
  Unknown delivery may have incurred billing; retain conservative accounting.
- Do not download RVL-CDIP or ARIES for this release. Optional SROIE needs a specific
  remaining OCR evaluation question and must fit the dataset cap.

## Phases

### Phase 0: contracts and provenance

- [x] Inspect pinned reusable source, licensing and dependency compatibility.
- [x] Record source manifests, licenses, artifact versions and size plans.
- [x] Define independent observations, profiles, coverage and finding schemas.
- [x] Package the app, add migrations and create owned functional fixtures.

### Phase 1: offline product workflow

- [x] Implement persistent intake, safe XML/PDF/image readers and JSON/CSV mapping.
- [x] Implement deterministic comparisons, coverage and ambiguous line alignment.
- [x] Build responsive review, evidence navigation and recovery.
- [x] Preserve review history; save cases and compare reruns/profile revisions.
- [x] Implement deletion, snapshot report export and offline integrity verification.

### Phase 2: genuine importer and OCR

- [x] Execute pinned Mustang and document bridge/API coverage.
- [x] Run real local OCR using pinned models and source provenance.
- [x] Exercise native PDF, hybrid XML/PDF and scanned-image cases.
- [x] Compare two pinned importer versions without presuming failures or improvements.
- [x] Record actual inputs, outputs, timings and adapter limitations.

### Phase 3: semantic comparison and evaluation

- [x] Integrate the optional Jev API path with typed validation, caches and budgets;
      live calls remain unverified without credentials.
- [ ] Freeze a representative family-level manifest before held-out test inference.
- [ ] Evaluate deterministic baseline and live Jev extension on the same reviewed pairs.
- [x] Separate authored faults, observed importer behavior and source/OCR failures.
- [ ] Publish representative held-out aggregates and reviewed error analysis.
- [x] State the current Jev conclusion: insufficient evidence for measured value.

### Phase 4: local MVP handoff

- [ ] Exercise true browser zoom at 125%/200%; Chromium viewport/DPR emulation and
      the four required 100% widths have been verified.
- [x] Verify restart recovery, stale-review protection and export consistency.
- [x] Verify clean Windows clone and document actual PowerShell and Linux/macOS
      commands; native Linux/macOS desktop runs remain unverified.
- [x] Add and verify app container setup; distinguish it from the optional ERP environment.
- [x] Replace proposed commands with tested Windows instructions and record evidence.
- [x] Update docs/RESULTS.md, review the diff, commit and push.

### Phase 5: optional ERP and customer pilot

- [ ] Add Odoo 19/PostgreSQL with pinned digests and explicit field-query coverage.
- [ ] Compare original sources with real persisted ERP data in an isolated test instance.
- [ ] Evaluate another importer/ERP only if it tests a concrete generalization question.
- [ ] Run representative integrator pilots and measure diagnosis effort/repeat use.

## Required verification

Test the complete source/output path and these material risks:

- Identical facts and configured normalization do not create false discrepancies.
- Unknown target coverage and uncertain source readings never become asserted losses.
- Currency/sign/decimal differences and line permutations retain their meaning.
- Repeated similar lines yield ambiguity rather than fabricated correspondence.
- Source/XML disagreement stays visible and cannot be erased by a successful validator.
- Actual importer output is kept distinct from authored target JSON.
- Restart preserves jobs and reviews without silently duplicating paid calls.
- Reruns retain prior decisions as history and require current review for changed evidence.
- Export manifests, snapshot IDs and hashes agree despite concurrent review.
- Document/CSV/HTML/XML input cannot execute content or access unintended paths.
- Test family leakage and expected-label leakage fail the evaluation gate.
- Browser controls, tables, text, boxes and export links work without clipping.
- Live and cached metrics are distinguishable; missing usage is never priced as free.

## Local MVP definition of done

A new user can install the app, process a permitted source through the real Mustang
adapter, inspect supported independent facts against its output, review discrepancies,
save a case, restart, rerun another version and export a verifiable report.
Uploaded output and real OCR paths also work under documented coverage limits.

The handoff includes actual commands, functional/browser evidence, provenance,
independent references, aggregate evaluations and an honest Jev assessment. If live
credentials are unavailable, finish the offline workflow and label the live evaluation
gate incomplete. Odoo/customer validation remains explicitly separate.
