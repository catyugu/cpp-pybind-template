# C++ / Python template

A C++17 numerical library, a pybind11 extension, and a Python package built from
one source tree. OpenMP is required and exercised by the example and tests.

The example assigns points to their nearest centroid. C++ calculates squared
distances in an OpenMP parallel loop; Python prepares arrays, chooses centers,
and summarizes assignments. The extension releases the GIL during computation.

## Install and run

Clone this template, install the build prerequisites below, then run:

```sh
python -m pip install .
python examples/python/assign_points.py --samples 100000 --threads 2
```

```python
from myproject import nearest_centroids, thread_info
labels, distances, counts = nearest_centroids(
    [[0, 0], [2, 3], [9, 9]], [[0, 0], [10, 10]], threads=2)
print(labels)      # [0 0 1]
print(counts)      # [2 1]
print(thread_info(threads=2))  # observed parallel_threads: 2
```

CI verifies that repaired wheels carry their OpenMP runtime and can be installed
and consumed from an isolated environment. NumPy is a package dependency. `threads=0`
uses the OpenMP environment, including `OMP_NUM_THREADS`; positive values choose
a team size for that call without changing global runtime settings. Set
`OMP_DYNAMIC=FALSE` when requiring an exact team size. Avoid mutating input
arrays concurrently with a kernel call. Output storage is O(samples × centers).

## Build from source

Requirements: Python 3.10+, a C++17 compiler, CMake 3.26+, and OpenMP development
files. Pip installs the isolated build dependencies (scikit-build-core and
pybind11). The C++-only build does not need Python, pybind11 or NumPy.

* Linux/GCC: install the compiler and its OpenMP development/runtime package.
* Windows: use an x64 Visual Studio 2022 Developer shell with C++ tools.
* macOS/AppleClang: `brew install libomp`, then set `OpenMP_ROOT` to the result
  of `brew --prefix libomp` before configuring or invoking pip.

```sh
python -m pip install -e '.[test]'
python -m pytest --pyargs myproject.tests
python examples/python/assign_points.py --threads 2
```

The local editable build links your development machine's OpenMP runtime.
Redistributable wheels are built, repaired and consumed within CI. Linux wheel
containers run only in GitHub Actions; local builds do not require Docker.

## C++ SDK

```sh
cmake -S . -B build -DBUILD_SHARED_LIBS=ON
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
cmake --install build --config Release --prefix install
```

`examples/cpp/main.cpp` uses the same kernel directly from C++17. A downstream
project consumes the installed SDK:

```cmake
find_package(myproject 0.1 CONFIG REQUIRED)
add_executable(app main.cpp)
target_link_libraries(app PRIVATE myproject::myproject)
```

Configure the consumer with `-DCMAKE_PREFIX_PATH=/path/to/install`.
The installed SDK contains headers, the C++ library, CMake package files and
licenses. Enable runtime bundling as described below to include OpenMP.
On Windows, put the SDK `bin` directory on PATH
or deploy its DLLs next to the application. Linux and macOS libraries resolve
the bundled OpenMP runtime relative to themselves. C++ SDK binaries require a
compatible compiler ABI and platform C/C++ runtime. CI builds Linux SDKs on Ubuntu 24.04
(glibc 2.39); portable Python wheels use manylinux_2_28 instead.

`-DMYPROJECT_BUNDLE_OPENMP=ON` bundles the shared SDK's runtime during install.
The default local install leaves runtime provisioning to the developer.
`-DBUILD_SHARED_LIBS=OFF` builds a static library; its exported CMake package
finds OpenMP in the consumer's toolchain. Static libraries retain the required
OpenMP link dependency. `add_subdirectory` exposes the same target, with tests
and examples disabled by default when used as a subproject.

## Layout

| Path | Responsibility |
| --- | --- |
| `include/myproject/` | Public C++17 API and symbol exports |
| `src/` | Python-independent C++/OpenMP kernels |
| `myproject/_core/bindings.cpp` | Private pybind11 extension, array boundary and GIL |
| `myproject/__init__.py` | Public Python API and orchestration |
| `myproject/tests/` | Numerical reference, edge cases and runtime tests |
| `tests/` | C++ kernel tests |
| `examples/cpp/`, `examples/python/` | Runnable usage in both languages |
| `cmake/` | Installed SDK configuration and runtime deployment |
| `.github/` | Build, relocation, wheel repair and release verification |

The package/private-core/test arrangement follows NumPy's separation of the
public Python API from compiled numerical code. This project uses CMake and
scikit-build-core so the standalone C++ SDK and Python extension share targets.

## CI and tag releases

Every main push and pull request verifies the template's build and export paths:

| Platform | SDK | CPython wheels |
| --- | --- | --- |
| Linux x86_64 | GCC / Ubuntu 24.04 | 3.10–3.14 / manylinux_2_28 |
| Linux aarch64 | GCC / Ubuntu 24.04 | 3.10–3.14 / manylinux_2_28 |
| Windows x64 | MSVC / VS 2022 | 3.10–3.14 |
| macOS x86_64 | AppleClang | 3.10–3.14 / macOS 11+ |
| macOS arm64 | AppleClang | 3.10–3.14 / macOS 11+ |

Linux uses auditwheel, macOS uses delocate, Windows uses delvewheel. Each repaired
wheel is installed and tested, including an actual two-thread OpenMP team and
both NumPy import orders. SDK tests relocate the installation, hide the original
build tree, compile an independent `find_package` consumer and run it. Separate
Debug jobs check static package exports with the minimum supported CMake.
The source distribution is unpacked, built, installed and tested separately.

To release, update the versions in `CMakeLists.txt` and `pyproject.toml`, wait
for main CI to pass, then push the matching `vX.Y.Z` tag on a main commit. The
tag pipeline repeats verification, checks version consistency and main ancestry,
and publishes version notes to GitHub Releases after every build/test job succeeds.
This template does not upload wheels, SDKs or source distributions as CI or
Release assets, and does not publish to PyPI. Build outputs stay within the CI
jobs that test them. GitHub supplies its usual source-code downloads for tags.
The GitHub Actions token needs repository contents write permission only in the
release-notes job. Projects created from the template can add artifact publishing
when they have useful binaries to distribute.

## Reuse this template

Create your repository with GitHub's **Use this template**. Rename `myproject`
consistently using:

```sh
python script/init_project.py --name pointcloud --distribution pointcloud-tools
```

This updates CMake targets, C++ namespaces, headers, the Python package,
distribution metadata, examples and tests. Review the README repository URL
and project metadata afterwards. CI also builds and tests a renamed template.
Add kernels to `src/` and their bindings to `myproject/_core/`; keep Python
orchestration in the package. Keep OpenMP runtime repair and installed-consumer
tests when replacing the example with your own parallel code.

Project code: MIT. Bundled runtime terms and full open-source license texts are
in `THIRD_PARTY_NOTICES.md` and accompany exported SDKs and wheels.
