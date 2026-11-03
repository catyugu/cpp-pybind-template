"""Build, relocate and consume the exact SDK tree that will be archived."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[2]


def run(*args, **kwargs):
    subprocess.run([str(a) for a in args], check=True, **kwargs)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--platform", required=True)
    p.add_argument("--static", action="store_true")
    p.add_argument("--config", default="Release")
    args = p.parse_args()
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    build = ROOT / "build-sdk"
    prefix = ROOT / "build-stage"
    sdk = ROOT / "build-relocated" / f"myproject-{version}-{args.platform}"
    run("cmake", "-S", ROOT, "-B", build, f"-DCMAKE_BUILD_TYPE={args.config}",
        f"-DBUILD_SHARED_LIBS={'OFF' if args.static else 'ON'}",
        f"-DMYPROJECT_BUNDLE_OPENMP={'OFF' if args.static else 'ON'}",
        "-DMYPROJECT_BUILD_PYTHON=OFF", "-DCMAKE_INSTALL_LIBDIR=lib")
    run("cmake", "--build", build, "--config", args.config, "--parallel", "2")
    run("ctest", "--test-dir", build, "-C", args.config, "--output-on-failure")
    run("cmake", "--install", build, "--config", args.config, "--prefix", prefix)
    sdk.parent.mkdir(exist_ok=True)
    shutil.move(prefix, sdk)
    shutil.copy(ROOT / "README.md", sdk)
    shutil.copytree(ROOT / "examples/cpp", sdk / "example")
    # Prevent accidental use of any build-tree library after relocation.
    build.rename(ROOT / "build-hidden")
    env = os.environ.copy()
    env["OMP_NUM_THREADS"], env["OMP_DYNAMIC"] = "2", "FALSE"
    if os.name == "nt":
        env["PATH"] = str(sdk / "bin") + os.pathsep + env["PATH"]
    consumer = ROOT / "build-consumer"
    run("cmake", "-S", ROOT / ".github/scripts/consumer", "-B", consumer,
        f"-DCMAKE_PREFIX_PATH={sdk}", f"-DCMAKE_BUILD_TYPE={args.config}", env=env)
    run("cmake", "--build", consumer, "--config", args.config, env=env)
    if os.name == "nt" and not args.static:
        exe_dir = consumer / args.config if (consumer / args.config).is_dir() else consumer
        for dll in (sdk / "bin").glob("*.dll"):
            shutil.copy2(dll, exe_dir)
        env["MYPROJECT_CHECK_BUNDLED"] = "1"
    run("ctest", "--test-dir", consumer, "-C", args.config, "--output-on-failure", env=env)
    if not args.static:
        runtimes = [p for p in sdk.rglob("*") if p.name.lower().startswith(("libgomp", "libomp", "vcomp"))]
        if not runtimes:
            raise RuntimeError("SDK has no bundled OpenMP runtime")
        dist = ROOT / "dist"
        dist.mkdir(exist_ok=True)
        shutil.make_archive(str(dist / sdk.name), "zip", sdk.parent, sdk.name)


if __name__ == "__main__":
    main()
