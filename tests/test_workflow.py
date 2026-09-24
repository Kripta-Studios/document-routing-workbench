import io
import json
import zipfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sourcecheck import store
from sourcecheck import export as export_module
from sourcecheck import service
from sourcecheck.compare import compare
from sourcecheck.export import create_export, verify_export
from sourcecheck.source import read_source, safe_xml

SOURCE = Path(__file__).resolve().parents[1].joinpath("fixtures/owned-minimal-cii.xml").read_bytes()

@pytest.fixture
def isolated(tmp_path,monkeypatch):
    monkeypatch.setattr(store,"DATA",tmp_path)
    monkeypatch.setattr(export_module,"DATA",tmp_path)
    return tmp_path

def target(**updates):
    return {"number":"SC-OWNED-001","issue_date":"2026-09-24","currency":"EUR","buyer_order":"PO-OWNED-9",**updates}

def test_coverage_numeric_and_conflict():
    source=read_source(SOURCE,"invoice.xml")
    profile=service.default_profile()
    by_id=lambda result:{item["id"]:item for item in result}
    equal=by_id(compare(SOURCE,source,target(issue_date="20260924"),profile))
    assert equal["issue_date"]["result"]=="equal"
    assert equal["grand_total"]["result"]=="not_checkable"
    missing=by_id(compare(SOURCE,source,target(buyer_order=None),profile))
    assert missing["buyer_order"]["result"]=="missing"
    unknown=json.loads(json.dumps(profile))
    next(item for item in unknown["checks"] if item["id"]=="buyer_order")["coverage"]="unknown"
    assert by_id(compare(SOURCE,source,target(buyer_order=None),unknown))["buyer_order"]["result"]=="not_checkable"
    conflict=by_id(compare(SOURCE,source,target(),profile,{"number":[{"raw":"DIFFERENT","method":"human_reviewed","path":"page 1","bbox":None}]}))
    assert conflict["number"]["source_state"]=="conflicting"
    assert conflict["number"]["result"]=="not_checkable"
    amount=json.loads(json.dumps(profile))
    next(item for item in amount["checks"] if item["id"]=="grand_total")["coverage"]="complete"
    assert by_id(compare(SOURCE,source,target(grand_total="-10.00"),amount))["grand_total"]["result"]=="different"

def test_unsafe_xml_and_ambiguous_lines():
    with pytest.raises(Exception):safe_xml(b'<!DOCTYPE x [<!ENTITY e SYSTEM "file:///secret">]><x>&e;</x>')
    source=read_source(SOURCE,"invoice.xml")
    findings=compare(SOURCE,source,target(lines=[{"name":"same"},{"name":"same"}]),service.default_profile())
    assert next(item for item in findings if item["id"]=="line_alignment")["coverage"]=="ambiguous"

def test_persistence_review_rerun_export_and_delete(isolated):
    case=service.create_case("Test", "invoice.xml",SOURCE)
    coverage={"reviewed":True,"field_coverage":{"buyer_order":"complete"}}
    first=service.start_run(case,"authored_simulation",destination_content=json.dumps(target(buyer_order=None)).encode(),destination_name="first.json",coverage_contract=coverage)
    assert service.get_run(first)["status"]=="complete"
    service.review(first,"buyer_order","Automated test","confirmed_issue","Original order reference is absent","deterministic_constructed")
    service.save_reference(case,first,"Tester")
    second=service.start_run(case,"authored_simulation",destination_content=json.dumps(target()).encode(),destination_name="second.json",previous_id=first,coverage_contract=coverage)
    rerun=service.get_run(second)
    assert next(item for item in rerun["diff"] if item["id"]=="buyer_order")["status"]=="changed"
    assert rerun["reviews"]==[]
    assert service.get_run(first)["reviews"][0]["disposition"]=="confirmed_issue"
    exported=create_export(first)
    assert verify_export(exported["path"])["run_id"]==first
    bad=isolated/"bad.zip"
    with zipfile.ZipFile(exported["path"]) as archive,zipfile.ZipFile(bad,"w") as output:
        for name in archive.namelist():output.writestr(name,b"tampered" if name=="findings.csv" else archive.read(name))
    with pytest.raises(ValueError):verify_export(bad)
    assert service.delete_case(case)>=3
    assert not Path(exported["path"]).exists()

def test_mutation_guard_and_failed_retry(isolated):
    from sourcecheck.web import app
    with TestClient(app) as client:
        denied=client.post("/api/cases",data={"title":"x"},files={"source":("invoice.xml",SOURCE,"application/xml")})
        assert denied.status_code==403
        created=client.post("/api/cases",headers={"X-SourceCheck":"1"},data={"title":"x"},files={"source":("invoice.xml",SOURCE,"application/xml")})
        assert created.status_code==200
        case=created.json()["id"]
        failed=client.post(f"/api/cases/{case}/runs",headers={"X-SourceCheck":"1"},data={"mode":"uploaded_json"},files={"destination":("bad.json",b"{","application/json")}).json()["id"]
        assert client.get(f"/api/runs/{failed}").json()["status"]=="failed"
        retry=client.post(f"/api/runs/{failed}/retry",headers={"X-SourceCheck":"1"})
        assert retry.status_code==200
        assert retry.json()["id"]!=failed

def test_interrupted_job_is_visible_after_restart(isolated):
    from sourcecheck.web import app
    case=service.create_case("Restart","invoice.xml",SOURCE)
    run=service.start_run(case,"authored_simulation",destination_content=b'{"number":"SC-OWNED-001"}')
    with store.db() as con:
        con.execute("UPDATE runs SET status='running' WHERE id=?",(run,))
        con.execute("UPDATE jobs SET status='running' WHERE run_id=?",(run,))
    with TestClient(app) as client:
        recovered=client.get(f"/api/runs/{run}").json()
        assert recovered["status"]=="failed"
        assert "retry explicitly" in recovered["error"]
