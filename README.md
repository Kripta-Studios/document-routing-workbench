# SourceCheck

SourceCheck is a local browser app for checking whether invoice imports preserve
configured facts. It reads original XML independently of the importer, captures
actual output from pinned Mustang versions or a supplied JSON/CSV export, and shows
source evidence beside destination paths. A reviewer can record decisions, save a
reference case, rerun after an importer or profile change, and export a verifiable ZIP.

The local MVP runs at **http://127.0.0.1:8770/**. It is a single-user development
tool. It does not certify invoice compliance, perform payments, or prove what an ERP
stores beyond the inspected export. [PRODUCT.md](PRODUCT.md) describes the intended
users and later pilot gates; [RESULTS.md](docs/RESULTS.md) contains actual evidence.

## Quick start

The tested Windows setup used Python 3.12.13 via `uv`, Java 25 with Java 21 bytecode,
and the pinned `uv.lock`:

```powershell
uv venv --python 3.12 .venv
uv sync --frozen --extra test
.\.venv\Scripts\python.exe -m sourcecheck datasets prepare --dry-run
.\.venv\Scripts\python.exe -m sourcecheck datasets prepare
.\.venv\Scripts\python.exe -m sourcecheck models prepare --dry-run
.\.venv\Scripts\python.exe -m sourcecheck models prepare
.\.venv\Scripts\python.exe -m sourcecheck doctor
.\.venv\Scripts\python.exe -m sourcecheck demo prepare --mode offline
.\.venv\Scripts\python.exe -m sourcecheck serve --host 127.0.0.1 --port 8770
```

`uv sync` installs the Python package. The acquisition commands put two pinned
Mustang CLI JARs, one private upstream smoke sample and the small pinned Latin OCR
weights in ignored local storage. Each command checks transfer bounds, file sizes and
SHA-256 hashes. The demo performs **real local Mustang imports** on an owned XML
fixture, while “offline” means no Jev request or network call after bootstrap. The
downloaded ConnectingEurope sample is kept outside Git because its individual
document redistribution rights were not established.

The equivalent POSIX command shape is `uv venv --python 3.12 .venv`, `uv sync
--frozen --extra test`, then `.venv/bin/python -m sourcecheck ...`. Native Linux
and macOS installation has not been exercised; see
[DEPLOYMENT.md](docs/DEPLOYMENT.md) for the precise status and container setup.

## Use the app

1. Create a case from XML, PDF, PNG or JPEG. XML is parsed without DTDs/entities;
   native PDF text and local OCR are distinct observations. Hybrid PDF embedded XML
   is kept as a separate representation.
2. Review the mapping profile. A check states its source selector, destination
   path, requirement and coverage. Saving a profile creates a version.
3. Run Mustang 2.26.0 or 2.24.0, or upload JSON/CSV. Uploaded output has unverified
   execution provenance. It needs a reviewed per-field coverage contract to treat
   absent paths as missing; CSV also needs an explicit column/entity/locale mapping.
4. Select findings to inspect raw/normalized values and source evidence. PDF/image
   pages support navigation, zoom and fit; OCR regions are selectable. Enter reviewed
   source facts for non-XML documents without inventing coordinates.
5. Record a disposition and reason. Save a reference explicitly. Reruns keep older
   reviews as history and show changes without inheriting approval.
6. Export a report ZIP and verify it independently:

```powershell
.\.venv\Scripts\python.exe -m sourcecheck report --run RUN_ID
.\.venv\Scripts\python.exe -m sourcecheck verify-export .runtime/exports/EXPORT_ID.zip
```

The report contains a snapshot, findings CSV, self-contained HTML, provenance and a
SHA-256 manifest. Integrity checks prove archive consistency, not the truth of the
business facts. Server-side deletion removes local originals, derived outputs,
reviews, references and exports; downloaded ZIPs remain outside its control.

## Verification and limits

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m sourcecheck evaluate --config configs/evaluation.json --dry-run
.\.venv\Scripts\python.exe -m sourcecheck evaluate --config configs/evaluation.json
.\.venv\Scripts\python.exe -m sourcecheck storage inspect
```

The functional suite uses owned, constructed mutations. The real importer comparison
currently covers two source families and two Mustang versions; it is too small for
accuracy claims. Mustang's narrow bridge exposes selected identifiers, dates,
references, payment fields and line items. Declared totals are unobserved through
this bridge, even when present in the XML. An old version returning a null reference
is reported in the scope of this inspected bridge, not generalized to ERP behavior.

Jev 1.13.0 can optionally suggest a relation for a bounded text pair after explicit
selection. Its request preview shows the text sent to TypeSafe. A server-side
`TYPESAFE_API_KEY` is required; a configured key does not trigger calls by itself.
Four constructed development pairs were tested live and matched their authored
labels; this does not establish performance on real invoices. Use `--key-stdin`
with `serve` or `evaluate --live-jev` to enter the key through a masked prompt
without saving it. A timeout keeps an unknown-delivery reservation and is not
silently retried. See
[EVALUATION.md](docs/EVALUATION.md) and [RESULTS.md](docs/RESULTS.md).

Private runtime data, corpora, model files, JARs, caches and outputs stay outside
Git. The two inspected sibling repositories are never required for a fresh install.
Their pinned revisions and licensing limitations are recorded in
[PROVENANCE.md](docs/PROVENANCE.md). Odoo stored-data comparison and customer pilots
remain later gates.
