"""Small, explicitly constructed functional suite and genuine importer observations."""
import hashlib
import json
from difflib import SequenceMatcher
from pathlib import Path
from .config import DATA, ROOT
from .compare import compare
from .mustang import import_xml
from .service import default_profile
from .source import read_source, sha
from .store import now, uid

def split_family(identity, seed=20260924):
    bucket=int(hashlib.sha256(f"{seed}:{identity}".encode()).hexdigest()[:8],16)/0xffffffff
    return "development" if bucket<.6 else "validation" if bucket<.8 else "test"

def manifest(config):
    spec=json.loads(Path(config).read_text(encoding="utf-8"))
    families=[]
    for item in spec["families"]:
        source=ROOT/item["source"] if not item["source"].startswith("private acquisition:") else DATA/"datasets"/"cii-business-example-02.xml"
        if source.exists():
            families.append({"id":item["id"],"source_sha256":sha(source.read_bytes()),"split":split_family(item["id"],spec["seed"]),"origin":item["origin"],"redistribution":item["redistribution"]})
    return families

def evaluate(config=ROOT/"configs/evaluation.json",dry_run=False):
    families=manifest(config)
    frozen=json.loads((ROOT/"configs/evaluation-manifest.json").read_text(encoding="utf-8"))
    expected={item["id"]:(item["source_sha256"],item["split"]) for item in frozen["families"]}
    for item in families:
        if expected.get(item["id"])!=(item["source_sha256"],item["split"]):
            raise ValueError("Evaluation family manifest changed; freeze a new version before evaluation")
    if dry_run:return {"dry_run":True,"families":families,"unique_families":len(families),"warning":"Small family count does not establish detection accuracy"}
    source=(ROOT/"fixtures/owned-minimal-cii.xml").read_bytes()
    source_data=read_source(source,"owned-minimal-cii.xml")
    profile=default_profile()
    baseline={"number":"SC-OWNED-001","issue_date":"2026-09-24","currency":"EUR","buyer_order":"PO-OWNED-9","lines":[{"id":"1","name":"Review service"}]}
    variants={
        "unchanged":(baseline,{"number":"equal","issue_date":"equal","currency":"equal","buyer_order":"equal"}),
        "normalized_date":({**baseline,"issue_date":"20260924"},{"issue_date":"equal"}),
        "omitted_order":({**baseline,"buyer_order":None},{"buyer_order":"missing"}),
        "changed_number":({**baseline,"number":"SC-OWNED-999"},{"number":"different"}),
        "unknown_coverage":({**baseline,"buyer_order":None},{"buyer_order":"not_checkable"}),
        "repeated_lines":({**baseline,"lines":[{"name":"Review service"},{"name":"Review service"}]},{"line_alignment":"not_checkable"})
    }
    records=[]
    for name,(target,expected) in variants.items():
        local_profile=json.loads(json.dumps(profile))
        if name=="unknown_coverage":
            next(item for item in local_profile["checks"] if item["id"]=="buyer_order")["coverage"]="unknown"
        findings=compare(source,source_data,target,local_profile)
        actual={item["id"]:item["result"] for item in findings}
        records.append({"variant":name,"mode":"authored_simulation","annotation_origin":"deterministic_constructed","expected":expected,"actual":{key:actual.get(key) for key in expected},"passed":all(actual.get(key)==value for key,value in expected.items())})
    real=[]
    sources=[("owned-minimal-cii",source)]
    private=DATA/"datasets"/"cii-business-example-02.xml"
    if private.exists():sources.append(("connecting-europe-business-02",private.read_bytes()))
    for family,document in sources:
        observation=read_source(document,"invoice.xml")
        for version in ("2.26.0","2.24.0"):
            captured=import_xml(document,version)
            findings=compare(document,observation,captured["data"],profile)
            real.append({"family":family,"version":version,"mode":"actual_importer_execution","tool_sha256":captured["tool_sha256"],"elapsed_ms":captured["elapsed_ms"],"counts":{label:sum(item["result"]==label for item in findings) for label in ("equal","different","missing","not_checkable")},"findings":{item["id"]:item["result"] for item in findings}})
    semantic_pairs=[("Pay within thirty days","Payment is due in 30 days","equivalent"),("Payment by bank transfer","Payment by direct debit","contradictory"),("Pay by bank transfer within 30 days","Pay by bank transfer","partially_preserved"),("Payment terms illegible","Payment due in 30 days","insufficient_evidence")]
    semantic=[]
    for original,captured,expected in semantic_pairs:
        ratio=SequenceMatcher(None,original.casefold(),captured.casefold()).ratio()
        lexical="equivalent" if ratio>=.86 else "insufficient_evidence"
        semantic.append({"source":original,"destination":captured,"expected":expected,"annotation_origin":"deterministic_constructed","rules_only":"abstain","lexical_prediction":lexical,"lexical_similarity":round(ratio,3),"jev_prediction":None})
    result={"run_id":uid(),"created":now(),"manifest":families,"manifest_sha256":sha(json.dumps(families,sort_keys=True).encode()),"functional_records":records,"functional_passed":sum(item["passed"] for item in records),"functional_total":len(records),"real_importer":real,"semantic_constructed":semantic,"jev":{"status":"not_run","contribution":"insufficient evidence"},"pilot":"not_run"}
    directory=DATA/"evaluation"
    directory.mkdir(parents=True,exist_ok=True)
    (directory/f"{result['run_id']}.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
