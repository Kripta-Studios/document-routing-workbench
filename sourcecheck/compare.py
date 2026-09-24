"""Coverage-aware exact comparison and conservative line alignment."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from .source import safe_xml, select_xml

VERSION = "exact-1"

def normalize(raw, kind, check):
    if raw is None:
        return None
    value = str(raw).strip()
    if kind == "date":
        try:
            if len(value) == 8 and value.isdigit():
                return datetime.strptime(value, "%Y%m%d").date().isoformat()
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            return None
    if kind == "decimal":
        try:
            return str(Decimal(value))
        except InvalidOperation:
            return None
    if kind == "text" and check.get("normalization") == "whitespace":
        return " ".join(value.split())
    return value

def get_path(data, path):
    current = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current

def xml_lines(root):
    if root is None:
        return []
    result=[]
    for node in root.iter():
        if node.tag.rsplit("}",1)[-1]!="IncludedSupplyChainTradeLineItem":
            continue
        def child_value(path):
            current=node
            for part in path.split("/"):
                current=next((child for child in current if child.tag.rsplit("}",1)[-1]==part),None)
                if current is None:return None
            return "".join(current.itertext()).strip() or None
        result.append({"id":child_value("AssociatedDocumentLineDocument/LineID"),"name":child_value("SpecifiedTradeProduct/Name"),"quantity":child_value("SpecifiedLineTradeDelivery/BilledQuantity"),"price":child_value("SpecifiedLineTradeAgreement/NetPriceProductTradePrice/ChargeAmount")})
    return result

def compare(source_bytes, source_data, destination, profile, manual=None):
    root = None
    if source_data["kind"] == "xml":
        root = safe_xml(source_bytes)
    elif source_data.get("embedded_xml"):
        from .source import embedded_xml
        root = safe_xml(embedded_xml(source_bytes))
    manual = manual or {}
    findings = []
    for check in profile["checks"]:
        key = check["id"]
        xml_observations = select_xml(root, check["source"]) if root is not None else []
        reviewed_observations = manual.get(key, [])
        observations = xml_observations + reviewed_observations
        conflicting = bool(xml_observations and reviewed_observations and normalize(xml_observations[0]["raw"],check["kind"],check) != normalize(reviewed_observations[0]["raw"],check["kind"],check))
        source_state = "conflicting" if conflicting else "available" if len(observations) == 1 or (len(xml_observations)==1 and len(reviewed_observations)==1) else "uncertain" if len(observations) > 1 else "unsupported"
        source = observations[0] if source_state == "available" else None
        exists, raw_destination = get_path(destination, check["destination"])
        coverage = check.get("coverage", "unknown")
        target_state = "observable" if exists and raw_destination is not None else "observable" if coverage == "complete" else "unobserved"
        source_norm = normalize(source["raw"], check["kind"], check) if source else None
        target_norm = normalize(raw_destination, check["kind"], check) if exists else None
        if source_state != "available" or source_norm is None:
            result = "not_checkable"
        elif target_state == "unobserved":
            result = "not_checkable"
        elif raw_destination is None or raw_destination == "":
            result = "missing"
        elif target_norm is None:
            result = "not_checkable"
        elif check["kind"] == "decimal":
            tolerance = Decimal(str(check.get("tolerance", "0")))
            result = "equal" if abs(Decimal(source_norm) - Decimal(target_norm)) <= tolerance else "different"
        elif check["kind"] == "text" and source_norm != target_norm:
            result = "semantic_review"
        else:
            result = "equal" if source_norm == target_norm else "different"
        findings.append({"id": key, "label": check.get("label", key), "requirement": "configured_required" if check.get("required") else "informational", "source_state": source_state, "coverage": target_state, "result": result, "source": source, "source_candidates": observations if len(observations) > 1 else [], "source_normalized": source_norm, "destination_path": check["destination"], "destination_raw": raw_destination if exists else None, "destination_normalized": target_norm, "profile_check": check, "comparator": VERSION})
    # Stable line IDs only; duplicate IDs or ID-less repeated lines are ambiguous.
    if profile.get("line_alignment") == "stable_id":
        dest_lines = destination.get("lines") if isinstance(destination.get("lines"),list) else []
        source_items=xml_lines(root)
        ids = [str(line.get("id")) for line in dest_lines if line.get("id") is not None]
        source_ids=[str(line.get("id")) for line in source_items if line.get("id") is not None]
        ambiguous=len(ids) != len(set(ids)) or any(line.get("id") is None for line in dest_lines) or len(source_ids)!=len(set(source_ids)) or any(line.get("id") is None for line in source_items)
        if ambiguous:
            findings.append({"id": "line_alignment", "label": "Line correspondence", "requirement": "informational", "source_state": "uncertain", "coverage": "ambiguous", "result": "not_checkable", "source": None, "destination_path": "lines", "destination_raw": None, "comparator": VERSION})
        elif source_items:
            indexed={str(item["id"]):item for item in dest_lines}
            for item in source_items:
                target=indexed.get(str(item["id"]))
                for field,kind in (("name","text"),("quantity","decimal"),("price","decimal")):
                    raw=item[field]
                    if raw is None:continue
                    target_raw=target.get(field) if target else None
                    coverage="observable" if target_raw is not None or profile.get("lines_coverage")=="complete" else "unobserved"
                    source_norm=normalize(raw,kind,{})
                    target_norm=normalize(target_raw,kind,{})
                    if coverage=="unobserved":status="not_checkable"
                    elif target_raw is None:status="missing"
                    elif source_norm is None or target_norm is None:status="not_checkable"
                    elif kind=="text" and source_norm!=target_norm:status="semantic_review"
                    else:status="equal" if source_norm==target_norm else "different"
                    findings.append({"id":f"line:{item['id']}:{field}","label":f"Line {item['id']} {field}","requirement":"informational","source_state":"available","coverage":coverage,"result":status,"source":{"raw":raw,"method":"xml","path":f"IncludedSupplyChainTradeLineItem[LineID={item['id']}]/.../{field}","page":None,"bbox":None},"source_candidates":[],"source_normalized":source_norm,"destination_path":f"lines[id={item['id']}].{field}","destination_raw":target_raw,"destination_normalized":target_norm,"comparator":VERSION})
    return findings

def diff(previous, current, old_profile, new_profile):
    old = {f["id"]: f for f in previous or []}
    changes = []
    for item in current:
        before = old.get(item["id"])
        status = "new" if before is None else "unchanged" if (before.get("result"), before.get("destination_raw"), before.get("source_normalized")) == (item.get("result"), item.get("destination_raw"), item.get("source_normalized")) else "changed"
        changes.append({"id": item["id"], "status": status, "before": before.get("result") if before else None, "after": item["result"], "comparable": old_profile == new_profile})
    for key in old.keys() - {item["id"] for item in current}:
        changes.append({"id": key, "status": "resolved_or_removed", "before": old[key]["result"], "after": None, "comparable": old_profile == new_profile})
    return changes
