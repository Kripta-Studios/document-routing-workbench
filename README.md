# SourceCheck

A planned browser application for checking whether invoice ingestion preserves the
information in the original document. Compare a PDF, image or electronic invoice
with actual importer output, inspect discrepancies at their source, and repeat
the check when an importer changes.

**Status: specification only, 2026-09-24.** No SourceCheck application, downloader,
benchmark or deployment command has been implemented or executed here. Product value
and Jev's contribution are hypotheses. [RESULTS.md](docs/RESULTS.md) records this status.

The GitHub repository is
[Kripta-Studios/sourcecheck](https://github.com/Kripta-Studios/sourcecheck).
SourceCheck is the product name. This plan supersedes archive handover,
country/type classification and the intermediate document-resubmission proposal.
Git history preserves earlier plans; they are not additional release requirements.

## Who it helps

Start with small ERP integrators and developers maintaining invoice import pipelines.
They need to check whether a connector update preserves references, dates, amounts,
line descriptions and payment instructions. A successful import or valid XML alone
does not demonstrate that every required item reached the intended destination.

Example, not an observed result: an invoice contains a purchase-order reference
and a direct-debit instruction. The importer retains the total but omits those
items. Show the source evidence, inspected destination fields and mapping profile.

An export may hide information the ERP actually stores. Report **not observable in
this export** unless the destination contract establishes absence.

## Proposed workflow

1. Upload an original and its actual importer output, or run the supported local adapter.
2. Review the destination mapping and coverage profile.
3. Inspect native text, XML facts and OCR regions alongside destination values.
4. Review deterministic differences and optional Jev semantic suggestions.
5. Save a reviewed reference case and compare a subsequent importer run.
6. Export a reproducible discrepancy report with provenance and integrity checks.

The first local release closes this loop using Mustang as a real importer and an
uploaded JSON destination format, with an explicit CSV mapping path. Odoo integration
is a later milestone. Testing Mustang does not establish behavior in an ERP database.

## Proposed distinction

Combine invoice-specific source-to-destination checks, visual evidence, semantic
comparison of text and reusable regression cases. Validators, ETL testing tools and
trace-it overlap with parts of this workflow. We have not established exclusivity,
market demand, lower costs or superior accuracy. Read [PRODUCT.md](PRODUCT.md) and
[RESEARCH.md](docs/RESEARCH.md).

## Jev's role

Local parsers and OCR read the source. Code checks identifiers, amounts, dates,
coverage and configured mappings. Jev may compare bounded source/destination text
and suggest equivalent, contradictory, partially preserved or insufficient evidence.
A person reviews semantic findings.

Jev does not calculate totals, certify compliance, recover invisible data, generate
source coordinates or authorize payments. Live use sends selected text to TypeSafe.
Local OCR does not make the entire pipeline local. The app must work without live Jev.

## Implementation handoff

| Document | Purpose |
|---|---|
| [PRODUCT.md](PRODUCT.md) | User task, competition, scope and pilot gates |
| [PLAN.md](PLAN.md) | Contracts, architecture, phases and acceptance |
| [DATASETS.md](docs/DATASETS.md) | Sources, revisions, sizes and acquisition |
| [EVALUATION.md](docs/EVALUATION.md) | References, splits, baselines and metrics |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Target commands and installation verification |
| [PROVENANCE.md](docs/PROVENANCE.md) | Reuse inventory and licenses |
| [RESULTS.md](docs/RESULTS.md) | Collected evidence and missing measurements |
| [NEXT_AGENT_PROMPT.md](NEXT_AGENT_PROMPT.md) | Prompt for the implementation session |

All code, UI, documentation and reports use English. Preserve source documents in
their original language. Agent instructions are in [AGENTS.md](AGENTS.md).

## Reuse and storage

Reuse the receipt-project Jev client, OCR adapter, viewer and measurement practices,
plus pinned trace-it OCR source. Preserve both reference repositories. Record every
adapted component and resolve relevant license questions.

The investigated initial bundle is approximately **370 MB** of source files, published
tools and existing OCR assets before runtimes, Git history and generated artifacts.
Allow **5 GB free** for the local MVP; allow **10â€“15 GB** with the later Odoo environment
when Docker is already installed. These are planning allowances, not measured
SourceCheck installation sizes. See [storage accounting](docs/DATASETS.md#storage-accounting).

## What can run today

Only repository/documentation operations exist:

```powershell
git clone https://github.com/Kripta-Studios/sourcecheck.git
cd sourcecheck
git status
```

The private repository requires authorized GitHub access. SSH is an alternative when
configured. The future web URL is `http://127.0.0.1:8770/`; this documentation update
does not start a server.

The implementer must supply tested fresh-machine setup, sample acquisition, offline
demo, live Jev, evaluation and export-verification commands.
[DEPLOYMENT.md](docs/DEPLOYMENT.md) labels all proposed commands as unavailable today.

## Credentials and files

Use server-side `TYPESAFE_API_KEY` from the environment or an ignored configuration
file. Never copy credentials from conversation history. Keep originals, OCR text,
provider responses, databases, models and downloaded corpora outside Git. Commit
only reviewed, permitted fixtures and sanitized reports.
