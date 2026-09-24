"""Pinned bounded downloads with local SHA/byte records."""
import hashlib
import json
import urllib.request
from pathlib import Path
import yaml
from .config import DATA, MODELS, ROOT, TOOLS
from .store import now

def checksum(path):
    h=hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda:file.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def download(url,target,limit):
    target.parent.mkdir(parents=True,exist_ok=True)
    temporary=target.with_suffix(target.suffix+".partial")
    received=0
    try:
        with urllib.request.urlopen(url,timeout=60) as response,temporary.open("wb") as output:
            while True:
                chunk=response.read(min(1024*1024,limit-received+1))
                if not chunk:break
                received+=len(chunk)
                if received>limit:raise ValueError("Download exceeded planned byte bound")
                output.write(chunk)
        temporary.replace(target)
        return received
    finally:
        temporary.unlink(missing_ok=True)

def prepare_sources(manifest=ROOT/"configs/sources.json",dry_run=False):
    spec=json.loads(Path(manifest).read_text(encoding="utf-8"))
    entries=[]
    missing=0
    dataset_missing=0
    for item in spec["artifacts"]:
        target=TOOLS/f"{item['id']}.jar" if item["id"].startswith("mustang-") else DATA/"datasets"/f"{item['id']}.xml"
        cached=target.exists() and target.stat().st_size==item["bytes"] and checksum(target)==item["sha256"]
        if not cached:
            missing+=item["bytes"]
            if not item["id"].startswith("mustang-"):dataset_missing+=item["bytes"]
        entries.append({**item,"target":str(target),"cached":cached})
    if missing>spec["budget_bytes"] or dataset_missing>spec["dataset_budget_bytes"]:
        raise ValueError("Planned transfers exceed budget")
    result={"planned_new_bytes":missing,"planned_dataset_bytes":dataset_missing,"artifacts":entries,"dry_run":dry_run}
    if dry_run:return result
    records=[]
    transferred=0
    for item in entries:
        target=Path(item["target"])
        used=0 if item["cached"] else download(item["url"],target,item["bytes"])
        transferred+=used
        if target.stat().st_size!=item["bytes"]:
            raise ValueError("Artifact size mismatch: "+item["id"])
        value=checksum(target)
        if value!=item["sha256"]:
            raise ValueError("Artifact hash mismatch")
        records.append({"id":item["id"],"url":item["url"],"revision":item["revision"],"license":item["license"],"sha256":value,"bytes":target.stat().st_size,"transferred_bytes":used,"acquired":now()})
    result.update({"transferred_bytes":transferred,"records":records})
    DATA.mkdir(parents=True,exist_ok=True)
    (DATA/"source-acquisition.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result

def prepare_models(dry_run=False):
    spec=json.loads((ROOT/"configs/models.json").read_text(encoding="utf-8"))
    entries=[]
    for item in spec["files"]:
        target=MODELS/item["role"]/item["name"]
        cached=target.exists() and target.stat().st_size==item["bytes"] and (not item.get("sha256") or checksum(target)==item["sha256"])
        entries.append({**item,"target":str(target),"cached":cached})
    planned=sum(item["bytes"] for item in entries if not item["cached"])
    if planned>20*1024*1024:raise ValueError("OCR model transfer budget exceeded")
    result={"profile":spec["profile"],"planned_new_bytes":planned,"files":entries,"dry_run":dry_run}
    if dry_run:return result
    transferred=0
    for item in entries:
        target=Path(item["target"])
        if not item["cached"]:
            url=f"https://huggingface.co/{item['repo']}/resolve/{item['revision']}/{item['name']}"
            transferred+=download(url,target,item["bytes"])
        if target.stat().st_size!=item["bytes"] or (item.get("sha256") and checksum(target)!=item["sha256"]):
            raise ValueError("OCR model identity mismatch")
    metadata=yaml.safe_load((MODELS/"rec/inference.yml").read_text(encoding="utf-8"))
    characters=metadata["PostProcess"]["character_dict"]
    keys=MODELS/"rec/keys.txt"
    # The inspected trace-it downloader produced CRLF bytes on Windows. Pin those
    # exact dictionary bytes so Linux and Windows use the same hashed model input.
    keys.write_bytes(("\r\n".join(characters)+"\r\n").encode("utf-8"))
    if checksum(keys)!=spec["keys_sha256"]:raise ValueError("OCR dictionary hash mismatch")
    result["transferred_bytes"]=transferred
    result["records"]=[{"repo":item["repo"],"revision":item["revision"],"name":item["name"],"bytes":item["bytes"],"sha256":checksum(Path(item["target"]))} for item in entries]
    (MODELS/"sourcecheck-manifest.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
