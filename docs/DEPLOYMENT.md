# Local deployment and command contract

Updated 2026-09-24. Windows 11, Python 3.12.13 and Java 25 were exercised. The Java
bridge compiles for Java 21. Native Linux/macOS setup instructions below are
equivalent commands but have not been exercised. Docker verification status is in
[RESULTS.md](RESULTS.md).

## Install and bootstrap

Use a clean checkout with `uv` and JDK 21 or newer available on `PATH`. These
PowerShell commands were executed in the implementation workspace:

```powershell
uv venv --python 3.12 .venv
uv sync --frozen --extra test
.\.venv\Scripts\python.exe -m sourcecheck doctor
.\.venv\Scripts\python.exe -m sourcecheck datasets prepare --manifest configs/sources.json --dry-run
.\.venv\Scripts\python.exe -m sourcecheck datasets prepare --manifest configs/sources.json
.\.venv\Scripts\python.exe -m sourcecheck models prepare --dry-run
.\.venv\Scripts\python.exe -m sourcecheck models prepare
.\.venv\Scripts\python.exe -m sourcecheck demo prepare --mode offline
.\.venv\Scripts\python.exe -m sourcecheck serve --host 127.0.0.1 --port 8770
```

Open `http://127.0.0.1:8770/`. The first dataset command prints every planned URL,
revision, size, license note, target and cache status. The download enforces the
manifest's 1 GiB dataset and 4 GiB aggregate limits. The model command uses pinned
PaddlePaddle revisions and a 20 MiB model transfer ceiling. Existing matching
files avoid new transfers. Java compilation occurs on the first Mustang run.

POSIX commands have the same order:

```bash
uv venv --python 3.12 .venv
uv sync --frozen --extra test
.venv/bin/python -m sourcecheck doctor
.venv/bin/python -m sourcecheck datasets prepare --manifest configs/sources.json --dry-run
.venv/bin/python -m sourcecheck datasets prepare --manifest configs/sources.json
.venv/bin/python -m sourcecheck models prepare --dry-run
.venv/bin/python -m sourcecheck models prepare
.venv/bin/python -m sourcecheck demo prepare --mode offline
.venv/bin/python -m sourcecheck serve --host 127.0.0.1 --port 8770
```

These POSIX commands are provided for installation parity, not a claim of native
Linux/macOS verification. The package does not search sibling repositories.

## Operational commands

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m sourcecheck evaluate --config configs/evaluation.json --dry-run
.\.venv\Scripts\python.exe -m sourcecheck evaluate --config configs/evaluation.json
.\.venv\Scripts\python.exe -m sourcecheck report --run RUN_ID
.\.venv\Scripts\python.exe -m sourcecheck verify-export .runtime/exports/EXPORT_ID.zip
.\.venv\Scripts\python.exe -m sourcecheck storage inspect
```

The offline demo executes genuine pinned Mustang imports on the owned fixture. The
evaluation separates authored mutations from actual importer runs. Generated
aggregate JSON remains in `.runtime/evaluation/`; the sanitized family manifest is
`configs/evaluation-manifest.json`. These commands do not request Jev unless the
user explicitly selects a semantic pair in the browser.

## Settings and safety boundaries

| Setting | Default | Meaning |
|---|---|---|
| `SOURCECHECK_DATA` | `.runtime/` | SQLite, originals, captures, models, caches, exports |
| `SOURCECHECK_TOOLS` | `external/tools/` | Pinned Mustang JARs |
| `SOURCECHECK_MODELS` | `<data>/models/` | Pinned local OCR models |
| `SOURCECHECK_JAVA`, `SOURCECHECK_JAVAC` | PATH commands | Java execution/compiler |
| `TYPESAFE_API_KEY` | absent | Optional server-side Jev access |
| Jev endpoint/model | `https://api.typesafe.ai/v1/systemone`, `jev-1.13.0` | Fixed by code |
| Jev estimate budget | USD 1.00 | Conservative cumulative reservation; unknown delivery remains charged |
| Intake | 25 MiB/file, 20 PDF pages, 18 MP/image | Server-enforced bounds |
| Mustang subprocess | 45 s, 384 MiB Java heap | One local process per run; two run slots |

The server binds to loopback by default, checks the Host and requires a same-origin
mutation header. It has no authentication and is not intended for a shared/public
interface. Selected text is previewed before optional Jev transmission. The source
files and provider cache never enter static serving; case deletion removes related
server-held content. Already downloaded exports remain under the user's control.

## Container

`Dockerfile` packages Python 3.12, the locked dependencies and Java 21. Compose
publishes only loopback port 8770, stores tools/models/data in a persistent named
volume, mounts a bounded temporary directory and makes the container root filesystem
read-only. It does not include Odoo.

```bash
docker compose build
docker compose run --rm app datasets prepare --manifest configs/sources.json --dry-run
docker compose run --rm app datasets prepare --manifest configs/sources.json
docker compose run --rm app models prepare
docker compose up -d
docker compose run --rm app demo prepare --mode offline
```

The first container setup transfers its own pinned tools/models into the volume.
`docker compose down` preserves the volume; `down -v` would delete it and is not
part of routine shutdown. Container build/run results and image size are recorded
in [RESULTS.md](RESULTS.md). Docker/WSL installation storage is additional.

## Limits of this handoff

The Windows native path, clean Windows clone and isolated Linux container were
verified. Their checks are recorded in [RESULTS.md](RESULTS.md). Live Jev requires an
authorized `TYPESAFE_API_KEY`; a missing key leaves that evaluation incomplete.
Odoo and real customer diagnosis pilots are later milestones.
