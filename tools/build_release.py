#!/usr/bin/env python3
"""Build reproducible v0.2.0 standalone skill ZIPs and manual-install suite."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.2.0"


def files(path):
    return sorted(p for p in path.rglob("*") if p.is_file()
                  and not any(part.startswith(".") or part == "__pycache__" for part in p.relative_to(path).parts)
                  and p.suffix != ".pyc")


def archive(path, entries):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name, content in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 9, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            output.writestr(info, content)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_license_file(path):
    return path.stem.upper() in {"LICENSE", "LICENCE"}


def main():
    dist = ROOT / "dist"
    upload = dist / "upload"
    upload.mkdir(parents=True, exist_ok=True)
    packages = []
    for skill in sorted((ROOT / "skills").iterdir()):
        if not (skill / "SKILL.md").is_file():
            continue
        published = "dsh-" + skill.name
        ready = dist / "skillhub-ready" / published
        ready.mkdir(parents=True, exist_ok=True)
        for existing in ready.rglob("*"):
            if existing.is_file() and is_license_file(existing):
                existing.unlink()
        entries = []
        for source in files(skill):
            if is_license_file(source):
                continue
            relative = source.relative_to(skill).as_posix()
            content = source.read_bytes()
            if relative == "SKILL.md":
                text = content.decode("utf-8")
                text = text.replace("name: " + skill.name + "\n", "name: " + published + "\n", 1)
                text = text.replace('  slug: "' + skill.name + '"', '  slug: "' + published + '"', 1)
                text = text.replace("\nmetadata:\n", "\nlicense: Apache-2.0\nmetadata:\n", 1)
                content = text.encode("utf-8")
            target = ready / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            entries.append((relative, content))
        path = upload / f"{published}-v{VERSION}.zip"
        archive(path, entries)
        packages.append({"skill": published, "version": VERSION, "file": path.name,
                         "sha256": digest(path), "files": len(entries)})
    manifest = {"version": VERSION, "date": "2026-11-09", "packages": packages,
                "import_note": "Each listed ZIP is one skill. The combined ZIP is a transport bundle, not one importable skill."}
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (upload / f"packages-v{VERSION}.json").write_bytes(manifest_bytes)
    bundle = dist / f"admin-expert-kit-skillhub-ready-v{VERSION}.zip"
    archive(bundle, [("packages.json", manifest_bytes)] + [(p["file"], (upload / p["file"]).read_bytes()) for p in packages])
    for source, target in [("MANIFEST.md", "MANIFEST.md"), ("INSTALL-AND-DEMO.md", "INSTALL.md")]:
        content = (ROOT / source).read_text(encoding="utf-8")
        if target == "MANIFEST.md":
            for original, replacement in [("INSTALL-AND-DEMO.md", "INSTALL.md"),
                                          ("BENCHMARK.md", "../BENCHMARK.md"),
                                          ("SELFTEST.md", "../SELFTEST.md"),
                                          ("dist/README.md", "README.md")]:
                content = content.replace("(" + original + ")", "(" + replacement + ")")
        (dist / target).write_text(content, encoding="utf-8", newline="\n")
    entries = []
    for name in ("README.md", "LICENSE", "MANIFEST.md", "INSTALL-AND-DEMO.md", "BENCHMARK.md", "SELFTEST.md"):
        entries.append((name, (ROOT / name).read_bytes()))
    for directory in ("skills", "docs", "tests", "tools"):
        entries.extend((p.relative_to(ROOT).as_posix(), p.read_bytes()) for p in files(ROOT / directory))
    for name in ("README.md", "INSTALL.md", "MANIFEST.md"):
        entries.append(("dist/" + name, (dist / name).read_bytes()))
    entries.extend(("dist/upload/" + p["file"], (upload / p["file"]).read_bytes()) for p in packages)
    entries.append((f"dist/upload/packages-v{VERSION}.json", manifest_bytes))
    manual = dist / f"admin-expert-kit-v{VERSION}-MANUAL-ONLY.zip"
    archive(manual, entries)
    artifacts = [upload / p["file"] for p in packages] + [bundle, manual]
    (dist / f"SHA256SUMS-v{VERSION}.txt").write_text(
        "".join(f"{digest(p)}  {p.relative_to(dist).as_posix()}\n" for p in artifacts), encoding="utf-8", newline="\n")
    print(f"Built {len(packages)} standalone packages, one transport bundle and one manual suite.")


if __name__ == "__main__":
    main()
