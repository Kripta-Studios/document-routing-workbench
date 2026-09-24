# Product direction and differentiation

Date: 2026-09-24. Status: product hypothesis and release requirements.

## Target user and job

Start with an operations coordinator in a small technical consultancy who prepares a
project archive for a client or another team. Source files arrive as mixed scans, PDFs
and text. The coordinator needs to agree on a folder structure, resolve uncertain
assignments and deliver a pack whose contents another person can check.

The user supplies the project identity and destination policy. The application proposes
document types from text, shows the consequences of those suggestions and records review.
The first release handles one local workspace and produces a new delivery archive.

This target segment is a design choice, not the outcome of customer interviews. Validate
its document mix and willingness to use the workflow before claiming product-market fit.

## Competitive review

Official sources checked on 2026-09-24:

| Alternative | Documented capabilities | Consequence for our design |
|---|---|---|
| [Paperless-ngx](https://docs.paperless-ngx.com/usage/) | OCR-based document management, content matching, suggested types/tags/storage paths and workflows | Local document management and automatic folder suggestions already exist. |
| [Rossum](https://knowledge-base.rossum.ai/docs/configuring-automation-in-rossum) | Configurable automation levels and confidence-based validation with human review | Confidence displays and review queues are standard capabilities. |
| [Docsumo](https://www.docsumo.com/) | Collection, classification, extraction, verification and document/case workflows | A generic document pipeline has established competitors. |

These pages establish advertised capabilities. They do not prove the absence of similar
handover features in those products. The proposed distinction is a focused workflow and
delivery artifact; we have not established an exclusive technical invention.

## The proposed distinction

Optimize the whole application around a reviewed archive handover. A user should be able
to answer these questions before downloading the delivery:

- Which source file will appear at each output path?
- Which assignments came from a person, a rule or a model suggestion?
- Which files would move to a different output folder if the policy changed?
- Which decisions remain unresolved, and what must I inspect to resolve them?
- Can the recipient verify the delivered originals and read the review history?

The deliverable is a versioned handover plan and its verified archive. The model's type
prediction is an intermediate input. The application should remain useful if Jev's
suggestions require correction or a conventional baseline performs better.

## Three required capabilities

### 1. Preview the consequences of a policy change

The main workspace shows the source tree and proposed destination tree with counts,
unresolved documents and collisions. Selecting a file opens its image/text and decision.

Example: a coordinator changes `specification -> Archive` to `specification -> Technical`.
The app shows the exact documents and paths affected, preserves manual overrides, and
creates a new plan revision after confirmation. It reuses the classifications and makes
zero Jev requests for this mapping-only change.

### 2. Resolve repeated work in groups

Group documents by transparent properties such as candidate type, destination or issue.
The user can inspect members, select the intended set and apply a correction once.
Before applying it, show the affected documents and conflicting existing decisions.

Every group action records its affected IDs and supports undo. Undo must account for
subsequent edits. One corrected document does not silently relabel other documents or
train a model. Rule creation is a separate action with its own preview.

### 3. Deliver an independently readable pack

Produce organized originals plus CSV/JSON manifests, hashes and an HTML decision ledger.
The recipient can view the ledger without the running application and verify file integrity.
The export identifies its immutable policy and plan revisions and excludes unresolved
documents while reporting them in the manifest.

Keep source files unchanged. A later revision produces another pack with a visible diff.
Do not promise filesystem rollback: v1 performs no in-place filesystem reorganization.

## Jev's place in the product

Use Jev to suggest types for heterogeneous extracted text where simple rules may have
low coverage. Measure whether those suggestions reduce human correction effort. Jev
receives document text and versioned class definitions; the application owns policies,
paths, group actions and export decisions.

The first release requires human confirmation. Its differentiating features must work
with any provider adapter. If Jev loses to a baseline on this task, report that outcome
and retain a useful review/export tool. The source of an inference must remain visible.

## Product demonstration scenario

Create 24 owned English fixtures representing a technical project archive. Include
native PDFs, rendered scans and text. Include invoices, specifications, reports,
correspondence, presentations and forms, plus exact duplicate occurrences, an unreadable
document and an ambiguous document. Choose and document the exact composition before
running the product demonstration. Mark these fixtures as authored, not real customer data.

Give the fixtures a reviewed expected destination manifest based on an explicit policy.
The project name is user-supplied. Define the expected behavior for ambiguous and failed
documents as review, and include an output-name collision.

The scenario must demonstrate:

1. Import a folder and preserve its relative paths in provenance.
2. Process the batch, keeping failures and duplicates visible.
3. Correct an intentionally wrong fixture suggestion and a selected group of suggestions.
4. Change a destination mapping and inspect the exact plan diff.
5. Undo a group action; exercise a conflict caused by a later individual edit.
6. Restart the app and retrieve the same plan and review state.
7. Export the confirmed revision, read its ledger and verify hashes outside the app.

Deterministic fixture-provider tests may inject known mistakes to verify correction logic.
Label those runs as simulated. A separate live demonstration must use genuine OCR and
Jev requests and report whatever mistakes or abstentions occur.

## Validation and decision gates

Keep three kinds of evidence separate:

| Evidence | What it can establish | Limitation |
|---|---|---|
| Frozen RVL-CDIP evaluation | Document-type agreement, abstention, latency and cost | Different distribution from project handovers; no destination labels |
| Owned handover scenario | Functional correctness, plan diffs, recovery and export integrity | Authored cases do not estimate customer accuracy or savings |
| Representative user pilot | Completion time, correction effort, destination errors and repeat use | Requires real users and permitted source documents |

Recruit three to five target users when possible. Observe their existing process and
compare completion of comparable batches with the app. Counterbalance task order and
avoid giving one approach a pre-reviewed version of the same documents. Include setup,
corrections and export verification in the timing. Treat results as a small pilot.

Initial product targets, not measured outcomes:

- At least 30% lower median handover preparation time than the user's current process.
- No increase in final destination errors on the evaluated batches.
- Complete source-to-export traceability and successful integrity verification.
- A recipient can inspect the pack without installing or trusting our running service.
- At least two pilot users choose it again for a subsequent batch.

Compare against manual folders and, where the user already uses one, a tool such as
Paperless-ngx. Do not infer savings from token costs or classifier accuracy alone.

If the focused workflow does not save work, revisit the segment or stop expanding it.
Do not respond by adding more model dashboards and calling them differentiation.

## Release priorities

The initial release requires plan preview/diff, grouped correction with undo, and the
portable ledger. Complete these before adding connectors, custom-trained models,
semantic near-duplicate detection, automatic routing, billing or multi-user hosting.

Keep RVL-CDIP's taxonomy in the evaluation. User-facing queues and output folders remain
configurable. Future customer-specific categories need their own definitions and labels;
their results cannot inherit RVL-CDIP scores.

## Claims the README may make after verification

- Users can preview and compare versioned output plans.
- Users can correct a defined group of documents and inspect or undo the action.
- Users can export verified originals with a portable decision ledger.
- OCR runs locally; Jev receives extracted text in live mode.

Claims requiring further evidence include superiority to competitors, calibrated safe
automation, financial return, customer time savings and accuracy on customer-specific
categories. Keep planned, tested and measured capabilities distinct in the documentation.
