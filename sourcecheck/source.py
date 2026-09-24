"""Independent, bounded source observations. Importer output is never a reference."""
import hashlib
import io
from pathlib import Path
from defusedxml import ElementTree as ET
from PIL import Image, ImageOps
from .config import MAX_FILE, MAX_PAGES, MAX_PIXELS, MODELS

def sha(data):
    return hashlib.sha256(data).hexdigest()

def local(tag):
    return tag.rsplit("}", 1)[-1]

def safe_xml(raw):
    if len(raw) > MAX_FILE or b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("XML exceeds the limit or declares a DTD/entity")
    root = ET.fromstring(raw)
    stack = [(root, 1)]
    nodes = 0
    while stack:
        node, depth = stack.pop()
        nodes += 1
        if depth > 80 or nodes > 150_000:
            raise ValueError("XML depth/node limit exceeded")
        stack.extend((child, depth + 1) for child in node)
    return root

def select_xml(root, selector):
    parts = selector.split("/")
    matches = []
    def visit(node, path):
        here = path + [local(node.tag)]
        if here[-len(parts):] == parts:
            value = "".join(node.itertext()).strip()
            if value:
                matches.append({"raw": value, "path": "/".join(here), "method": "xml", "page": None, "bbox": None})
        for child in node:
            visit(child, here)
    visit(root, [])
    return matches[:20]

def _ocr(image, page):
    import yaml
    from rapidocr import OCRVersion, RapidOCR
    from .config import MODELS
    paths = {"Det.model_path": MODELS / "det/inference.onnx", "Rec.model_path": MODELS / "rec/inference.onnx", "Rec.rec_keys_path": MODELS / "rec/keys.txt"}
    if any(not path.exists() for path in paths.values()):
        raise RuntimeError("OCR models missing; run sourcecheck models prepare")
    metadata = yaml.safe_load((MODELS / "det/inference.yml").read_text(encoding="utf-8"))
    normalize = next(item["NormalizeImage"] for item in metadata["PreProcess"]["transform_ops"] if "NormalizeImage" in item)
    post = metadata["PostProcess"]
    params = {key: str(path) for key, path in paths.items()}
    params.update({"Global.use_cls": False, "Global.log_level": "warning", "Det.ocr_version": OCRVersion.PPOCRV5, "Rec.ocr_version": OCRVersion.PPOCRV5, "Det.mean": normalize["mean"], "Det.std": normalize["std"], "Det.thresh": post["thresh"], "Det.box_thresh": post["box_thresh"], "Det.unclip_ratio": post["unclip_ratio"], "Det.limit_side_len": 2048, "Det.limit_type": "max", "EngineConfig.onnxruntime.intra_op_num_threads": 2})
    image = ImageOps.exif_transpose(image).convert("RGB")
    if image.width * image.height > MAX_PIXELS:
        raise ValueError("Image exceeds 18 megapixels")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    result = RapidOCR(params=params)(buffer.getvalue(), use_cls=False)
    lines = []
    for index, (box, value, confidence) in enumerate(zip(result.boxes if result.boxes is not None else [], result.txts if result.txts is not None else [], result.scores if result.scores is not None else [])):
        xs, ys = zip(*box)
        lines.append({"id": f"p{page}:ocr:{index}", "raw": str(value), "page": page, "bbox": [float(min(xs)), float(min(ys)), float(max(xs)), float(max(ys))], "confidence": float(confidence), "method": "ocr"})
    return lines

def read_source(raw, filename, use_ocr=True):
    if not raw or len(raw) > MAX_FILE:
        raise ValueError("Source must be 1 byte to 25 MiB")
    kind = Path(filename).suffix.lower().lstrip(".")
    result = {"kind": kind, "sha256": sha(raw), "representations": [], "lines": [], "xml_facts": {}, "warnings": [], "embedded_xml": None}
    if kind == "xml":
        root = safe_xml(raw)
        result["representations"].append({"kind": "xml", "root": local(root.tag)})
    elif kind == "pdf" and raw.startswith(b"%PDF"):
        import pymupdf
        with pymupdf.open(stream=raw, filetype="pdf") as doc:
            if len(doc) > MAX_PAGES:
                raise ValueError("PDF exceeds 20 pages")
            for index, page in enumerate(doc):
                text = page.get_text(sort=True)
                if len(text) > 200_000:
                    text = text[:200_000]
                    result["warnings"].append("Page text truncated")
                native_used=sum(char.isalnum() for char in text) >= 40
                if native_used:
                    number=0
                    for block in page.get_text("dict",sort=True).get("blocks",[]):
                        if "lines" not in block:continue
                        for line in block["lines"]:
                            spans=line.get("spans",[])
                            value="".join(span.get("text","") for span in spans).strip()
                            if not value:continue
                            box=[float(min(span["bbox"][0] for span in spans)),float(min(span["bbox"][1] for span in spans)),float(max(span["bbox"][2] for span in spans)),float(max(span["bbox"][3] for span in spans))]
                            result["lines"].append({"id": f"p{index+1}:native:{number}", "raw": value, "page": index + 1, "bbox": box, "confidence": None, "method": "native_pdf"})
                            number+=1
                elif use_ocr:
                    scale = min(180 / 72, (MAX_PIXELS / max(1, page.rect.width * page.rect.height)) ** .5)
                    pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
                    with Image.open(io.BytesIO(pix.tobytes("png"))) as image:
                        result["lines"].extend(_ocr(image, index + 1))
                result["representations"].append({"kind": "pdf_page", "page": index+1, "width": page.rect.width, "height": page.rect.height, "rotation": page.rotation, "text_method": "native" if native_used else "ocr" if use_ocr else "unread", "ocr_dpi": 180 if not native_used and use_ocr else None})
            if doc.embfile_count() > 10:
                result["warnings"].append("Embedded attachment count exceeds inspection limit")
            else:
                for index in range(doc.embfile_count()):
                    info = doc.embfile_info(index)
                    if not str(info.get("filename", "")).lower().endswith(".xml") or info.get("size", 0) > MAX_FILE:
                        continue
                    embedded = doc.embfile_get(index)
                    safe_xml(embedded)
                    result["embedded_xml"] = {"name": info.get("filename"), "sha256": sha(embedded), "bytes": len(embedded)}
                    result["representations"].append({"kind": "embedded_xml", **result["embedded_xml"]})
                    break
    elif kind in {"png", "jpg", "jpeg"}:
        with Image.open(io.BytesIO(raw)) as image:
            image.verify()
        with Image.open(io.BytesIO(raw)) as image:
            if image.width * image.height > MAX_PIXELS:
                raise ValueError("Image exceeds 18 megapixels")
            result["representations"].append({"kind": "image", "width": image.width, "height": image.height})
            if use_ocr:
                result["lines"] = _ocr(image, 1)
    else:
        raise ValueError("Supported source formats: XML, PDF, PNG, JPEG")
    result["lines"] = result["lines"][:5000]
    if any(line["method"]=="ocr" for line in result["lines"]):
        result["ocr_models"]={str(path.relative_to(MODELS)):sha(path.read_bytes()) for path in (MODELS/"det/inference.onnx",MODELS/"rec/inference.onnx",MODELS/"rec/keys.txt")}
    return result

def embedded_xml(raw):
    import pymupdf
    with pymupdf.open(stream=raw, filetype="pdf") as doc:
        for index in range(min(doc.embfile_count(), 10)):
            info = doc.embfile_info(index)
            if str(info.get("filename", "")).lower().endswith(".xml") and info.get("size", 0) <= MAX_FILE:
                value = doc.embfile_get(index)
                safe_xml(value)
                return value
    raise ValueError("PDF has no supported embedded XML")
