"""Expose platform OpenMP development/runtime paths to SDK and wheel builds."""
import os
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import tarfile
import urllib.request

if sys.platform == "darwin":
    # Homebrew bottles target the runner OS. Build a small standalone runtime
    # so the wheel's deployment target also applies to its dependencies.
    work = Path(os.environ["RUNNER_TEMP"]) / "openmp"
    work.mkdir(exist_ok=True)
    for name, digest in {
        "cmake": "3319203cfd1172bbac50f06fa68e318af84dcb5d65353310c0586354069d6634",
        "openmp": "b21c04ee9cbe56e200c5d83823765a443ee6389bbc3f64154c96e94016e6cee9",
    }.items():
        url = f"https://github.com/llvm/llvm-project/releases/download/llvmorg-20.1.8/{name}-20.1.8.src.tar.xz"
        data = urllib.request.urlopen(url, timeout=120).read()
        if hashlib.sha256(data).hexdigest() != digest:
            raise RuntimeError(f"LLVM {name} archive checksum mismatch")
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:xz") as archive:
            archive.extractall(work, filter="data")
        (work / f"{name}-20.1.8.src").rename(work / name)
    root = str(work / "install")
    subprocess.run(["cmake", "-S", str(work / "openmp"), "-B", str(work / "build"),
                    "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_OSX_DEPLOYMENT_TARGET=11.0",
                    "-DOPENMP_ENABLE_LIBOMPTARGET=OFF", "-DOPENMP_ENABLE_OMPT_TOOLS=OFF",
                    f"-DCMAKE_INSTALL_PREFIX={root}"], check=True)
    subprocess.run(["cmake", "--build", str(work / "build"), "--parallel", "3"], check=True)
    subprocess.run(["cmake", "--install", str(work / "build")], check=True)
    with open(os.environ["GITHUB_ENV"], "a") as f:
        f.write(f"OpenMP_ROOT={root}\nMACOSX_DEPLOYMENT_TARGET=11.0\nCIBW_ENVIRONMENT_MACOS=OpenMP_ROOT={root} MACOSX_DEPLOYMENT_TARGET=11.0\n")
elif sys.platform == "win32":
    root = Path(os.environ["VCToolsRedistDir"])
    dirs = list((root / "x64").glob("Microsoft.VC*.OpenMP"))
    if len(dirs) != 1 or not (dirs[0] / "vcomp140.dll").is_file():
        raise RuntimeError(f"Cannot locate MSVC's redistributable OpenMP runtime: {dirs}")
    with open(os.environ["GITHUB_PATH"], "a") as f:
        f.write(str(dirs[0]) + "\n")
