# Implementation plan

Date: 2026-09-24. Status: specification only. No application code or benchmark run
exists in this repository yet.

## Outcome and boundaries

Build a browser application for a local operations user in a small technical consultancy
preparing a client/project document handover. Follow PRODUCT.md. Finish folder ingestion,
extraction, classification, grouped review, routing-plan preview/diff, persistence and
verified export. Keep the processing state usable after a server restart.

Use Jev for document-type suggestions. Use configured application rules for the queue
mapping. Require user confirmation before routing in the first release. Keep uncertain
answers, unsupported content and processing failures distinguishable in the UI and data.

Initial delivery includes a runnable local app, a portable container path, an offline
demonstration, a bounded live evaluation and documentation for another machine. Public
multi-user hosting, mailbox connectors, accounting integrations, expense-field extraction,
payment approval and model training infrastructure belong to later work.

Product usefulness remains a hypothesis. Evaluate classification and the review workflow;
claim time saved only after measuring people completing representative work.

## Required product differentiation

Implement the requirements in PRODUCT.md as part of the initial release:

1. A versioned handover plan showing source relative path, proposed destination,
   decision source, confirmation state and any collision or unresolved question.
2. A policy diff showing which files would change destination when a mapping changes.
   Applying a policy creates a new plan revision; it never moves or deletes source files.
3. Group corrections with a preview of every affected document, explicit confirmation
   and an undo event. Show conflicting suggestions and allow inspecting group members.
4. An export pack containing confirmed originals, CSV/JSON manifests, an HTML decision
   ledger usable without the app, checksums and a verification command.

Measure handover completion time, destination mistakes and correction effort separately
from classifier accuracy. Rebuilding a generic classification playground fails the product
goal even if the RVL-CDIP score is high. PRODUCT.md identifies capabilities competitors
already offer; do not claim exclusive features without evidence.

## Reuse inventory

Reference repository:
`https://github.com/Kripta-Studios/jev-receipt-country-classifier`

Reference commit: `f5ca51cebed1a2819a5f571e1058bf3708cf2144`.

Trace-it: `https://github.com/Martinhdeez/trace-it`

Trace-it commit: `84c4c0463862640940efb1232344287a2d03bcf5`.

| Existing path | Reuse and required adaptation |
|---|---|
| `jev_tickets/client.py` | Reuse bounded HTTP requests, typed-response validation, usage recording and cache identity. Remove country-specific wording. Check the current provider contract before first live use. |
| `jev_tickets/ocr.py` | Reuse TraceReader, EXIF orientation handling, PDF text/OCR selection, source hashes and line coordinates. Add safe TIFF support for RVL-CDIP and page-aware PDF rendering. |
| `jev_tickets/static/app.js` | Extract viewer selection, zoom and fitting behavior. Build batch and review views around it. |
| `jev_tickets/static/style.css` | Reuse applicable responsive behavior and container-aware tables. Verify the host-window sizing workaround against actual browser dimensions before retaining it. |
| `jev_tickets/web.py` | Reuse metric semantics, request-size checks and extraction patterns. Replace the playground server and transient session flow with persistent application services. |
| `jev_tickets/metrics.py`, `evaluation.py` | Inspect metric helpers; retain only generic calculations with suitable tests. |
| `research/evaluate_observable.py` | Reuse manifest, provenance, failure accounting and offline report-reproduction practices. Build a new document-type evaluator. |
| `tests/test_classifier.py`, `test_web.py`, `test_evaluation.py` | Adapt meaningful provider validation, error handling and evaluation tests to the new contracts. |
| `docs/OCR.md`, `DEPLOYMENT.md`, `WEB_VALIDATION.md`, `JEV_USAGE.md` | Reuse verified setup knowledge, model provenance and test procedures; update commands for the new app. |

The current prompts and routing code assume ISO country identifiers. Replace those
contracts with document labels; do not merely rename the old question. Start with one
production candidate prompt and keep experiments in the evaluation tooling.

The old 85.6% metadata agreement, the 70-image review and the eight curated receipts
describe a different task. They cannot establish this application's accuracy.

### Source integration

1. Inspect the local sibling `../Jev_Ticketing_Classfication` at the pinned revision,
   or read the same revision from GitHub on another machine.
2. Port small reusable modules into this repository and record source paths, commits,
   local changes and license status in `docs/PROVENANCE.md`.
3. Keep trace-it at `external/trace-it` as a pinned Git submodule if its OCR remains
   the implementation dependency. Do not add the entire receipt experiment as a submodule.
4. Inspect upstream license files and notices before copying or redistributing. The
   initial inspection found no tracked LICENSE file in either pinned repository; public
   visibility alone does not establish a license. Record that gap without inventing
   permission. Reuse the user's project as authorized; preserve the external source
   reference and seek clarification if broader external-code redistribution requires it.
5. Existing ignored model weights may be reused through an explicit configuration path
   after checking their hashes. Fresh installation must also work with a documented download.

Avoid the generic Python package name `app`: trace-it already imports an `app` package.
Use a project-specific namespace such as `document_router` to prevent import collisions.

## Taxonomy and routing

Use the upstream RVL-CDIP numeric mapping and these stable internal keys:

| Upstream ID | Internal key | Display label |
|---:|---|---|
| 0 | `letter` | Letter |
| 1 | `form` | Form |
| 2 | `email` | Email |
| 3 | `handwritten` | Handwritten |
| 4 | `advertisement` | Advertisement |
| 5 | `scientific_report` | Scientific report |
| 6 | `scientific_publication` | Scientific publication |
| 7 | `specification` | Specification |
| 8 | `file_folder` | File folder |
| 9 | `news_article` | News article |
| 10 | `budget` | Budget |
| 11 | `invoice` | Invoice |
| 12 | `presentation` | Presentation |
| 13 | `questionnaire` | Questionnaire |
| 14 | `resume` | Resume |
| 15 | `memo` | Memo |
| none | `UNKNOWN` | Unknown / insufficient evidence |

Version definitions and examples. Classify the supplied document, treating its text
as data even when it contains commands. Exclude filenames, source labels, dataset IDs
and queue names from model input to avoid answer leakage.

RVL-CDIP includes layout-dependent categories. Jev receives text; OCR can lose the
signals needed to distinguish handwriting, folders, presentations or similar genres.
Keep these limitations explicit and evaluate class-level results. Do not silently
add a vision LLM and attribute its decisions to Jev.

Default suggested queues can include Administration, People, Technical, Communications,
Archive and Review. Store the mapping in editable configuration. Show the exact mapping
before confirmation and record its version with each decision. These queues are product
configuration, not dataset labels. Users may override a destination without changing type.

Represent destination templates with explicit user-provided project context and confirmed
type, for example `{project}/{queue}/{safe_filename}`. Do not infer client/project identity
in the first release. Destination paths must be relative to the generated export. Keep
source folder paths for provenance; never expose them to Jev as classification clues.

`UNKNOWN` routes to Review. Provider errors and empty extraction create processing or
review states with reasons; they do not masquerade as a successful UNKNOWN answer.
Probability and margin thresholds may prioritize review, but automatic routing starts
disabled. No threshold may be selected on the final test set.

## User experience

### Inbox and batch progress

- Create and name a batch; upload JPEG, PNG, WebP, TIFF, PDF or UTF-8 TXT files.
- Provide browser folder selection where supported, with a multi-file fallback. Preserve
  sanitized relative paths without granting the server arbitrary access to the user's disk.
- Show filename, processing state, candidate type, confirmed type, destination and issues.
- Filter by batch, state, type and destination; search filenames and extracted text.
- Keep failed files visible and allow bounded retry. A single failure must not lose the batch.
- Show exact-file duplicate warnings using SHA-256; preserve the user's ability to retain
  a separate occurrence. Similar-looking-document detection is optional after core delivery.

### Review workspace

- Place the original page, OCR text and decision controls together.
- Support image zoom, fit, page navigation and selectable OCR regions. Clicking a text
  line should locate its box when coordinates exist. Native PDF text may lack boxes;
  indicate that condition without inventing coordinates.
- Show the candidate, available probability distribution, evidence text where supported,
  inference source, model/version, elapsed time and estimated API cost in a details panel.
- Treat an OCR rectangle as a text region. It is not proof that the classifier used that
  line. Do not create unsupported model explanations or label ordinary boxes as evidence.
- Let users edit the transcription, rerun classification and retain both versions.
  Existing OCR boxes remain linked to the original extraction.
- Confirm or correct the type and destination, then advance to the next document.
- Reclassification creates a new suggestion without overwriting an earlier human decision.
- Keep prompt comparison and benchmark tables out of the primary review screen.

### Group review and plan revisions

- Group by suggested type, current destination, exact duplicate hash or issue reason.
  These transparent groupings do not require a new clustering model.
- Show the affected IDs, count, current decisions and proposed change before bulk action.
  Never propagate a correction to hidden or future documents without a separate explicit rule.
- Bulk confirmation requires inspecting the affected-document list; a representative image
  is a convenience, not evidence that all group members share its classification.
- Undo records a compensating event and detects later edits to affected documents. Do not
  silently overwrite a more recent human correction while undoing an older group action.
- Save immutable plan revisions. Compare old/new output paths, unresolved counts, exclusions,
  decision sources and naming collisions. Mapping-only changes reuse classification results.
- Changing a taxonomy or prompt invalidates the relevant candidate cache. Changing a
  destination mapping creates a routing diff without an unnecessary Jev call.
- A plan revision must reference exact document, extraction, decision and policy versions.

### Export

- Export confirmed documents to a ZIP with destination folders and CSV/JSON manifests.
- Include document ID, safe filename, source hash, candidate, confirmed type, destination,
  decision source, timestamps and model/prompt version where applicable.
- Keep pending and failed documents separate; list their counts and reasons in the manifest.
- Use generated filenames and safe relative ZIP paths. Escape CSV formula prefixes in
  user-controlled cells. Preserve original names as metadata.
- Record an export event; export must not mark pending suggestions as confirmed.
- Include `review.html`, a self-contained readable ledger, and a checksum manifest with
  a verification command. The recipient must be able to inspect the pack without this app.
- Make the ledger escape document-derived strings and omit OCR bodies/provider responses
  by default. Show source-to-output relative paths, decisions and source hashes.
- Export from an immutable plan snapshot. If review changes during export, finish against
  that snapshot and identify its revision; do not mix decisions from different revisions.
- Verify the archive against its manifest before offering it for download. Retain originals
  in place; the v1 product creates a new archive and does not perform in-place file moves.

## Architecture and persistent state

Preferred starting point: Python 3.12, FastAPI, SQLite, local file storage and a small
worker process. Reuse the existing vanilla HTML/CSS/JavaScript viewer to minimize new
dependencies. The implementer may choose an equally simple alternative and document why.
Pin dependencies after checking compatibility with trace-it's existing lockfile.

Use these separable services:

1. Intake: validate files, allocate IDs, compute hashes and persist originals.
2. Extraction: native PDF text or local OCR; preserve page sizes, orientation and boxes.
3. Classification: provider interface with Jev, rules and conventional-baseline adapters.
4. Review/routing: record human decisions and versioned queue mappings.
5. Export: generate manifests and archive confirmed originals.
6. Evaluation: use the same extraction/classification services with isolated data stores.

Persist batches, document records, extraction versions, classification runs, review
decisions, job attempts, policy/plan revisions, bulk-action events and export events. Keep raw provider responses in private runtime
storage with configurable retention. Store model inputs or their hashes with provenance.

Separate processing state (`queued`, `extracting`, `classifying`, `processed`, `failed`)
from review state (`pending`, `confirmed`, `excluded`). A candidate is not a confirmation.
Use transactions, foreign keys, timestamps and schema migrations.

For jobs, implement claim/lease or equivalent single-worker recovery. A restart must
recover interrupted work without losing completed extraction. Do not blindly retry a
provider request whose delivery or billing status is unknown. Mark that uncertainty
and permit an explicit retry. Honor known retryable statuses with bounded backoff.

For reuse caches, include the source hash, OCR configuration/version and model hashes;
for Jev include endpoint, model, prompt/taxonomy version and exact text. Expose cache hits.
Never report a cache hit's zero network time as a fresh-inference latency measurement.

### Proposed command contract

These commands are targets for implementation, not commands available at handoff:

```text
python -m document_router.web --host 127.0.0.1 --port 8770
python -m document_router.worker
python -m document_router.datasets prepare --manifest configs/rvl-sample.json
python -m document_router.evaluate --config configs/evaluation.json
python -m document_router.report --run <run-id>
```

The default app port is 8770 to avoid the receipt demo's 8765. Provide a documented
one-command way to launch the web app and worker together. Choose final commands once
the implementation exists and replace this section with tested examples.

### Local deployment boundaries

- Bind to loopback by default. Keep the provider key on the server and out of browser data.
- Reject unexpected origins/hosts for mutating browser requests and protect local uploads
  from cross-site requests. Document the local single-user trust model.
- Enforce configurable file, pixel, page, text and batch limits before costly work.
  Validate file contents; reject path traversal, unsupported formats and unsafe filenames.
- Handle image orientation and multi-frame TIFFs; decide and document whether each frame
  becomes a page. Limit decoded image sizes as well as upload sizes.
- Store documents outside served static files. Serve originals by validated document ID.
- Implement document/batch deletion for originals, derived text and associated cache records;
  describe any retention of audit metadata and exports.
- Give each worker bounded concurrency and provider request limits.
- A Docker deployment must document writable volumes, model setup and worker startup.
  Public multi-user hosting requires additional access control and is outside this release.

## Data and evaluation

### Sources and bounded acquisition

- Official dataset: <https://adamharley.com/rvl-cdip/>.
- Authors' Hugging Face link: <https://huggingface.co/datasets/aharley/rvl_cdip>.
- Full archive: 38,762,320,458 bytes; 400,000 images; 320,000 train, 40,000 validation,
  40,000 test. Do not download that archive for the initial evaluation.
- Inspect the current Hub schema and shard layout. Pin a revision and retrieve a bounded
  subset. Streaming or selecting rows can still transfer large shards; measure bytes and
  show a download plan first. Prefer metadata-driven selection before fetching images.
- Initial default transfer limit: 4 GiB across dataset downloads for this pilot. Enforce a
  configurable limit and report actual cache/disk use. If the provider cannot supply a
  bounded subset, finish the app using owned fixtures and document the acquisition block.
  Do not silently download the complete corpus.
- Keep images, OCR text, weights and dataset caches ignored. Track manifests with IDs,
  upstream splits, revisions, hashes, selection seed, labels and acquisition provenance.
- Check source redistribution terms before publishing examples. Existing access to
  Hugging Face does not grant additional dataset rights.

### Sampling protocol

Target 1,600 documents, 100 per upstream class, with a fixed seed such as 20260924:

| Partition | Per class | Total | Use |
|---|---:|---:|---|
| Upstream train | 40 | 640 | Develop rules and train a small text baseline |
| Upstream validation | 10 | 160 | Prompt selection and exploratory threshold tuning |
| Upstream test | 50 | 800 | Final frozen evaluation |

Select each class by a stable hash ordering of `(seed, source revision, upstream ID)`.
Commit the manifest before model development. Check cross-partition exact duplicates;
document removals/replacements before inspecting predictions. Keep transformations and
multiple pages from the same source document in its original partition.

Run a small train-only smoke test before the full sample. Choose the prompt and acceptance
policy using development data, freeze their hashes, then run the test partition once for
the initial report. Preserve failures and denominators. Later prompt changes require a
clearly identified new exploratory run; they do not create an untouched test set.

Before development, review a preselected small subset for label ambiguity and whether the
type is recoverable from OCR text. Keep metadata labels and reviewed judgments separately,
including reviewer identity and uncertainty. Assistant judgments are not human ground truth.
Never relabel examples merely because the model disagrees.

### Comparisons

Evaluate the same extraction and split manifest with:

1. A deterministic keyword/rule baseline with abstention.
2. A small character/word TF-IDF linear classifier trained only on the 640 train examples.
3. Jev with one frozen document-type question and explicit UNKNOWN support.

The small conventional baseline does not represent the best possible trained model.
Document feature choices and use development data for tuning. Do not train on the test
OCR text or derive rules from test failures.

Separate text-classifier results from full image-to-decision pipeline results. Human
reference transcriptions are not supplied by default in the RVL-CDIP image/label release;
our generated OCR is an input, not an OCR-accuracy ground truth. Report extraction failures.

Add a separate owned-fixture stress suite with blank pages, unreadable crops, commands
embedded in document text and out-of-taxonomy content. Record the expected abstention or
failure for each fixture. Do not mix this constructed suite into RVL-CDIP benchmark scores.
An absent annotation is not proof that a field is absent from an image.

### Measurements and cost controls

- Overall label agreement and macro-F1 on the frozen test sample; per-class precision,
  recall and confusion matrix. Count UNKNOWN as an abstention and pipeline errors as
  failures, with explicit denominators.
- Coverage versus error among non-abstained suggestions. The 16-class source has no
  representative UNKNOWN prevalence; use the separate stress suite to assess abstention.
- Median and p95 OCR, Jev and total processing latency. Separate cold model initialization,
  warm fresh inference and cached replay; report upload/render time separately if measured.
- Input/output tokens, known API usage and pricing source/date. Flag incomplete cost
  accounting when request delivery or provider usage is unknown.
- CPU time/storage where available; API cost alone is not total operating cost.
- User corrections and review duration in the app, clearly separated from benchmark accuracy.

Verify the current model ID, payload schema and provider prices before live evaluation.
The old project used `jev-1.13.0`, USD 0.042 per million input tokens and free output on
2026-09-24; these are historical reference values, not a promise about later availability.
Read credentials from the environment. Default the pilot's configured API estimate budget
to USD 1.00 across smoke/development/test requests, with bounded tokens and concurrency.
Show the estimate before a run and stop further requests when the budget would be exceeded.
Report that provider billing may differ from estimates, especially after uncertain delivery.

Store raw runs privately and produce sanitized aggregate JSON/CSV/Markdown reports.
Regenerate published aggregates offline from permitted saved artifacts. Record corpus,
code, OCR, model, prompt and taxonomy versions; make replay versus fresh inference explicit.

## Implementation phases

### Phase 0: inspect and establish contracts

- [ ] Inspect pinned sources, dependency compatibility and provenance/license status.
- [ ] Inspect RVL-CDIP schema, classes, shard sizes and download feasibility.
- [ ] Define schemas, taxonomy, versioned route mapping and provider interface.
- [ ] Add packaging, pinned dependencies, environment template and owned fixtures.
- [ ] Record decisions and implementation status without claiming unrun results.

### Phase 1: complete the application workflow

- [ ] Persist batches, originals, jobs, extractions, suggestions, corrections and exports.
- [ ] Implement upload, image/text/PDF/TIFF reading and worker restart recovery.
- [ ] Build inbox, viewer, confirmation, queue mapping and ZIP/CSV/JSON export.
- [ ] Implement folder import, plan preview/diff, group correction/undo and portable ledger.
- [ ] Implement deletion, exact-duplicate warnings and per-document retry.
- [ ] Verify the full path with deterministic owned fixtures and label fixture providers.

### Phase 2: integrate real OCR and Jev

- [ ] Add the pinned trace-it submodule or document a justified compatible integration.
- [ ] Reuse and adapt the Jev client; validate the live provider schema.
- [ ] Show real costs, timing, cache provenance and separate failure reasons.
- [ ] Exercise a fresh image OCR + Jev run and a direct-text run when credentials exist.
- [ ] Confirm that reprocessing does not overwrite human decisions.

### Phase 3: prepare and evaluate the pilot

- [ ] Acquire the bounded sample and commit its manifest before tuning.
- [ ] Implement rules and TF-IDF baselines and a frozen Jev prompt.
- [ ] Complete train/validation work, then the 800-document test run within budget.
- [ ] Publish aggregate results, error analysis and data/representation limitations.
- [ ] Run the owned handover scenario from PRODUCT.md and report its separate workflow results.
- [ ] Verify that the offline report reproduces the stored aggregate results.

### Phase 4: verify and hand over

- [ ] Browser-test upload, progress, image/text selection, corrections, persistence,
      retry, queue configuration, exports, deletion and empty/error states.
- [ ] Check actual viewport widths 360, 768, 1280 and 1920 pixels, plus 125% and 200%
      browser zoom. Confirm that controls and text remain reachable without clipping.
- [ ] Inspect the browser console and relevant network errors; keyboard-test review controls.
- [ ] Verify clean installation and startup, live configuration and persistent volumes.
- [ ] Write README setup, deployment, architecture, dataset, evaluation and provenance docs.
- [ ] Add a short demo recording if tooling permits, with fresh/recorded behavior identified.
- [ ] Review the diff, run required checks, commit and push; report exact remaining limits.

## Required verification

Prioritize tests that protect the product's behavior:

- A mixed batch containing a valid image, text, PDF, TIFF, duplicate and invalid file
  preserves individual outcomes and can reach export for confirmed documents.
- Server/worker restart preserves progress and recovers interrupted jobs safely.
- Human correction survives reload, reclassification and export.
- Queue changes have explicit effects; export uses confirmed decisions and safe paths.
- A mapping-only policy revision changes the correct preview rows with zero provider calls.
- Group correction lists its complete affected set; undo detects conflicts with later edits.
- Folder import retains safe relative-path provenance and resolves duplicate output names.
- Export snapshots, the HTML ledger and checksum verification agree after concurrent edits.
- OCR/provider failures remain distinct from UNKNOWN and do not count as successful routing.
- File limits, traversal attempts, cross-site mutation attempts and unsafe CSV cells fail safely.
- Credentials never appear in browser payloads, logs, exports or committed artifacts.
- Deletion removes document content and linked extraction/provider-cache data as documented.
- Test partitions never enter baseline training or prompt selection.
- A fresh-inference browser run matches its persisted metrics and provenance.

If credentials or dataset access are unavailable, complete all independent functionality
and mark the affected live checks as unverified. Do not substitute simulated provider
responses in a report labelled live. Do not claim the full definition of done in that case.

## Definition of done

The implemented release is ready for local pilot use when a new user can install it
from the repository, upload a mixed batch, inspect real extractions and suggestions,
correct decisions individually and in groups, preview a policy change, restart the service,
and export an organized archive whose contents match an immutable confirmed plan. A recipient
can read the ledger and verify the files without installing the app. The browser must fit the tested viewports without hiding
controls or table values.

The handoff must include tested commands, automated test outcomes, browser evidence,
dataset/provenance records, measured evaluation results or explicit access limitations,
and a candid assessment of Jev relative to both baselines. Accuracy targets are not
invented in advance. If Jev performs poorly, keep the app usable with review and report
the failure rather than changing the test set or hiding difficult classes.

The research question for this release is whether Jev supplies useful, reviewable
document-type suggestions. Product adoption and staff time savings require a later
pilot with real users and their document mix.
