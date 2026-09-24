# Reuse and provenance

Status: reuse plan. No upstream code has been copied into SourceCheck yet.

## Pinned references

| Repository | Revision | Reference |
|---|---|---|
| Receipt classifier | f5ca51cebed1a2819a5f571e1058bf3708cf2144 | https://github.com/Kripta-Studios/jev-receipt-country-classifier |
| trace-it | 84c4c0463862640940efb1232344287a2d03bcf5 | https://github.com/Martinhdeez/trace-it |

Original workstation locations:

```text
~/Desktop/KriptaStudios/sourcecheck
~/Desktop/KriptaStudios/Jev_Ticketing_Classfication
~/Desktop/KriptaStudios/Reto_Maisa/trace-pay-main
```

The receipt repository contains the pinned trace-it submodule at external/trace-it.
The older standalone checkout is a reference only; inspect its revision before use.
SourceCheck installation must never require these sibling paths.

## Component inventory

| Existing path in receipt repository | Intended reuse / adaptation |
|---|---|
| jev_tickets/client.py | Typed HTTP validation, bounded retries, cache identity and usage records |
| jev_tickets/ocr.py | TraceReader integration, EXIF handling, native-PDF/OCR choice and coordinates |
| jev_tickets/static/app.js | Image selection, page/zoom/fit behavior; replace country-classification workflow |
| jev_tickets/static/style.css | Responsive viewer patterns, verified in new layouts |
| jev_tickets/web.py | Intake limits and metric semantics; replace transient playground services |
| jev_tickets/metrics.py and evaluation.py | Reuse generic calculations only after inspecting their task assumptions |
| research/evaluate_observable.py | Provenance, failure accounting and offline report practices |
| docs/OCR.md and docs/DEPLOYMENT.md | Model provenance, dependencies and fresh-machine setup knowledge |
| docs/WEB_VALIDATION.md and docs/JEV_USAGE.md | Browser verification and provider integration lessons |

Inspect actual APIs and files at the pinned commits before porting. Replace ISO-country
labels and prompt-comparison UI with observation, coverage and semantic-relation
contracts. The old metadata agreement and reviewed receipt results apply to a different
task and cannot be reused as SourceCheck performance.

## Integration rules

- Port small generic components into the sourcecheck namespace where authorized.
- Retain trace-it as a pinned submodule only if its source remains a runtime dependency.
  A submodule is not required merely to cite models or inspect documentation.
- Do not add the whole receipt experiment as a runtime submodule.
- Record source path, commit, original hash, local modifications and license status
  for each reused component.
- Reuse existing OCR weights only after verifying provenance and hashes; provide
  a documented fresh download path for another machine.
- Do not copy virtual environments, ignored evaluation caches or unrelated services.
- Avoid generic Python package names that conflict with trace-it's app package.

## Licensing status

The initial pinned-source inspection found no tracked LICENSE file in either reference
repository. Public GitHub visibility does not establish general redistribution rights.
The user's authorization covers work on their project; document the external-code
license gap and resolve relevant redistribution permission before distributing copied
external code. Continue independent implementation and source inspection meanwhile.

Upstream dataset/tool declarations inspected on 2026-09-24:

| Source | Declared license / qualification |
|---|---|
| ConnectingEurope EN16931 | EUPL-1.2 in LICENSE.txt |
| Mustangproject | Apache-2.0 |
| KoSIT validator/configuration | Apache-2.0 |
| ZUGFeRD corpus repository | Apache-2.0; check individual third-party documents/notices |
| alyf-de/eu_einvoice | GPL-3.0; optional integration |
| Odoo/PostgreSQL images | Preserve applicable software and image notices; inspect selected versions |

This inventory is not a blanket license for every fixture or dependency. Keep a
per-artifact origin and redistribution decision. Do not publish private invoices
merely because a technical evaluation used them.

## Implementation provenance deliverables

Add a machine-readable source manifest with URL, resolved commit/tag/digest, hashes,
byte counts, license/notice paths and acquisition time. Add model identifiers,
normalization/comparator versions, mapping versions, bridge build identity and Jev
criteria/model versions to each run.

Distinguish upstream assertions, assistant interpretation, deterministic construction,
human review and actual execution. An integrity hash does not establish source truth.
