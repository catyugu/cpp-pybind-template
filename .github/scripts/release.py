"""Publish exactly the artifacts tested by this workflow, with SHA256 hashes."""
import hashlib
import argparse
import os
from pathlib import Path
import re
import subprocess
import tomllib
import zipfile

root = Path(__file__).resolve().parents[2]
version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--tag", default=os.environ.get("GITHUB_REF_NAME"))
tag = parser.parse_args().tag
if tag != f"v{version}" or not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
    raise RuntimeError(f"Tag {tag} disagrees with project version {version}")
cmake = (root / "CMakeLists.txt").read_text()
if f"project(myproject VERSION {version} LANGUAGES CXX)" not in cmake:
    raise RuntimeError("CMake and Python versions disagree")
subprocess.run(["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"], check=True)
def revision(ref):
    return subprocess.check_output(["git", "rev-parse", ref], text=True).strip()

if revision(f"{tag}^{{commit}}") != revision("HEAD"):
    raise RuntimeError("Release tag does not point to the tested commit")
assets = sorted((root / "dist").iterdir())
if len(list((root / "dist").glob("*.whl"))) != 25:
    raise RuntimeError("Expected 25 CPython 3.10-3.14 wheels across five platforms")
if len(list((root / "dist").glob("*.zip"))) != 5:
    raise RuntimeError("Expected five SDK archives")
if len(list((root / "dist").glob("*.tar.gz"))) != 1:
    raise RuntimeError("Expected one source distribution")
for asset in assets:
    if asset.suffix == ".whl":
        with zipfile.ZipFile(asset) as z:
            if not any(Path(n).name.lower().startswith(("libgomp", "libomp", "vcomp"))
                       and any(ext in n for ext in (".so", ".dylib", ".dll")) for n in z.namelist()):
                raise RuntimeError(f"Missing OpenMP runtime in {asset.name}")
checksums = root / "dist/SHA256SUMS"
checksums.write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n"
                             for p in assets), encoding="utf-8")
subprocess.run(["gh", "release", "create", tag, "--draft", "--verify-tag", "--title", tag,
                "--generate-notes", *map(str, assets), str(checksums)], check=True)
subprocess.run(["gh", "release", "edit", tag, "--draft=false", "--latest"], check=True)
