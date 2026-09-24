"""Loopback browser API. All mutations require a same-origin custom header."""
import json
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .config import ROOT
from .service import add_profile, create_case, delete_case, get_case, get_run, list_cases, review, retry_run, save_reference, start_run
from .export import create_export
from .jev import preview as jev_preview, suggest as jev_suggest
from .store import db, row

@asynccontextmanager
async def lifespan(app):
    with db() as con:
        con.execute("UPDATE runs SET status='failed',error='Server stopped during this run; retry explicitly' WHERE status IN ('queued','running')")
        con.execute("UPDATE jobs SET status='failed',error='Server stopped during this run; retry explicitly' WHERE status IN ('queued','running')")
    yield

app = FastAPI(title="SourceCheck", docs_url=None, redoc_url=None, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=Path(__file__).with_name("static")), name="static")

@app.middleware("http")
async def local_guard(request: Request, call_next):
    host = request.headers.get("host", "").split(":")[0].lower()
    if host not in {"127.0.0.1","localhost","testserver"}:
        return JSONResponse({"detail":"Loopback host required"},status_code=403)
    if request.method in {"POST","PUT","PATCH","DELETE"}:
        origin = request.headers.get("origin")
        if request.headers.get("x-sourcecheck") != "1" or (origin and origin.rstrip("/") != f"{request.url.scheme}://{request.headers.get('host')}"):
            return JSONResponse({"detail":"Same-origin mutation header required"},status_code=403)
    return await call_next(request)

def bad(exc):
    raise HTTPException(400,str(exc)) from exc

@app.get("/",response_class=HTMLResponse)
def index():
    return Path(__file__).with_name("static").joinpath("index.html").read_text(encoding="utf-8")

@app.get("/api/cases")
def cases():
    return list_cases()

@app.post("/api/cases")
async def new_case(source: UploadFile=File(...), title: str=Form(""), use_ocr: bool=Form(True)):
    try:
        content = await source.read(25*1024*1024+1)
        return {"id":create_case(title or source.filename or "Invoice",source.filename or "invoice",content,use_ocr)}
    except (ValueError,RuntimeError) as exc:
        bad(exc)

@app.get("/api/cases/{case_id}")
def case_detail(case_id: str):
    case = get_case(case_id)
    if not case:
        raise HTTPException(404,"Case not found")
    case.pop("source_path",None)
    return case

@app.get("/api/cases/{case_id}/source")
def source_file(case_id: str):
    with db() as con:
        case = row(con,"SELECT source_path,source_name,source_kind FROM cases WHERE id=? AND deleted=0",(case_id,))
    if not case:
        raise HTTPException(404,"Case not found")
    media = {"pdf":"application/pdf","png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg","xml":"application/xml"}[case["source_kind"]]
    return FileResponse(case["source_path"],media_type=media,headers={"Content-Security-Policy":"sandbox", "X-Content-Type-Options":"nosniff"})

@app.post("/api/cases/{case_id}/profiles")
async def profile(case_id: str, request: Request):
    try:
        return add_profile(case_id,await request.json())
    except ValueError as exc:
        bad(exc)

@app.post("/api/cases/{case_id}/runs")
async def run(case_id: str, mode: str=Form(...), version: str=Form("2.26.0"), destination: UploadFile|None=File(None), csv_contract: str=Form(""), coverage_contract: str=Form(""), profile_id: str=Form(""), previous_id: str=Form(""), manual: str=Form("")):
    try:
        content = await destination.read(25*1024*1024+1) if destination else None
        contract = json.loads(csv_contract) if csv_contract else None
        coverage = json.loads(coverage_contract) if coverage_contract else None
        manual_facts = json.loads(manual) if manual else None
        return {"id":start_run(case_id,mode,version,content,destination.filename if destination else None,contract,profile_id or None,previous_id or None,manual_facts,coverage)}
    except (ValueError,RuntimeError,json.JSONDecodeError) as exc:
        bad(exc)

@app.get("/api/runs/{run_id}")
def run_detail(run_id: str):
    run = get_run(run_id)
    if not run:
        raise HTTPException(404,"Run not found")
    run.pop("destination_path",None)
    return run

@app.post("/api/runs/{run_id}/retry")
def retry(run_id: str):
    try:
        return {"id":retry_run(run_id)}
    except ValueError as exc:
        bad(exc)

@app.post("/api/runs/{run_id}/review")
async def new_review(run_id: str, request: Request):
    body = await request.json()
    try:
        return {"id":review(run_id,body.get("finding_id",""),body.get("reviewer",""),body.get("disposition",""),body.get("reason",""))}
    except ValueError as exc:
        bad(exc)

@app.get("/api/runs/{run_id}/semantic/{finding_id}/preview")
def semantic_preview(run_id: str, finding_id: str):
    try:
        return jev_preview(run_id,finding_id)
    except ValueError as exc:
        bad(exc)

@app.post("/api/runs/{run_id}/semantic/{finding_id}")
def semantic_suggest(run_id: str, finding_id: str):
    try:
        return jev_suggest(run_id,finding_id)
    except ValueError as exc:
        bad(exc)

@app.post("/api/cases/{case_id}/references")
async def reference(case_id: str, request: Request):
    body = await request.json()
    try:
        return {"id":save_reference(case_id,body.get("run_id",""),body.get("reviewer",""))}
    except ValueError as exc:
        bad(exc)

@app.post("/api/runs/{run_id}/exports")
def export(run_id: str):
    try:
        result = create_export(run_id)
        return {"id":result["id"],"sha256":result["sha256"],"url":f"/api/exports/{result['id']}"}
    except ValueError as exc:
        bad(exc)

@app.get("/api/exports/{export_id}")
def download(export_id: str):
    with db() as con:
        record = row(con,"SELECT path FROM exports WHERE id=?",(export_id,))
    if not record:
        raise HTTPException(404,"Export not found")
    return FileResponse(record["path"],media_type="application/zip",filename=f"sourcecheck-{export_id}.zip")

@app.get("/api/cases/{case_id}/delete-preview")
def delete_preview(case_id: str):
    with db() as con:
        case = row(con,"SELECT id FROM cases WHERE id=? AND deleted=0",(case_id,))
        if not case:
            raise HTTPException(404,"Case not found")
        runs = con.execute("SELECT COUNT(*) FROM runs WHERE case_id=?",(case_id,)).fetchone()[0]
        exports = con.execute("SELECT COUNT(*) FROM exports WHERE run_id IN (SELECT id FROM runs WHERE case_id=?)",(case_id,)).fetchone()[0]
        return {"case_id":case_id,"runs":runs,"exports":exports,"effect":"Deletes server originals, derived outputs, reviews, references and exports. Previously downloaded ZIPs remain outside server control."}

@app.delete("/api/cases/{case_id}")
def remove_case(case_id: str):
    try:
        return {"deleted_files":delete_case(case_id)}
    except ValueError as exc:
        bad(exc)
