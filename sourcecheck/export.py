"""Self-contained snapshot export with a reproducible SHA-256 manifest."""
import csv
import hashlib
import html
import io
import json
import zipfile
from pathlib import Path
from .store import DATA, db, decode, encode, now, row, rows, uid

def digest(data):
    return hashlib.sha256(data).hexdigest()

def _csv_safe(value):
    text = "" if value is None else str(value)
    return "'" + text if text.lstrip().startswith(("=","+","-","@")) else text

def create_export(run_id):
    with db() as con:
        run = row(con, "SELECT * FROM runs WHERE id=? AND status='complete'", (run_id,))
        if not run:
            raise ValueError("Complete run required")
        case = row(con, "SELECT title,source_name,source_sha FROM cases WHERE id=?", (run["case_id"],))
        profile = row(con, "SELECT sha,document FROM profiles WHERE id=?", (run["profile_id"],))
        cutoff = now()
        reviews = rows(con, "SELECT * FROM review_events WHERE run_id=? AND created<=? ORDER BY created,id", (run_id,cutoff))
        semantic = rows(con, "SELECT finding_id,status,request_sha,response,usage,elapsed_ms,created FROM semantic_runs WHERE run_id=? AND created<=?", (run_id,cutoff))
        semantic_summary=[]
        for item in semantic:
            response=decode(item["response"])
            answer=response.get("answers",{}).get("relation",{}) if response else {}
            semantic_summary.append({"finding_id":item["finding_id"],"status":item["status"],"request_sha256":item["request_sha"],"suggestion":answer.get("choice"),"confidence":answer.get("confidence"),"usage":decode(item["usage"]),"elapsed_ms":item["elapsed_ms"],"created":item["created"]})
        capture=(decode(run["destination_data"]) or {}).get("capture",{})
        capture_metadata={key:value for key,value in capture.items() if key not in {"data","response"}}
        summary = {"schema":"sourcecheck-export-1","snapshot_id":uid(),"created":cutoff,"case_id":run["case_id"],"run_id":run_id,"case_title":case["title"],"source_name":case["source_name"],"source_sha256":case["source_sha"],"destination_sha256":run["destination_sha"],"mode":run["mode"],"adapter_version":run["adapter_version"],"capture":capture_metadata,"profile_sha256":profile["sha"],"profile":decode(profile["document"]),"findings":decode(run["findings"]),"diff":decode(run["diff"]),"review_events":reviews,"semantic_runs":semantic_summary,"review_cutoff":cutoff,"limits":"Integrity proves file consistency, not correctness of business facts."}
    findings = summary["findings"]
    counts = {name:sum(1 for finding in findings if finding["result"]==name) for name in ("equal","different","missing","semantic_review","not_checkable")}
    counts["unobserved"] = sum(1 for finding in findings if finding["coverage"]=="unobserved")
    counts["source_uncertain"] = sum(1 for finding in findings if finding["source_state"]=="uncertain")
    summary["counts"] = counts
    csv_out = io.StringIO()
    writer = csv.writer(csv_out)
    writer.writerow(["id","label","requirement","source_state","coverage","result","source_raw","source_path","destination_path","destination_raw"])
    for finding in findings:
        source = finding.get("source") or {}
        writer.writerow([_csv_safe(value) for value in (finding["id"],finding["label"],finding["requirement"],finding["source_state"],finding["coverage"],finding["result"],source.get("raw"),source.get("path"),finding.get("destination_path"),finding.get("destination_raw"))])
    table = "".join("<tr>" + "".join(f"<td>{html.escape(str(value or ''))}</td>" for value in (f["label"],f["result"],(f.get("source") or {}).get("raw"),f.get("destination_raw"),f["coverage"])) + "</tr>" for f in findings)
    page = f"<!doctype html><html lang='en'><meta charset='utf-8'><title>SourceCheck report</title><style>body{{font:16px system-ui;margin:2rem;color:#17241f}}table{{border-collapse:collapse;width:100%}}td,th{{padding:.65rem;border:1px solid #abb8b1;text-align:left;overflow-wrap:anywhere}}small{{color:#566}}</style><h1>SourceCheck report</h1><p>{html.escape(case['title'])} · Run {html.escape(run_id)}</p><p>Mode: {html.escape(run['mode'])}. Profile SHA-256: {html.escape(profile['sha'])}</p><table><thead><tr><th>Check</th><th>Result</th><th>Source</th><th>Destination</th><th>Coverage</th></tr></thead><tbody>{table}</tbody></table><p><small>Integrity proves file consistency, not correctness of business facts. Passing checks apply only to the configured scope.</small></p></html>"
    files = {"summary.json":(json.dumps(summary,ensure_ascii=False,indent=2)+"\n").encode(),"findings.csv":csv_out.getvalue().encode("utf-8-sig"),"report.html":page.encode(),"provenance.json":(json.dumps({"source_sha256":case["source_sha"],"destination_sha256":run["destination_sha"],"profile_sha256":profile["sha"],"adapter_version":run["adapter_version"],"mode":run["mode"]},indent=2)+"\n").encode()}
    manifest = {name:{"sha256":digest(data),"bytes":len(data)} for name,data in sorted(files.items())}
    files["manifest.json"] = (json.dumps({"schema":"sourcecheck-manifest-1","files":manifest},indent=2)+"\n").encode()
    directory = DATA / "exports"
    directory.mkdir(parents=True,exist_ok=True)
    path = directory / f"{summary['snapshot_id']}.zip"
    with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_DEFLATED) as archive:
        for name,data in files.items():
            archive.writestr(name,data)
    verify_export(path)
    with db() as con:
        con.execute("INSERT INTO exports VALUES(?,?,?,?,?,?)",(summary["snapshot_id"],run_id,cutoff,cutoff,digest(path.read_bytes()),str(path)))
    return {"id":summary["snapshot_id"],"path":str(path),"sha256":digest(path.read_bytes()),"snapshot_id":summary["snapshot_id"]}

def verify_export(path):
    path = Path(path)
    if path.stat().st_size > 50*1024*1024:
        raise ValueError("Export exceeds verifier size limit")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != {"manifest.json","summary.json","findings.csv","report.html","provenance.json"}:
            raise ValueError("Unexpected export members")
        manifest = json.loads(archive.read("manifest.json"))
        if set(manifest["files"]) != set(names)-{"manifest.json"}:
            raise ValueError("Manifest does not cover all files")
        for name,identity in manifest["files"].items():
            if name.startswith("/") or ".." in name:
                raise ValueError("Unsafe path")
            data = archive.read(name)
            if len(data) != identity["bytes"] or digest(data) != identity["sha256"]:
                raise ValueError(f"Integrity failure: {name}")
        summary = json.loads(archive.read("summary.json"))
        provenance = json.loads(archive.read("provenance.json"))
        for key in ("source_sha256","destination_sha256","profile_sha256","adapter_version","mode"):
            if summary[key] != provenance[key]:
                raise ValueError("Provenance mismatch")
        return {"ok":True,"snapshot_id":summary["snapshot_id"],"run_id":summary["run_id"],"files":len(names)-1,"sha256":digest(path.read_bytes())}
