# Data, tools and storage

Inspection date: 2026-09-24. These measurements describe upstream files and existing
local references, not a SourceCheck installation. No corpus or binary was acquired
as part of the documentation update.

MB means 1,000,000 bytes; GiB means 1,073,741,824 bytes. Git tree totals are logical
file sizes, excluding history, filesystem allocation and submodules. Release asset
sizes are their published download sizes. Do not use GitHub's repository size field
as a working-tree or ZIP measurement.

## Required sources

| Source | Observed revision | Files / bytes | Purpose |
|---|---|---|---|
| [ZUGFeRD/corpus](https://github.com/ZUGFeRD/corpus) | d891458e9822e34271a5438497bf924e89955979 | 250 files; 151,876,596 bytes | Hybrid/native invoice examples and deliberate errors |
| [ConnectingEurope/eInvoicing-EN16931](https://github.com/ConnectingEurope/eInvoicing-EN16931) | b6c9e06a59812fb1a83585da40923b3678a649ad | 525 files; 10,910,699 bytes | CII/UBL examples and validation artifacts |
| [Mustangproject](https://github.com/ZUGFeRD/mustangproject) | 7869b59a0ff17636355e4ed44a4518d190683155 | 635 files; 67,900,047 bytes | Importer source, adapter investigation and tests |

These are measured branch snapshots. For actual execution use the chosen release
tag/commit consistently across bridge API and binary. Recalculate sizes if selecting
a different source revision; do not imply the measured master snapshot equals a release.

The ZUGFeRD corpus contains 151 PDF files and 88 XML files. They are not necessarily
239 independent invoices: duplicates, representations and related variants exist.
Two large XML examples total 86,811,768 bytes:

- PEPPOL/Valid/Qvalia/Large_Invoice_sample1.xml
- PEPPOL/Valid/Qvalia/Large_Invoice_sample2.xml

Excluding them leaves 65,064,828 bytes. Reserve them for a separate large-input test;
the ordinary app limit intentionally rejects files over its configured limit.

ConnectingEurope has 15 files in cii/examples and 19 in ubl/examples, together
3,843,427 bytes. Its overall XML count includes supporting files; it is not an
invoice-example count. Mustang test resources occupy 14,490,682 bytes across 143
files and are already included in its source total.

Corpus labels and validator verdicts are not complete preservation references.
Construct source facts and expected destination relations independently.

## Published tools

| Artifact | Version | Download bytes |
|---|---|---:|
| [Mustang CLI](https://github.com/ZUGFeRD/mustangproject/releases/tag/core-2.26.0) | 2.26.0 | 59,163,641 |
| [Mustang CLI comparison version](https://github.com/ZUGFeRD/mustangproject/releases/tag/core-2.24.0) | 2.24.0 | 58,755,189 |
| [KoSIT standalone JAR](https://github.com/itplr-kosit/validator/releases/tag/v1.6.3) | 1.6.3 | 10,648,594 |
| [XRechnung configuration ZIP](https://github.com/itplr-kosit/validator-configuration-xrechnung/releases/tag/v2026-08-31) | 3.0.2 / 2026-08-31 | 499,607 |

The older Mustang release is for bounded regression investigation, not proof of an
existing defect. Run historical tools locally on permitted fixtures under resource
limits. Check compatibility and artifact hashes before use.

KoSIT's configuration is separate from its executable. The measured configuration
source tree is 998,587 bytes at bd160dc19ba7a1f5b73c148a7fff60bf111ab590; its release
ZIP replaces, rather than duplicates, the configuration source for normal execution.
Document validation scenario/version with each verdict.

## Already available reusable assets

Measured from tracked blobs at the pinned revisions or existing local files:

| Asset | Logical bytes |
|---|---:|
| Receipt project at f5ca51cebed1a2819a5f571e1058bf3708cf2144 | 20,599,552 |
| trace-it at 84c4c0463862640940efb1232344287a2d03bcf5 | 33,419,292 |
| Existing .cache/models OCR assets | 12,881,094 |
| Existing trace-it Python virtual environment, separate reference measurement | 439,381,894 |

The source totals exclude virtual environments and Git history. Do not copy the
virtual environment to another machine; rebuild from verified dependencies. There
are duplicate models/caches in old experiments: reuse explicitly configured verified
weights instead of copying the entire experiment cache.

Jev is hosted inference: no Jev model weights are planned for local download.
Trace-it's explicit Latin OCR configuration must be checked; installing a newer
RapidOCR package does not guarantee the same default models.

## Optional ERP integration

Use the official [Odoo Docker configuration](https://github.com/odoo/docker/tree/master/19.0).
Registry manifests inspected for linux/amd64:

| Image | Compressed layer bytes | Platform manifest digest |
|---|---:|---|
| odoo:19.0 | 697,563,402 | sha256:08af340902122af116a92c917359cd8bb411ca6960c0b4877dc636423a8d5b26 |
| postgres:16 | 160,275,130 | sha256:a85daf0dbd5e79586e850e3fe4b21b796799828ad015ce2166aeb98cc24da61c |

Sum: 857,838,532 bytes of compressed layers before cache reuse or shared-layer
deduplication. Installed layers, database volumes, runtime logs and Docker/WSL itself
are additional. Other architectures have different manifests and sizes.

A later ERPNext alternative is [alyf-de/eu_einvoice](https://github.com/alyf-de/eu_einvoice):
8,066,184 source bytes at 488ec68f1b6667bb4199d080ccc4fb8c4fd37d25. It needs compatible
ERPNext/Frappe and services. That source size is not a running ERP's footprint.
Do not install both ERP stacks for the initial MVP.

## Acquisition protocol

1. Generate a reviewed download plan with URL, revision, artifact name, planned bytes,
   extraction bound, license/provenance and intended evaluation use.
2. Use snapshot archives, selective downloads or shallow checkouts. Avoid full Git
   history. Do not assume a sparse working tree means a small network transfer.
3. Download into ignored data/ or external/tools/ with transport timeouts and bounds.
   Record actual transferred bytes including retries.
4. Verify published hashes where available; compute local SHA-256 for every artifact.
   A self-computed hash supports reproducibility, not independent authenticity.
5. Extract archives with traversal/symlink and decompression limits. Record actual
   extracted bytes and inventory; reject incomplete downloads.
6. Build family/representation manifests and freeze the evaluation split before tuning.
7. Preserve source notices and keep unreviewed documents/private output out of Git.

Default limits: 1 GiB dataset transfer, 4 GiB total new bootstrap transfer, USD 1.00
estimated live API usage. Treat these as cumulative run budgets. Show remaining
budget and stop before exceeding it. A larger budget must be explicitly configured.
Existing valid cache files can be reused by hash.

No acquisition commands are implemented yet. The proposed CLI in DEPLOYMENT.md must
support a dry run, pinned manifests and byte accounting before being advertised.

## Reference cases we must author

Store labels for source facts, observable destination fields, correspondence and
expected preservation results. Capture real outputs from the selected importer,
then annotate independently. Separate synthetic mutations from observed failures.

Cover legitimate normalization, missing required facts, changed exact values,
equivalent/contradictory text, incomplete exports, repeated lines, source conflicts,
unreadable evidence and unsupported profiles. Preserve provenance and reviewer type.
See [EVALUATION.md](EVALUATION.md).

## Sources outside the default download

- RVL-CDIP: document-type classification does not test import preservation.
- ARIES: academic review/edit alignment does not provide invoice import references.
- SROIE: optional OCR-only evaluation; 987 receipt images, approximately 510 MB
  compressed in the previously inspected mirror. Reverify revision and size before
  acquisition. It supplies no real importer outputs.
- DESCAN-18K: not required; restoration pairs do not label semantic import losses.

Do not expand downloads to increase an impressive-looking example count. Count unique
source families, checks and variants separately.

## Storage accounting

The initial bundle sum is 367,899,122 bytes: corpus, ConnectingEurope, Mustang source,
one Mustang JAR, KoSIT JAR, configuration ZIP, both reference source trees and OCR assets.
This mixes uncompressed source files with ready-to-use JAR/ZIP files; it is a planning
inventory, not a total network download or allocated-disk measurement.

Adding the comparison Mustang JAR gives 426,654,311 bytes. Excluding the two large XML
files saves 86,811,768 bytes. The existing reference source trees and models account
for 66,899,938 bytes and need not be downloaded again on the original machine.

Planning estimates, not installed measurements:

- Local MVP including runtimes and moderate generated output: 1.5–3 GB.
- Recommended free space for development: 5 GB.
- Later Odoo integration: reserve 10–15 GB with Docker already installed.
- Docker/WSL installation, long-term datasets and repeated container caches are extra.

Measure a fresh installation during implementation. Report transfer bytes, extracted
assets, environments, images, volumes, caches and generated artifacts separately.

## Licenses

ConnectingEurope declares EUPL-1.2. Mustang, KoSIT and the ZUGFeRD corpus repository
declare Apache-2.0. The ERPNext integration declares GPL-3.0. Check file-level notices
and originating document permissions; a repository license is not sufficient evidence
about every third-party invoice. See [PROVENANCE.md](PROVENANCE.md).
