"""SourceCheck command line entry point."""
import argparse
import hashlib
import json
import os
import platform
import shutil
from pathlib import Path
from .config import DATA, MODELS, ROOT, TOOLS, VERSIONS

def emit(value):
    print(json.dumps(value,indent=2,ensure_ascii=False,default=str))

def key_from_stdin():
    import sys
    from getpass import getpass
    key = getpass("Jev API key: ") if sys.stdin.isatty() else sys.stdin.readline().strip()
    if not key:
        raise ValueError("Empty Jev API key")
    os.environ["TYPESAFE_API_KEY"] = key

def doctor():
    from .mustang import jar_for
    from .acquire import checksum
    tools={}
    for name in ("java","javac"):
        tools[name]=shutil.which(os.getenv(f"SOURCECHECK_{name.upper()}",name))
    jars={}
    for version in VERSIONS:
        try:jars[version]={"path":str(jar_for(version)),"verified":True}
        except RuntimeError as exc:jars[version]={"verified":False,"message":str(exc)}
    model_files=[MODELS/"det/inference.onnx",MODELS/"rec/inference.onnx",MODELS/"rec/keys.txt"]
    DATA.mkdir(parents=True,exist_ok=True)
    probe=DATA/".write-test"
    probe.write_text("ok")
    probe.unlink()
    return {"python":platform.python_version(),"os":platform.platform(),"data_root":str(DATA),"writable":True,"tools":tools,"mustang":jars,"models":{str(path.relative_to(MODELS)):checksum(path) if path.exists() else None for path in model_files},"jev_key_configured":bool(os.getenv("TYPESAFE_API_KEY"))}

def main():
    parser=argparse.ArgumentParser(prog="python -m sourcecheck")
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("doctor")
    serve=sub.add_parser("serve");serve.add_argument("--host",default="127.0.0.1");serve.add_argument("--port",type=int,default=8770);serve.add_argument("--key-stdin",action="store_true")
    datasets=sub.add_parser("datasets");datasets.add_argument("action",choices=["prepare"]);datasets.add_argument("--manifest",default=str(ROOT/"configs/sources.json"));datasets.add_argument("--dry-run",action="store_true")
    models=sub.add_parser("models");models.add_argument("action",choices=["prepare"]);models.add_argument("--dry-run",action="store_true")
    demo=sub.add_parser("demo");demo.add_argument("action",choices=["prepare"]);demo.add_argument("--mode",choices=["offline"],default="offline")
    evaluation=sub.add_parser("evaluate");evaluation.add_argument("--config",default=str(ROOT/"configs/evaluation.json"));evaluation.add_argument("--dry-run",action="store_true");evaluation.add_argument("--live-jev",action="store_true");evaluation.add_argument("--key-stdin",action="store_true")
    report=sub.add_parser("report");report.add_argument("--run",required=True)
    verify=sub.add_parser("verify-export");verify.add_argument("path")
    storage=sub.add_parser("storage");storage.add_argument("action",choices=["inspect"])
    args=parser.parse_args()
    if args.command=="doctor":emit(doctor())
    elif args.command=="serve":
        if args.host not in {"127.0.0.1","localhost"} and not (args.host=="0.0.0.0" and os.getenv("SOURCECHECK_CONTAINER")=="1"):
            parser.error("Only loopback bind is supported outside the local container")
        if args.key_stdin:
            key_from_stdin()
        import uvicorn
        uvicorn.run("sourcecheck.web:app",host=args.host,port=args.port)
    elif args.command=="datasets":
        from .acquire import prepare_sources
        emit(prepare_sources(args.manifest,args.dry_run))
    elif args.command=="models":
        from .acquire import prepare_models
        emit(prepare_models(args.dry_run))
    elif args.command=="demo":
        from .service import create_case,start_run,get_run
        source=ROOT/"fixtures/owned-minimal-cii.xml"
        case=create_case("Owned local Mustang example",source.name,source.read_bytes())
        first=start_run(case,"mustang","2.26.0")
        second=start_run(case,"mustang","2.24.0",previous_id=first)
        emit({"mode":"offline with actual pinned Mustang executions","case_id":case,"runs":[{"id":first,"status":get_run(first)["status"]},{"id":second,"status":get_run(second)["status"]}],"url":"http://127.0.0.1:8770/"})
    elif args.command=="evaluate":
        from .evaluation import evaluate
        if args.key_stdin:
            if not args.live_jev:
                parser.error("--key-stdin requires --live-jev")
            key_from_stdin()
        if args.live_jev and not os.getenv("TYPESAFE_API_KEY"):
            parser.error("--live-jev requires TYPESAFE_API_KEY")
        emit(evaluate(args.config,args.dry_run,args.live_jev))
    elif args.command=="report":
        from .export import create_export
        emit(create_export(args.run))
    elif args.command=="verify-export":
        from .export import verify_export
        emit(verify_export(args.path))
    elif args.command=="storage":
        def size(path):return path.stat().st_size if path.is_file() else sum(file.stat().st_size for file in path.rglob("*") if file.is_file()) if path.exists() else 0
        emit({"data_root":str(DATA),"database_bytes":size(DATA/"sourcecheck.sqlite") if (DATA/"sourcecheck.sqlite").exists() else 0,"models_bytes":size(MODELS),"datasets_bytes":size(DATA/"datasets"),"originals_bytes":size(DATA/"originals"),"destinations_bytes":size(DATA/"destinations"),"exports_bytes":size(DATA/"exports"),"jev_cache_bytes":size(DATA/"jev-cache"),"tools_bytes":size(TOOLS)})

if __name__=="__main__":main()
