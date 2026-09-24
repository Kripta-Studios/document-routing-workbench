# Deployment and command contract

Status: planned, 2026-09-24. There is no runnable SourceCheck package, server,
Dockerfile or downloader in this repository yet. Commands marked proposed below
are implementation targets and must not be presented as tested setup instructions.

## Available today

The public repository can be cloned over HTTPS without authentication:

```powershell
git clone https://github.com/Kripta-Studios/sourcecheck.git
cd sourcecheck
git status
```

The same Git commands work in a POSIX shell. Use an already configured SSH remote
if preferred; do not copy the original workstation's SSH alias onto another machine.

## Proposed runtime

- Python 3.12 with pinned dependencies and a rebuildable virtual environment.
- Java 21 for the selected Mustang bridge/tools, subject to actual compatibility checks.
- Browser UI served by the local application.
- SQLite and local private storage.
- Loopback address 127.0.0.1, port 8770.
- No GPU required for the planned local OCR/structured comparison path.
- Live Jev requires authorized outbound API access and TYPESAFE_API_KEY.
- Odoo/PostgreSQL need Docker only at the optional ERP milestone.

An implementation must choose a dependency lock strategy and exercise it. Avoid
installing all trace-it backend services merely to call its OCR reader.

## Proposed setup commands — not implemented

The implementation should support equivalent PowerShell commands:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m sourcecheck doctor
.\.venv\Scripts\python.exe -m sourcecheck datasets prepare --manifest configs/sources.json --dry-run
.\.venv\Scripts\python.exe -m sourcecheck datasets prepare --manifest configs/sources.json
.\.venv\Scripts\python.exe -m sourcecheck serve --host 127.0.0.1 --port 8770
```

POSIX equivalents:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m sourcecheck doctor
.venv/bin/python -m sourcecheck datasets prepare --manifest configs/sources.json --dry-run
.venv/bin/python -m sourcecheck datasets prepare --manifest configs/sources.json
.venv/bin/python -m sourcecheck serve --host 127.0.0.1 --port 8770
```

The package, manifest and commands above do not exist yet. Replace editable-install
examples with tested locked installation instructions when dependency files exist.
The serve command should supervise the worker so another user can launch the complete
app in one step. Doctor should report Java, model hashes, writable storage, tool
versions and live-provider configuration presence without revealing secrets.

## Proposed operational commands — not implemented

```text
python -m sourcecheck demo prepare --mode offline
python -m sourcecheck evaluate --config configs/evaluation.json --dry-run
python -m sourcecheck evaluate --config configs/evaluation.json
python -m sourcecheck report --run <run-id>
python -m sourcecheck verify-export <report.zip>
python -m sourcecheck storage inspect
```

Offline demonstration must work without credentials. Label authored targets and
recorded provider responses. A live demonstration executes actual OCR/importer/Jev
calls and identifies fresh versus cached outputs.

Report regeneration should need no provider calls. Evaluation must respect frozen
manifests and cumulative budgets. Storage inspection separates datasets, models,
database, caches and exports. Deletion commands must preview concrete targets.

## Configuration contract

Document the implemented names and defaults for:

- Runtime storage root and database path.
- OCR model directory and expected hashes.
- Java executable, tool paths and pinned artifacts.
- Input/page/pixel/text limits and worker concurrency.
- Dataset/bootstrap byte caps and live API estimate budget.
- Provider endpoint, fixed model ID, timeout and cache behavior.
- Selected profile, destination adapter and live-transmission mode.

Read TYPESAFE_API_KEY on the server. Never put a real key in examples, screenshots,
browser storage, query strings or commits. Supply an .env.example with placeholders
only when implementation adds configuration loading.

A configured key alone should not make every upload transmit content. The user
selects live semantic comparison; show what representation is sent. Protect local
mutation endpoints against unintended cross-site requests.

## Containers

The future application Docker setup must include a documented persistent volume,
model/tool bootstrap, read-only code and bounded worker execution. Do not assume
the app container also includes a full ERP.

For the optional Odoo milestone, use a separate Compose profile with Odoo 19 and
PostgreSQL 16, pinned compatible images, isolated test database and no production
credentials. Capture actual stored-data snapshots and declare queried field coverage.
Architecture-specific digests and measured layer sizes are in DATASETS.md.

Docker/WSL installation storage is additional to the documented image totals.
Public/shared deployment requires a later authentication and access-control design;
binding the local app to all interfaces is not a production deployment guide.

## Fresh-machine acceptance

Before claiming deployability:

1. Install from a clean checkout with no sibling paths or old caches.
2. Bootstrap tools/models under the documented budgets.
3. Run the offline demonstration and a real Mustang case.
4. Restart web/worker and confirm persistent progress/review.
5. Generate and independently verify a report.
6. Run genuine OCR and live Jev when credentials are available.
7. Record OS, architecture, dependency lock, actual commands, download bytes and disk use.

Verify PowerShell and Linux/macOS instructions where environments are available.
State clearly which OS was actually exercised and which commands remain unverified.
A Linux container run does not verify native macOS setup.
