# Results and implementation status

Updated: 2026-09-24.

## Current state

This repository contains the SourceCheck specification and implementation handoff.
There is no SourceCheck application, downloader, importer bridge or evaluation run.

| Area | Status |
|---|---|
| Product/competitor investigation | Desk research completed; market hypothesis unvalidated |
| Public source/tool inventory | Metadata and revision/size inspection completed |
| Local reusable source/model inventory | Measured in the existing receipt workspace |
| SourceCheck dataset acquisition | Not performed |
| Independent reference annotations | Not created |
| SourceCheck backend/browser | Not implemented |
| Genuine Mustang adapter execution | Not performed |
| OCR/Jev pipeline evaluation | Not performed |
| Fresh-machine/container deployment | Not performed |
| Odoo stored-data comparison | Not performed; later milestone |
| Customer pilot, time savings, willingness to pay | Not measured |

## What the size measurements establish

DATASETS.md records logical Git-blob totals, published release sizes, registry layer
sizes and local reference-asset measurements. Git trees were non-truncated for the
listed small source repositories. Registry measurements fetched manifests, not image
layers. No new full corpus or ERP environment was downloaded for this research.

The approximately 370 MB initial inventory and 5 GB free-space recommendation are
different quantities. The latter is a planning allowance. No claim is made that
SourceCheck has been installed and measured.

## What must not be reused as results

- Receipt-country metadata agreement or prior manually/assistant-reviewed receipt scores.
- Classifier results from RVL-CDIP or academic edit alignment from ARIES.
- A corpus filename containing "valid" or "error" as a complete preservation label.
- Demonstration mutations as observed failures of a real importer.
- Provider confidence as measured correctness or customer time saved.

## Required structure for each future report

Record run ID/date, Git revision, environment/lockfile, corpus manifest hash, unique
families/splits, annotation provenance, tool/model/profile versions, mode
(simulated/actual importer/live/cached), denominators, failures and unobserved checks.

Include deterministic baseline versus Jev-extension results; fresh/cached timing;
API usage and uncertain billing; storage; error review; exact reproduction commands;
and the limits of public reproduction when source data cannot be redistributed.

Give an explicit conclusion: useful measured Jev contribution, no measured benefit,
or insufficient evidence. Keep technical evaluation, browser verification and customer
pilot results in separate sections. Update this page as evidence is actually produced.
