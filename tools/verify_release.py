#!/usr/bin/env python3
"""Verify self-contained skill packages and run their extracted CLI examples."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def links(root):
    for path in root.rglob("*.md"):
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = path.parent / link.split("#")[0]
            if not target.exists():
                raise ValueError(f"Broken reference: {path.relative_to(root)} -> {link}")


def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise ValueError(result.stdout + result.stderr)
    return result


def main():
    links(ROOT / "skills")
    dist = ROOT / "dist"
    manifest = json.loads((dist / "upload/packages-v0.2.0.json").read_text(encoding="utf-8"))
    for entry in manifest["packages"]:
        path = dist / "upload" / entry["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("Package hash mismatch: " + path.name)
        with zipfile.ZipFile(path) as archive, tempfile.TemporaryDirectory() as temp:
            names = archive.namelist()
            if len(set(names)) != len(names) or archive.testzip() is not None:
                raise ValueError("Duplicate entries or CRC failure: " + path.name)
            for name in names:
                parts = PurePosixPath(name).parts
                if name.startswith("/") or "\\" in name or any(p.startswith(".") or ":" in p or p == "__pycache__" for p in parts):
                    raise ValueError("Unsafe or hidden path: " + name)
                if name.endswith("SKILL.md") and archive.read(name).startswith(b"\xef\xbb\xbf"):
                    raise ValueError("BOM-prefixed skill: " + name)
            if [n for n in names if n.endswith("SKILL.md")] != ["SKILL.md"]:
                raise ValueError("Exactly one root skill entry is required.")
            if len(names) != entry["files"]:
                raise ValueError("File count differs from manifest.")
            source_root = ROOT / "skills" / entry["skill"].removeprefix("dsh-")
            for name in names:
                if name == "SKILL.md":
                    source = (source_root / name).read_text(encoding="utf-8")
                    published = archive.read(name).decode("utf-8")
                    if source.split("\n---\n", 1)[1] != published.split("\n---\n", 1)[1]:
                        raise ValueError("Published skill body differs from source.")
                    if not re.search(r'^name: ' + re.escape(entry["skill"]) + r'$', published, re.M):
                        raise ValueError("Published skill name differs from manifest.")
                elif name == "LICENSE":
                    if archive.read(name) != (ROOT / "LICENSE").read_bytes():
                        raise ValueError("Published license differs from repository.")
                elif archive.read(name) != (source_root / name).read_bytes():
                    raise ValueError("Published resource differs from source: " + name)
            archive.extractall(temp)
            extracted = Path(temp)
            links(extracted)
            result = run([sys.executable, "-B", "scripts/check.py", "references/example.json"], extracted)
            if json.loads(result.stdout)["status"] != "passed":
                raise ValueError("Extracted example did not pass: " + path.name)
        print("Verified:", path.name)
    manual = dist / "admin-expert-kit-v0.2.0-MANUAL-ONLY.zip"
    with zipfile.ZipFile(manual) as archive, tempfile.TemporaryDirectory() as temp:
        if archive.testzip() is not None:
            raise ValueError("Suite CRC failure")
        archive.extractall(temp)
        links(Path(temp))
        run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"], temp)
    print("Verified: manual suite extracted regression tests.")
    for line in (dist / "SHA256SUMS-v0.2.0.txt").read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        if hashlib.sha256((dist / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Artifact checksum failed: " + name)
    print("Verified: all release checksums.")


if __name__ == "__main__":
    main()
