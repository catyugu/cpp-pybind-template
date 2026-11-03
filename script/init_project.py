"""Rename the C++ namespace/CMake package/Python package and distribution."""
import argparse
import fnmatch
import keyword
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--name", required=True, help="C++ and Python identifier, e.g. pointcloud")
parser.add_argument("--distribution", required=True, help="pip distribution name, e.g. pointcloud-tools")
args = parser.parse_args()
cpp_keywords = {"alignas", "alignof", "asm", "auto", "bool", "break", "case", "catch",
                "char", "class", "const", "constexpr", "continue", "decltype", "default",
                "delete", "do", "double", "else", "enum", "explicit", "export", "extern",
                "false", "float", "for", "friend", "goto", "if", "inline", "int", "long",
                "mutable", "namespace", "new", "noexcept", "nullptr", "operator", "private",
                "protected", "public", "register", "return", "short", "signed", "sizeof",
                "static", "struct", "switch", "template", "this", "thread_local", "throw",
                "true", "try", "typedef", "typeid", "typename", "union", "unsigned",
                "using", "virtual", "void", "volatile", "while"}
if (not re.fullmatch(r"[a-z][a-z0-9_]*", args.name) or keyword.iskeyword(args.name)
        or args.name in cpp_keywords or args.name == "myproject"):
    parser.error("--name must be a fresh lowercase C++/Python identifier")
if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.distribution):
    parser.error("--distribution must contain lowercase letters, digits and single hyphens")
if not (root / "myproject").is_dir():
    parser.error("template is already initialized")
skip = (".git", ".cache", ".venv", "build", "build-*", "dist", "wheelhouse",
        "unpacked", "__pycache__", ".pytest_cache", "script", "*.egg-info")
paths = [p for p in root.rglob("*") if not any(
    fnmatch.fnmatchcase(part, pattern) for part in p.relative_to(root).parts for pattern in skip)]
replacements = {"cpp-pybind-template": args.distribution,
                "cpp_pybind_template": args.distribution.replace("-", "_"),
                "MYPROJECT": args.name.upper(), "myproject": args.name}
changes = []
for path in paths:
    target = path.with_name(path.name.replace("myproject", args.name))
    if target != path and target.exists():
        parser.error(f"destination already exists: {target}")
    if path.is_file():
        data = path.read_bytes()
        if b"\0" in data:
            continue
        text = data.decode("utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        if text != data.decode("utf-8"):
            changes.append((path, text))
for path, text in changes:
    path.write_text(text, encoding="utf-8")
for path in sorted(paths, key=lambda p: len(p.parts), reverse=True):
    if "myproject" in path.name:
        path.rename(path.with_name(path.name.replace("myproject", args.name)))
print(f"Initialized {args.name} ({args.distribution}); updated {len(changes)} files")
