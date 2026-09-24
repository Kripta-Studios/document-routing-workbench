"""Pinned, subprocess-isolated Mustang importer bridge."""
import hashlib
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from .config import DATA, TOOLS, VERSIONS
from .source import safe_xml

PINNED = {"2.26.0": (59163641, "42d7868cb68264874a7b8cab4c3587b03b23ccc7cd72373da917f66758bb9736"), "2.24.0": (58755189, "e4904ffa0afdce3f5836dceb927c440a05ed5d60386fdd37e17a4b2f7652edbf")}

def jar_for(version):
    if version not in VERSIONS:
        raise ValueError("Unsupported Mustang version")
    jar = TOOLS / f"mustang-{version}.jar"
    if not jar.exists() or jar.stat().st_size != PINNED[version][0] or hashlib.sha256(jar.read_bytes()).hexdigest() != PINNED[version][1]:
        raise RuntimeError(f"Pinned Mustang {version} JAR missing or hash mismatch; run datasets prepare")
    return jar

def compile_bridge(version="2.26.0"):
    jar = jar_for(version)
    source = Path(__file__).resolve().parents[1] / "bridge" / "SourceCheckBridge.java"
    output = DATA / "bridge"
    output.mkdir(parents=True, exist_ok=True)
    compiled = output / "SourceCheckBridge.class"
    if not compiled.exists() or compiled.stat().st_mtime < source.stat().st_mtime:
        proc = subprocess.run([os.getenv("SOURCECHECK_JAVAC", "javac"), "--release", "21", "-cp", str(jar), "-d", str(output), str(source)], capture_output=True, text=True, timeout=60)
        if proc.returncode:
            raise RuntimeError("Bridge compilation failed: " + proc.stderr[:2000])
    return output

def import_xml(xml, version):
    safe_xml(xml)
    jar = jar_for(version)
    bridge = compile_bridge()
    DATA.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mustang-", dir=DATA) as directory:
        path = Path(directory) / "invoice.xml"
        path.write_bytes(xml)
        started = time.perf_counter()
        proc = subprocess.run([os.getenv("SOURCECHECK_JAVA", "java"), "-Xmx384m", "-cp", os.pathsep.join([str(bridge), str(jar)]), "SourceCheckBridge", str(path)], capture_output=True, text=True, timeout=45, cwd=directory)
        elapsed = round((time.perf_counter() - started) * 1000, 2)
        if proc.returncode:
            raise RuntimeError("Mustang importer failed: " + proc.stderr[-2000:])
        data = json.loads(proc.stdout)
        return {"data": data, "elapsed_ms": elapsed, "tool_sha256": PINNED[version][1], "bridge_sha256": hashlib.sha256(Path(__file__).resolve().parents[1].joinpath("bridge/SourceCheckBridge.java").read_bytes()).hexdigest(), "command": "java -Xmx384m -cp <bridge>:<pinned-jar> SourceCheckBridge <input.xml>", "mode": "actual_importer_execution"}
