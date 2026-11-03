"""Expose platform OpenMP development/runtime paths to SDK and wheel builds."""
import os
from pathlib import Path
import subprocess
import sys

if sys.platform == "darwin":
    subprocess.run(["brew", "install", "libomp"], check=True)
    root = subprocess.check_output(["brew", "--prefix", "libomp"], text=True).strip()
    with open(os.environ["GITHUB_ENV"], "a") as f:
        f.write(f"OpenMP_ROOT={root}\nCIBW_ENVIRONMENT_MACOS=OpenMP_ROOT={root} MACOSX_DEPLOYMENT_TARGET=11.0\n")
elif sys.platform == "win32":
    root = Path(os.environ["VCToolsRedistDir"])
    dirs = list((root / "x64").glob("Microsoft.VC*.OpenMP"))
    if len(dirs) != 1 or not (dirs[0] / "vcomp140.dll").is_file():
        raise RuntimeError(f"Cannot locate MSVC's redistributable OpenMP runtime: {dirs}")
    with open(os.environ["GITHUB_PATH"], "a") as f:
        f.write(str(dirs[0]) + "\n")
