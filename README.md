# Document Routing Workbench

A planned browser application for preparing a reviewed document handover from a
disorganized archive. A small technical consultancy can import project documents,
preview their destination folders, resolve uncertain decisions in groups, compare
routing-policy revisions and export a traceable delivery pack.

**Status: implementation handoff, 2026-09-24.** This repository currently contains
the specification and implementation plan. The application, dataset downloader and
evaluation commands still need implementation. No classification results have been
measured for this project.

## The user task

The first target user is the operations person in a small technical consultancy
preparing an archive for a client or an internal project handover. They have mixed
scans, PDFs and text files, an agreed destination structure, and responsibility for
checking what the recipient will receive. The first version uses a local workspace.
The user supplies project context; the app must not guess a client from weak clues.

## Product distinction

The product centers on a **reviewable handover plan**: source files, proposed output
paths, unresolved decisions, policy changes and the exact contents of the delivery.
OCR, classification, confidence scores and manual review already exist in competing
products. Our proposed differentiation combines:

- A before/after folder preview and a diff between routing-policy revisions.
- Group review with exact affected-document lists and reversible batch corrections.
- A portable delivery pack with originals, hashes and a human-readable decision ledger.

These features are release requirements. Their market value remains a hypothesis
until users compare this workflow with their current tools. Read
[PRODUCT.md](PRODUCT.md) for the competitor review, target scenario and validation gates.

The first release must support this complete path:

1. Create a batch and upload several supported files.
2. Follow persistent processing progress, including individual failures.
3. Open a document beside its extracted text and selectable OCR boxes.
4. Inspect Jev's proposed type, change it if needed, and confirm a destination queue.
5. Return after a browser or server restart and find the same decisions.
6. Compare destination plans, resolve collisions and export a verified handover pack.

## Jev's role

The local OCR reads pixels. Jev receives extracted or supplied text and proposes a
document type from a versioned taxonomy. Application rules map confirmed types to
destination queues. Users review suggestions before routing in the initial release.
Unknown content and processing failures have separate states.

The product must retain the evidence needed to judge whether Jev helps. Compare it
against a rules baseline and a small conventional text classifier. Report mistakes,
abstentions, latency, costs and the corrections made during review. A model
probability is not measured accuracy.

## Initial classification scope

Use the 16 RVL-CDIP classes plus `UNKNOWN`: letter, form, email, handwritten,
advertisement, scientific report, scientific publication, specification, file
folder, news article, budget, invoice, presentation, questionnaire, resume and memo.
See [the exact identifiers and category contract](PLAN.md#taxonomy-and-routing).

Some categories depend on layout or handwriting that a text-only classifier cannot
observe. Keep these cases in the evaluation, measure per-class failures and permit
abstention. The first release does not promise receipt extraction, expense policy
decisions or category coverage beyond this taxonomy.

## Reuse the existing work

| Source | Reuse |
|---|---|
| [Jev receipt country classifier](https://github.com/Kripta-Studios/jev-receipt-country-classifier) | Jev HTTP client, OCR adapter, document viewer behavior, metrics and evaluation practices |
| [trace-it](https://github.com/Martinhdeez/trace-it) | Local OCR implementation, pinned model setup and dependency definitions |

Start from receipt-project commit
`f5ca51cebed1a2819a5f571e1058bf3708cf2144` and trace-it commit
`84c4c0463862640940efb1232344287a2d03bcf5`. The [reuse inventory](PLAN.md#reuse-inventory)
identifies files and the changes they need.

On the original development machine:

```text
~/Desktop/KriptaStudios/document-routing-workbench
~/Desktop/KriptaStudios/Jev_Ticketing_Classfication
~/Desktop/KriptaStudios/Reto_Maisa/trace-pay-main
```

The receipt project also contains the pinned source under `external/trace-it`.
Treat the older standalone trace-it checkout as a reference whose revision must be
checked. Keep both source repositories and their published evaluation artifacts intact.
The finished application must work on a fresh machine without those sibling paths.

## Dataset plan

[RVL-CDIP](https://adamharley.com/rvl-cdip/) contains 400,000 grayscale document
images across 16 classes. Its official archive is 38,762,320,458 bytes. Begin with
a reproducible 1,600-document sample, 100 per class, preserving the upstream splits.
Record source revisions, sample identifiers and hashes. Sampling and storage limits
are specified in [PLAN.md](PLAN.md#data-and-evaluation).

Dataset availability does not establish redistribution permission. Check the original
dataset terms before publishing images. Store downloaded data outside Git and bundle
only owned fixtures or examples with verified redistribution permission.

RVL-CDIP measures document classification. It does not establish business usefulness,
staff time saved, real duplicate prevalence or performance on modern expense receipts.

## Implementation handoff

Open this folder in a new Codex session and ask the agent to implement
[PLAN.md](PLAN.md). Read [AGENTS.md](AGENTS.md) and [PRODUCT.md](PRODUCT.md) first. The plan defines architecture,
milestones, verification, an evaluation protocol and completion criteria.
Use [NEXT_AGENT_PROMPT.md](NEXT_AGENT_PROMPT.md) for the complete implementation prompt.

All source code, UI copy, documentation, tests and committed reports must use English.
Real user documents may retain their original language.

At handoff, Git commands are the only setup commands that exist:

```powershell
git clone https://github.com/Kripta-Studios/document-routing-workbench.git
cd document-routing-workbench
git status
```

The implementation agent must replace this status section with tested installation,
execution and deployment instructions for Windows PowerShell and Linux/macOS.
Keep offline demonstration, live inference and benchmark reproduction separate.

## Credentials and data

Supply `TYPESAFE_API_KEY` through the server environment when live inference is ready.
The environment may also need an authenticated Hugging Face session for dataset access.
Do not commit credentials or copy tokens from the previous conversation into files.
OCR runs locally; live Jev classification sends document text to TypeSafe.

The initial deployment binds to localhost. Shared hosted access requires a later
authentication and access-control design. The implementation plan defines local
storage, export, deletion and request boundaries.

## Sources

- [Receipt-project architecture and limitations](https://github.com/Kripta-Studios/jev-receipt-country-classifier/blob/f5ca51cebed1a2819a5f571e1058bf3708cf2144/docs/ARCHITECTURE.md)
- [Receipt-project OCR provenance](https://github.com/Kripta-Studios/jev-receipt-country-classifier/blob/f5ca51cebed1a2819a5f571e1058bf3708cf2144/docs/OCR.md)
- [Receipt-project deployment guide](https://github.com/Kripta-Studios/jev-receipt-country-classifier/blob/f5ca51cebed1a2819a5f571e1058bf3708cf2144/docs/DEPLOYMENT.md)
- [RVL-CDIP authors and download information](https://adamharley.com/rvl-cdip/)
- [RVL-CDIP on Hugging Face, linked by its authors](https://huggingface.co/datasets/aharley/rvl_cdip)
- [TypeSafe documentation](https://docs.typesafe.ai/)
