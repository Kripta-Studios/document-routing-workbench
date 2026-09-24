# Reuse and provenance

Status: implementation inventory, 2026-09-24. No code from the two unlicensed
reference repositories was copied into SourceCheck. Their behavior and API shape
were inspected; SourceCheck adapters were written independently.

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

## Implemented inspection and artifact record

The local receipt and trace-it checkouts were read at the exact revisions above and
were not modified. Inspected source SHA-256 values:

| Inspected source | SHA-256 | SourceCheck counterpart |
|---|---|---|
| `jev_tickets/client.py` | `1816931283aaf1ecb5db32d62574bac4c6ab519e37971dec5f4586fca3ad9662` | Independent bounded client in `sourcecheck/jev.py` |
| `jev_tickets/ocr.py` | `d3e293d723f0c713750914b34b0932d3fae9ffbe68df7ab71bebc8dfba92e09d` | Independent reader in `sourcecheck/source.py` |
| `trace-it/.../ocr/local.py` | `9b8ee9d62747125d9871d4d7bd9441d168c4db6a77ae5df4ee184856febf6de5` | Explicit RapidOCR settings and pinned model files |

The receipt viewer and evaluation notes informed UI and measurement choices. No
source files, weights or caches from either reference tree are published in Git.
The receipt/trace-it code license gap remains relevant to any future direct copy;
this implementation does not rely on redistribution permission for that code.

Machine-readable plans are in `configs/sources.json` and `configs/models.json`.
Actual local acquisition records are ignored runtime files. The two Mustang JARs
were downloaded from `core-2.26.0` and `core-2.24.0`: SHA-256
`42d7868cb68264874a7b8cab4c3587b03b23ccc7cd72373da917f66758bb9736`
(59,163,641 bytes) and
`e4904ffa0afdce3f5836dceb927c440a05ed5d60386fdd37e17a4b2f7652edbf`
(58,755,189 bytes). The bridge source hash during the evaluation was
`982b9a25faf30b01faf48808264240b79e04c9c6f4e8d1041c9f60fb7b7f7b62`;
runs store their own bridge hash. Mustang declares Apache-2.0, and the CLI offers
`--action license` for its notices.

The private ConnectingEurope CII example is 10,178 bytes, SHA-256
`53a636ac10592aa6fdc280190a366955380a64883519a4d58926b96802eb7163`,
from revision `b6c9e06a59812fb1a83585da40923b3678a649ad`. Its repository declares
EUPL-1.2; individual invoice rights were not established, so the XML is excluded
from Git. The owned XML and rendered image fixtures are authored functional
examples, not customer or upstream ground truth.

The OCR detector and recognizer are from PaddlePaddle Hugging Face repositories at
the revisions in `configs/models.json`. Their model-card tags declare Apache-2.0.
Model hashes are
`a431985659dc921974177a95adcfbb90fd9e51989a5e04d70d0b75f597b6e61d`
and `7888113072263cb471b93f66dd5e2ad70548dc526fa1ace760d0d973dd121498`.
The derived `keys.txt` SHA-256 is
`5ddc5c6086d61db3e1485f1237e059b89df9a228cebdac40a54406c6005bca67`.
These files are ignored and independently downloadable; the model tags do not
establish accuracy on SourceCheck invoices.
