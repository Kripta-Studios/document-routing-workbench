"""Case lifecycle and immutable comparison runs."""
import csv
import hashlib
import io
import json
import threading
import time
from pathlib import Path
from .config import MAX_FILE, ROOT
from .compare import compare, diff
from .mustang import import_xml
from .source import embedded_xml, read_source, sha
from .store import db, decode, encode, now, row, rows, save_bytes, uid

RUN_SLOTS = threading.BoundedSemaphore(2)

def profile_hash(profile):
    return sha(encode(profile).encode())

def validate_profile(profile):
    if not isinstance(profile, dict) or not isinstance(profile.get("checks"), list) or len(profile["checks"]) > 100:
        raise ValueError("Profile needs at most 100 checks")
    ids = set()
    for check in profile["checks"]:
        if not isinstance(check, dict) or any(not isinstance(check.get(key), str) or not check[key] for key in ("id", "source", "destination", "kind")):
            raise ValueError("Each check needs id, source, destination and kind")
        if check["id"] in ids or check["kind"] not in {"identifier", "date", "decimal", "text"} or check.get("coverage", "unknown") not in {"complete", "partial", "unknown"}:
            raise ValueError("Invalid or duplicate check")
        ids.add(check["id"])
    return profile

def default_profile():
    return json.loads((ROOT / "configs/default-profile.json").read_text(encoding="utf-8"))

def create_case(title, filename, content, use_ocr=True):
    if len(content) > MAX_FILE:
        raise ValueError("Source exceeds 25 MiB")
    source_data = read_source(content, filename, use_ocr)
    case_id = uid()
    path = save_bytes("originals", content)
    profile = default_profile()
    with db() as con:
        con.execute("INSERT INTO cases VALUES(?,?,?,?,?,?,?,?,0)", (case_id, title[:200] or filename[:200], now(), Path(filename).name[:200], sha(content), source_data["kind"], path, encode(source_data)))
        con.execute("INSERT INTO profiles VALUES(?,?,?,?,?,?)", (uid(), case_id, 1, profile_hash(profile), encode(profile), now()))
    return case_id

def get_case(case_id):
    with db() as con:
        case = row(con, "SELECT * FROM cases WHERE id=? AND deleted=0", (case_id,))
        if not case:
            return None
        case["source_data"] = decode(case["source_data"])
        case["profiles"] = rows(con, "SELECT id,version,sha,created,document FROM profiles WHERE case_id=? ORDER BY version", (case_id,))
        for profile in case["profiles"]:
            profile["document"] = decode(profile["document"])
        case["runs"] = rows(con, "SELECT id,profile_id,previous_id,created,mode,adapter_version,status,error,elapsed_ms FROM runs WHERE case_id=? ORDER BY created DESC", (case_id,))
        case["references"] = rows(con, "SELECT id,run_id,reviewer,origin,created FROM reference_cases WHERE case_id=? ORDER BY created DESC", (case_id,))
        return case

def list_cases():
    with db() as con:
        return rows(con, "SELECT id,title,created,source_name,source_kind FROM cases WHERE deleted=0 ORDER BY created DESC")

def add_profile(case_id, profile):
    validate_profile(profile)
    with db() as con:
        case = row(con, "SELECT id FROM cases WHERE id=? AND deleted=0", (case_id,))
        if not case:
            raise ValueError("Case not found")
        version = con.execute("SELECT COALESCE(MAX(version),0)+1 FROM profiles WHERE case_id=?", (case_id,)).fetchone()[0]
        profile_id = uid()
        con.execute("INSERT INTO profiles VALUES(?,?,?,?,?,?)", (profile_id, case_id, version, profile_hash(profile), encode(profile), now()))
        return {"id": profile_id, "version": version, "sha": profile_hash(profile)}

def _csv_target(content, contract):
    if not isinstance(contract, dict) or not contract.get("columns") or not contract.get("entity_column") or not contract.get("reviewed") or not isinstance(contract.get("field_coverage"),dict) or contract.get("decimal_separator") not in {".",","}:
        raise ValueError("CSV requires reviewed columns, entity_column, decimal separator and per-field coverage")
    text = content.decode("utf-8-sig")
    records = list(csv.DictReader(io.StringIO(text)))
    if len(records) != 1 or contract["entity_column"] not in records[0] or not records[0][contract["entity_column"]]:
        raise ValueError("CSV MVP requires one row with an explicit entity ID")
    result = {}
    for column, destination in contract["columns"].items():
        if column not in records[0] or not isinstance(destination, str) or not destination.isidentifier():
            raise ValueError("Invalid CSV column mapping")
        value = records[0][column]
        if contract.get("decimal_separator") == "," and column in contract.get("decimal_columns", []):
            value = value.replace(".", "").replace(",", ".")
        result[destination] = value
    return result

def start_run(case_id, mode, version=None, destination_content=None, destination_name=None, csv_contract=None, profile_id=None, previous_id=None, manual=None, coverage_contract=None):
    retained_input = None
    with db() as con:
        case = row(con, "SELECT * FROM cases WHERE id=? AND deleted=0", (case_id,))
        if not case:
            raise ValueError("Case not found")
        profile_row = row(con, "SELECT * FROM profiles WHERE id=? AND case_id=?", (profile_id, case_id)) if profile_id else row(con, "SELECT * FROM profiles WHERE case_id=? ORDER BY version DESC LIMIT 1", (case_id,))
        if not profile_row:
            raise ValueError("Profile not found")
        if previous_id and not row(con, "SELECT id FROM runs WHERE id=? AND case_id=?", (previous_id, case_id)):
            raise ValueError("Previous run not found")
        if destination_content is not None:
            if len(destination_content) > MAX_FILE:
                raise ValueError("Destination exceeds 25 MiB")
            retained_input = save_bytes("destinations", destination_content)
        run_id = uid()
        job_id = uid()
        con.execute("INSERT INTO runs(id,case_id,profile_id,previous_id,created,mode,adapter_version,status,destination_name,destination_path,destination_data) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (run_id,case_id,profile_row["id"],previous_id,now(),mode,version,"queued",destination_name,retained_input,encode({"csv_contract":csv_contract,"manual":manual,"coverage_contract":coverage_contract})))
        con.execute("INSERT INTO jobs(id,run_id,status) VALUES(?,?,?)", (job_id,run_id,"queued"))
    # One local worker per request. The queued record survives process loss and is retryable.
    RUN_SLOTS.acquire()
    try:
        with db() as con:
            con.execute("UPDATE jobs SET status='running',attempts=attempts+1,started=? WHERE id=?", (now(),job_id))
            con.execute("UPDATE runs SET status='running' WHERE id=?", (run_id,))
        started = time.perf_counter()
        raw = Path(case["source_path"]).read_bytes()
        source_data = decode(case["source_data"])
        if mode == "mustang":
            if source_data["kind"] not in {"xml", "pdf"}:
                raise ValueError("Mustang requires XML or a PDF with embedded XML")
            xml = raw if source_data["kind"] == "xml" else embedded_xml(raw)
            capture = import_xml(xml, version or "2.26.0")
            target = capture["data"]
            dest_bytes = encode(target).encode()
            destination_name = f"mustang-{version or '2.26.0'}.json"
            recorded_mode = "actual_importer_execution"
        elif mode in {"uploaded_json", "uploaded_csv", "authored_simulation"}:
            if not destination_content or len(destination_content) > MAX_FILE:
                raise ValueError("Destination must be 1 byte to 25 MiB")
            if mode == "uploaded_csv":
                target = _csv_target(destination_content, csv_contract)
            else:
                target = json.loads(destination_content)
            if not isinstance(target, dict):
                raise ValueError("Destination must be a JSON object")
            dest_bytes = destination_content
            recorded_mode = "user_uploaded_unverified" if mode != "authored_simulation" else "authored_simulation"
            capture = {"data": target, "mode": recorded_mode, "csv_contract": csv_contract}
        else:
            raise ValueError("Unsupported destination mode")
        profile = decode(profile_row["document"])
        effective_profile = json.loads(json.dumps(profile))
        if mode != "mustang":
            contract = csv_contract if mode == "uploaded_csv" else coverage_contract
            fields = contract.get("field_coverage",{}) if isinstance(contract,dict) and contract.get("reviewed") is True else {}
            for check in effective_profile["checks"]:
                coverage = fields.get(check["destination"],"unknown")
                if coverage not in {"complete","partial","unknown"}:
                    raise ValueError("Invalid destination field coverage")
                check["coverage"] = coverage
            effective_profile["lines_coverage"] = fields.get("lines","unknown")
            capture["coverage_contract"] = contract
        findings = compare(raw, source_data, target, effective_profile, manual)
        with db() as con:
            prior = row(con, "SELECT findings,profile_id FROM runs WHERE id=?", (previous_id,)) if previous_id else None
            prior_profile = row(con, "SELECT sha FROM profiles WHERE id=?", (prior["profile_id"],))["sha"] if prior else None
        changes = diff(decode(prior["findings"]) if prior else [], findings, prior_profile, profile_row["sha"]) if prior else []
        dest_path = retained_input or save_bytes("destinations", dest_bytes)
        elapsed = round((time.perf_counter()-started)*1000,2)
        with db() as con:
            con.execute("UPDATE runs SET status='complete', mode=?, destination_sha=?,destination_name=?,destination_path=?,destination_data=?,findings=?,diff=?,elapsed_ms=? WHERE id=?", (recorded_mode,sha(dest_bytes),Path(destination_name or 'destination').name[:200],dest_path,encode({"capture":capture,"data":target,"manual":manual}),encode(findings),encode(changes),elapsed,run_id))
            con.execute("UPDATE jobs SET status='complete',finished=? WHERE id=?", (now(),job_id))
    except Exception as exc:
        with db() as con:
            con.execute("UPDATE runs SET status='failed',error=? WHERE id=?", (str(exc)[:2000],run_id))
            con.execute("UPDATE jobs SET status='failed',error=?,finished=? WHERE id=?", (str(exc)[:2000],now(),job_id))
    finally:
        RUN_SLOTS.release()
    return run_id

def retry_run(run_id):
    with db() as con:
        old = row(con,"SELECT * FROM runs WHERE id=?",(run_id,))
    if not old or old["status"] not in {"failed","delivery_unknown"}:
        raise ValueError("Only failed runs can be retried")
    saved = decode(old["destination_data"]) or {}
    content = Path(old["destination_path"]).read_bytes() if old["destination_path"] and old["mode"] in {"uploaded_json","uploaded_csv","authored_simulation"} else None
    return start_run(old["case_id"],old["mode"],old["adapter_version"],content,old["destination_name"],saved.get("csv_contract"),old["profile_id"],old["previous_id"],saved.get("manual"),saved.get("coverage_contract"))

def get_run(run_id):
    with db() as con:
        run = row(con, "SELECT * FROM runs WHERE id=?", (run_id,))
        if not run:
            return None
        for key in ("destination_data","findings","diff"):
            run[key] = decode(run[key])
        run["reviews"] = rows(con, "SELECT * FROM review_events WHERE run_id=? ORDER BY created,id", (run_id,))
        run["job"] = row(con, "SELECT * FROM jobs WHERE run_id=?", (run_id,))
        run["profile"] = decode(row(con, "SELECT document FROM profiles WHERE id=?", (run["profile_id"],))["document"])
        run["semantic_runs"] = rows(con, "SELECT id,finding_id,status,request_sha,response,usage,elapsed_ms,created FROM semantic_runs WHERE run_id=? ORDER BY created", (run_id,))
        return run

def review(run_id, finding_id, reviewer, disposition, reason, origin="human_reviewed"):
    if disposition not in {"confirmed_issue","accepted_transformation","dismissed","unresolved"} or not reviewer.strip() or not reason.strip():
        raise ValueError("Reviewer, disposition and reason are required")
    if origin not in {"human_reviewed","assistant_reviewed","deterministic_constructed"}:
        raise ValueError("Invalid review origin")
    with db() as con:
        run = row(con, "SELECT findings,status FROM runs WHERE id=?", (run_id,))
        if not run or run["status"] != "complete" or finding_id not in {f["id"] for f in decode(run["findings"])}:
            raise ValueError("Finding not found in a complete run")
        event = uid()
        con.execute("INSERT INTO review_events(id,run_id,finding_id,reviewer,disposition,reason,created,origin) VALUES(?,?,?,?,?,?,?,?)", (event,run_id,finding_id,reviewer.strip()[:100],disposition,reason.strip()[:1000],now(),origin))
        return event

def save_reference(case_id, run_id, reviewer):
    with db() as con:
        run = row(con, "SELECT findings,status FROM runs WHERE id=? AND case_id=?", (run_id,case_id))
        if not run or run["status"] != "complete" or not reviewer.strip():
            raise ValueError("Complete run and reviewer required")
        reviews = rows(con, "SELECT * FROM review_events WHERE run_id=? ORDER BY created,id", (run_id,))
        latest = {review["finding_id"]: review for review in reviews}
        reference = {f["id"]: {"expected_result": f["result"], "disposition": latest.get(f["id"],{}).get("disposition", "pending"), "annotation_origin": latest[f["id"]]["origin"] if f["id"] in latest else "deterministic_constructed"} for f in decode(run["findings"])}
        ref_id = uid()
        con.execute("INSERT INTO reference_cases VALUES(?,?,?,?,?,?,?)", (ref_id,case_id,run_id,reviewer.strip()[:100],"mixed_reviewed_and_constructed",now(),encode(reference)))
        return ref_id

def delete_case(case_id):
    with db() as con:
        case = row(con, "SELECT * FROM cases WHERE id=? AND deleted=0", (case_id,))
        if not case:
            raise ValueError("Case not found")
        paths = [case["source_path"]] + [run["destination_path"] for run in rows(con, "SELECT destination_path FROM runs WHERE case_id=?", (case_id,)) if run["destination_path"]]
        for export in rows(con, "SELECT path FROM exports WHERE run_id IN (SELECT id FROM runs WHERE case_id=?)", (case_id,)):
            paths.append(export["path"])
        semantic_hashes = [item["request_sha"] for item in rows(con, "SELECT DISTINCT request_sha FROM semantic_runs WHERE run_id IN (SELECT id FROM runs WHERE case_id=?)", (case_id,))]
        con.execute("DELETE FROM semantic_runs WHERE run_id IN (SELECT id FROM runs WHERE case_id=?)", (case_id,))
        con.execute("DELETE FROM exports WHERE run_id IN (SELECT id FROM runs WHERE case_id=?)", (case_id,))
        con.execute("DELETE FROM reference_cases WHERE case_id=?", (case_id,))
        con.execute("DELETE FROM review_events WHERE run_id IN (SELECT id FROM runs WHERE case_id=?)", (case_id,))
        con.execute("DELETE FROM jobs WHERE run_id IN (SELECT id FROM runs WHERE case_id=?)", (case_id,))
        con.execute("DELETE FROM runs WHERE case_id=?", (case_id,))
        con.execute("DELETE FROM profiles WHERE case_id=?", (case_id,))
        con.execute("DELETE FROM cases WHERE id=?", (case_id,))
    for path in paths:
        Path(path).unlink(missing_ok=True)
    from .config import DATA
    for identity in semantic_hashes:
        (DATA / "jev-cache" / f"{identity}.json").unlink(missing_ok=True)
    return len(paths)
