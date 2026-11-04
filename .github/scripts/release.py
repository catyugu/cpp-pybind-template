"""Publish template release notes after CI has verified build and export paths."""
import os
from pathlib import Path
import re
import subprocess
import tomllib

root = Path(__file__).resolve().parents[2]
version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
create_tag = os.environ["GITHUB_REF"] == "refs/heads/main"
tag = f"v{version}" if create_tag else os.environ["GITHUB_REF_NAME"]
if tag != f"v{version}" or not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
    raise RuntimeError(f"Tag {tag} disagrees with project version {version}")
cmake = (root / "CMakeLists.txt").read_text()
if f"project(myproject VERSION {version} LANGUAGES CXX)" not in cmake:
    raise RuntimeError("CMake and Python versions disagree")
subprocess.run(["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"], check=True)
def revision(ref):
    return subprocess.check_output(["git", "rev-parse", ref], text=True).strip()

if create_tag:
    subject = subprocess.check_output(["git", "log", "-1", "--format=%s"], text=True).strip()
    if subject != f"Release {tag}":
        raise RuntimeError("Release commit subject disagrees with project version")
    subprocess.run(["git", "tag", tag], check=True)
    subprocess.run(["git", "push", "origin", f"refs/tags/{tag}"], check=True)

if revision(f"{tag}^{{commit}}") != revision("HEAD"):
    raise RuntimeError("Release tag does not point to the tested commit")
subprocess.run(["gh", "release", "create", tag, "--verify-tag", "--title", tag,
                "--generate-notes"], check=True)
