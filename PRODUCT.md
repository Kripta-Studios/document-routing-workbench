# Product direction

Date: 2026-09-24. Status: hypothesis and proposed release requirements.

## User and task

Start with a small ERP integrator or developer maintaining invoice ingestion.
Before accepting an integration or deploying an update, they need to check whether
the destination preserves required facts and instructions.

Input: original invoice, actual importer output, reviewed mapping/coverage profile.
Output: source-linked findings, human dispositions and a reusable regression case.

The technical-consultancy archive handover and resubmission ideas are retired.
The product and repository name is SourceCheck (sourcecheck on GitHub).

## Evidence and limits

Public reports describe unused order/delivery references, selective extraction and
recalculated source values. Reproduce specific reported behavior; do not generalize
it to all installations. Some reports concern fixed bugs or disputed interpretations.
[RESEARCH.md](docs/RESEARCH.md) preserves source links and qualifications.

No customer interviews, paid pilots or SourceCheck executions have taken place.
Internet research does not establish product-market fit.

## Proposed distinction

Show what arrived, where it appears in the inspected destination, and which required
items differ or cannot be checked. Reproduce that check after a connector, schema,
mapping or OCR change.

Required capabilities:

- Invoice-specific mapping and coverage profiles.
- Original-page/XML evidence beside destination fields.
- Meaning-preserving and contradictory text comparisons with review.
- Saved reference cases and diffs across importer runs.

These are planned capabilities, not exclusive inventions.

## Alternatives and overlap

| Alternative | Existing capability | Proposed focus |
|---|---|---|
| trace-it | Ingestion, decisions, evidence, versions and stale-decision alerts | Test the import pipeline itself; trace-it can be a system under test |
| QuerySurge / ETL testing | Source/target data validation | Invoice evidence across pages, structured facts and free text |
| ZUGFeRD Validator | Format validation and documented PDF/XML field checks | Actual destination output, coverage and repeatable importer checks |
| ERP connectors and test suites | Format-specific ingestion and regression tests | Reviewable cross-representation evidence and portable reports |
| Xenett / Keeper | Client questions and document workflows | Integration acceptance |
| Numerint / backup tools | Export data and attachments | Preservation checking |

See [RESEARCH.md](docs/RESEARCH.md). Do not claim that competitors cannot implement
these features. Recheck capabilities before writing marketing claims.

## First release

Local single-user browser application, port 8770:

1. Upload PDF, PNG/JPEG or XML plus destination JSON/CSV.
2. Run a pinned Mustang adapter to obtain genuine importer output.
3. Review a profile defining required facts and destination coverage.
4. Inspect findings and original evidence.
5. Confirm, dismiss or leave findings unresolved with reasons.
6. Save a reviewed case and compare a subsequent importer run.
7. Export an integrity-checked report and reproduce permitted metrics offline.

Unsupported fields remain explicit. A limitation in our adapter is not proof of an
importer failure. Odoo 19 and PostgreSQL are a later milestone; its output must be an
actual stored-data snapshot, not an authored JSON fixture.

## Demonstration

Create owned, labeled examples covering:

- An unchanged invoice and an equivalent normalized date.
- An omitted required order reference and a changed amount.
- Equivalent and contradictory payment instructions.
- An export whose field coverage is unknown.
- Repeated line items without unique alignment.
- An unreadable region and malformed XML.
- A profile update, rerun and retained human disposition.
- Restart recovery and consistent export.

Label fixture simulation, real importer execution, cached replay and live Jev
separately. Functional demonstration does not estimate customer accuracy.

## Pilot and decision gates

After the MVP, recruit three integrators with permitted examples. Compare equivalent
acceptance/diagnosis tasks against their current tools, counterbalance order and
include setup, mapping, corrections and report effort in elapsed time.

Proposed targets, not results:

- At least 30% lower median diagnosis time without more unresolved important errors.
- Source facts and destination paths that users can independently inspect.
- At least two participants choose the tool for another integration change.
- Evidence of willingness to pay from actual pilot conversations.

Hard risks: destination access, coverage, line alignment, source ambiguity, mapping
maintenance and false alarms. Jev is optional. If rules perform as well, keep rules
and report the outcome.

## Scope exclusions

The MVP does not execute payments, write to a production ERP, provide tax advice,
certify compliance, route general archives or provide multi-tenant hosting.
Keep the adapter contract narrow. Expand only after the core workflow proves useful.
