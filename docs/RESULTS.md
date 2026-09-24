# SourceCheck results and implementation status

Updated 2026-09-24. This page records actual implementation checks. Commands below
were executed on Windows 11 with Python 3.12.13, Java 25.0.2 and `uv.lock` unless
marked otherwise. Runtime artifacts and private source files are ignored by Git.

## Scope and conclusion

The local app can intake an invoice, execute either pinned Mustang importer, show
independent XML facts and destination paths, record review, rerun a saved case and
export a ZIP that verifies offline. Uploaded JSON/CSV and local OCR work under
explicit coverage limits. Six authored functional variants passed. Two independent
source families were run through two genuine Mustang versions each. These small
development cases establish functionality and one narrow version difference; they
do not estimate preservation accuracy or customer diagnosis time.

**Jev's measured value on real invoices: insufficient evidence.** Four live calls
on constructed development text pairs matched all four authored labels. Rules
abstained on those pairs; the lexical demonstration matched one label. This confirms
the bounded API path and a narrow semantic capability, but the pairs were not
independently reviewed or held out, and they are not a real-data model benchmark.
Odoo stored-data checks and customer pilots were not run.

## Technical runs

`python -m sourcecheck evaluate --config configs/evaluation.json` produced run
`46c3dc3a47c648e79ea19d6eddd05916` in ignored runtime storage. The family
manifest SHA-256 was `256b3a9c835bdf593f71a7832b09bb732961b002061618d30fd5d5b475821a37`.
Both families landed in the development partition. The frozen manifest was written
after implementation began; there is no untouched validation/test partition and no
held-out correctness claim.

| Suite | Attempted | Observed result |
|---|---:|---|
| Authored functional variants | 6 | 6 matched constructed expectations |
| Owned XML through Mustang 2.26.0 | 11 checks | 7 equal, 4 not checkable |
| Owned XML through Mustang 2.24.0 | 11 checks | 7 equal, 4 not checkable |
| Private ConnectingEurope CII through 2.26.0 | 17 checks | 13 equal, 4 not checkable |
| Same CII through 2.24.0 | 17 checks | 12 equal, 1 missing, 4 not checkable |
| Authored semantic pairs | 4 | Rules abstained on 4; lexical baseline matched 1 label; live Jev matched 4 labels |

The live run `b30e4d9895994e1489a8480d71f219ea` sent only constructed source
and destination payment text plus the fixed criterion. Expected labels, case IDs
and filenames were excluded from the provider request. The four validated fresh
responses used 1,797 input tokens and 260 output tokens, with provider times of
652–915 ms (median 702 ms). At the official input rate below, estimated input
cost was USD 0.00007547; the conservative cumulative reservation was USD
0.00023381, within the USD 1 cap. The four-class constructed macro-F1 was 1.0,
with one example per class. Provider confidence was recorded, not treated as
calibrated correctness. There were no failed or unknown-delivery live attempts.
Raw responses and request hashes remain in ignored runtime storage. The key was
read into a temporary process through a masked prompt and was not saved to disk.
A replay of the first pair returned `cached`, preserved its original 450/63 token
usage for provenance, recorded 0 ms model time and made no new provider request.
The native server was restarted with `serve --key-stdin`, returned HTTP 200, and
Chrome completed the semantic preview and cached-send UI path with zero JavaScript
errors. The key remains process-scoped; restarting the server requires entering it
again or supplying the authorized environment variable.

The private CII independently declares `ContractReferencedDocument/IssuerAssignedID`
as `SUBSCR571`. The 2.26.0 bridge returned `contract_reference: SUBSCR571`; the
2.24.0 bridge returned null. This is an observed missing value under the selected
bridge field contract. Mustang's [2.26.0 release notes](https://github.com/ZUGFeRD/mustangproject/releases/tag/core-2.26.0)
also list import support for that reference. The sample's original XML and both
actual Java outputs are retained only in local runtime storage. The owned XML has
no contract reference, so this field is not checkable there. Declared totals in
both XMLs remain unobserved through the bridge; a missing bridge field is not
reported as an importer loss.

One real OCR pass on an owned 1,200×760 PNG returned four visible lines, including
`INVOICE SC-OWNED-001` and `BUYER ORDER PO-OWNED-9`, using the pinned Latin ONNX
models. A generated native-text PDF with embedded owned XML produced seven native
text lines and a separately hashed embedded XML representation. These are
functional examples, not an OCR accuracy estimate. Malformed XML/entity input is
rejected; conflicts between manually reviewed page facts and XML remain source
conflicts rather than destination losses.

## Browser and persistence verification

The browser check used installed Chrome via Playwright against the live local
server. It created an owned case, ran both real Mustang versions, selected source
and destination evidence, recorded a review, saved a reference, uploaded JSON with
unknown and then complete coverage, previewed and saved a profile revision,
inspected the rerun comparability warning, downloaded and independently verified a
ZIP, exercised a failed JSON run and retry, navigated both pages of a hybrid PDF,
selected an OCR image region, used zoom and fit, and deleted its test cases. There
were zero page JavaScript errors.

At 100% zoom, layout widths 360, 768, 1280 and 1920 px all had document scroll
width equal to viewport width and no clipped input/button controls. Chromium device
metric emulation at 1.25× (1024 CSS px) and 2× (640 CSS px) also passed those checks.
Actual browser-toolbar zoom in a physical desktop window was **not** verified;
the device-metric checks are labeled emulated. An earlier mobile overflow caused by
the long export hash and a hidden-field display issue were found and fixed.

After stopping and restarting the local server, run
`bff6cd9cc62c4d2182758bb114b3f219` remained complete with 11 findings, its
completed job and one `assistant_reviewed` decision. Automated tests additionally
verified interrupted jobs become visible failed runs requiring explicit retry;
reruns have no inherited current review. A report snapshot
`0698196aa6af4790a3e8dec44ae804ac` verified with SHA-256
`8b637d41f01b03cdf54de75bfd77ddd0548d7551fc84b54144378eab70050816`.
Tampering with one CSV member failed the verifier. These checks prove persistence
and integrity behavior in the local implementation, not invoice truth.

## Acquisition and storage

The two Mustang JARs total 117,918,830 downloaded bytes. The private 10,178-byte
CII file was fetched twice during development; the app keeps one ignored copy.
The OCR weights were first reused by verified hash, then freshly downloaded to a
separate ignored directory with 12,876,261 transfer bytes and matching hashes.
No full public corpus, KoSIT binary, Odoo image, RVL-CDIP, ARIES or SROIE was
downloaded for this run. The `.venv` logical file sum was 335,465,278 bytes;
active JARs 117,918,830; active OCR directory 12,880,238; active SQLite database
438,272 bytes at inspection time. These are logical file sums, not allocated disk
or an end-to-end fresh-install total.

The container image built successfully and had an uncompressed logical image size
of 468,654,986 bytes. An isolated Linux/Java 21 container prepared both pinned
JARs and OCR models in its named volume, verified their hashes with `doctor`, and
completed the owned offline demo through both real Mustang versions (runs
`bdfcc7c48aea4d298c92179e7f773f0f` and
`40002d752c8c49188c7b4b0d049e`). Its volume inspection reported
117,918,830 tool bytes, 12,882,212 model bytes, 10,178 dataset bytes and a
90,112-byte database at that point. These are logical sizes; Docker/WSL layers
and transfer overhead are additional. The container models command was repeated
after the first fetch and reported zero new transfer bytes from verified cache.
`docker compose up -d` served the app on loopback port 8770 and returned HTTP 200.

A new clone at `sourcecheck-fresh-e9186d2` under the Windows temporary directory
installed 47 locked packages into Python 3.12.13 without sibling repositories.
Its dry runs planned 117,929,008 tool/dataset bytes and 12,876,261 OCR download
bytes; fresh acquisition transferred those amounts and verified the pinned hashes.
`doctor` passed, the owned offline demo completed Mustang runs
`f3732171ebbe40de9feafdf063c083d2` and
`8ec78ae6966d46f8b760e15818506b56`, and all seven tests passed. A fresh
report snapshot `8482653fc48241e79065814cc8476696` verified offline with ZIP
SHA-256 `b515873ba5fedc3b753b649f8b6f69cfc8886c702839d2a035159fd961f46904`.
The first exploratory `uv sync` in that clone selected Python 3.13; the environment
was explicitly recreated with `uv venv --python 3.12 .venv --clear` and the frozen
install and checks were repeated on 3.12. Container and clean-clone tests prove
installation independence; they are not native Linux/macOS desktop tests.

The TypeSafe [model page](https://docs.typesafe.ai/models) listed `jev-1.13.0`
at USD 0.042 per million input tokens on 2026-09-24; output tokens were listed
as free. This is the estimate source for the USD 1.00 reservation cap and the
observed usage estimate above. The failure test also simulates unknown delivery
and leaves a conservative reservation, without a repeat network call.

## Reproduction commands

```powershell
uv venv --python 3.12 .venv
uv sync --frozen --extra test
.\.venv\Scripts\python.exe -m sourcecheck doctor
.\.venv\Scripts\python.exe -m sourcecheck datasets prepare --dry-run
.\.venv\Scripts\python.exe -m sourcecheck datasets prepare
.\.venv\Scripts\python.exe -m sourcecheck models prepare --dry-run
.\.venv\Scripts\python.exe -m sourcecheck models prepare
.\.venv\Scripts\python.exe -m sourcecheck demo prepare --mode offline
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m sourcecheck evaluate --config configs/evaluation.json
.\.venv\Scripts\python.exe -m sourcecheck evaluate --config configs/evaluation.json --live-jev --key-stdin
.\.venv\Scripts\python.exe -m sourcecheck report --run bff6cd9cc62c4d2182758bb114b3f219
.\.venv\Scripts\python.exe -m sourcecheck verify-export .runtime/exports/0698196aa6af4790a3e8dec44ae804ac.zip
.\.venv\Scripts\python.exe -m sourcecheck serve --host 127.0.0.1 --port 8770 --key-stdin
python tests/browser_check.py
```

The `browser_check.py` command used an existing Python 3.14 Playwright installation
and system Chrome, separate from the locked app environment. It requires the server
already running and creates/deletes owned runtime test cases. The current eight Python tests
passed; only a third-party Starlette/AnyIO deprecation warning remained.

## Remaining gates

- Live Jev evaluation on independently reviewed, observable real pairs with
  a fair same-input rules/lexical comparison and held-out metrics.
- More independently sourced and reviewed invoice families, a genuinely frozen
  validation/test split and human error analysis.
- Native browser-toolbar zoom and physical-window checks; native Linux/macOS
  installation checks.
- Odoo persisted-data snapshots and representative integrator pilots.
