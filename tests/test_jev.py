import json
import urllib.error
import pytest
from sourcecheck import jev,store,service
from sourcecheck.jev import payload,validate
from pathlib import Path

def test_jev_contract_and_failures():
    request=payload("Pay within 30 days","Due in one month","payment due timing")
    assert "invoice" in request["questions"]["relation"]["instructions"]
    valid={"model":"jev-1.13.0","answers":{"relation":{"type":"choice","choice":"equivalent","probabilities":{"equivalent":.7,"contradictory":.1,"partially_preserved":.1,"insufficient_evidence":.1},"confidence":.4}},"usage":{"input_tokens":100,"output_tokens":10}}
    assert validate(valid)==valid
    with pytest.raises(ValueError):validate({**valid,"usage":{"input_tokens":-1,"output_tokens":10}})
    with pytest.raises(ValueError):payload("x"*1801,"y","criterion")

def test_transport_failure_keeps_unknown_delivery(tmp_path,monkeypatch):
    monkeypatch.setattr(store,"DATA",tmp_path)
    monkeypatch.setattr(jev,"DATA",tmp_path)
    source=Path(__file__).resolve().parents[1].joinpath("fixtures/owned-minimal-cii.xml").read_bytes()
    case=service.create_case("Semantic","invoice.xml",source)
    profile={"name":"text relation","checks":[{"id":"number_text","label":"Invoice label","source":"ExchangedDocument/ID","destination":"number","kind":"text","required":True,"coverage":"complete"}]}
    service.add_profile(case,profile)
    coverage={"reviewed":True,"field_coverage":{"number":"complete"}}
    run=service.start_run(case,"authored_simulation",destination_content=b'{"number":"invoice SC-OWNED-001"}',coverage_contract=coverage)
    assert service.get_run(run)["findings"][0]["result"]=="semantic_review"
    monkeypatch.setenv("TYPESAFE_API_KEY","test-only")
    calls=[]
    def fail(*args,**kwargs):
        calls.append(1)
        raise urllib.error.URLError("offline")
    monkeypatch.setattr(jev.urllib.request,"urlopen",fail)
    with pytest.raises(ValueError,match="delivery"):
        jev.suggest(run,"number_text")
    with pytest.raises(ValueError,match="unknown delivery"):
        jev.suggest(run,"number_text")
    assert len(calls)==1
    with store.db() as con:
        status=con.execute("SELECT status FROM semantic_runs").fetchone()[0]
    assert status=="delivery_unknown"
