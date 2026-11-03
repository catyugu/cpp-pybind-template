# Bundled OpenMP runtimes

The project code is MIT licensed. Binary distributions also contain one OpenMP
runtime, under its own license:

* Linux: GCC libgomp, GPLv3 with the GCC Runtime Library Exception 3.1. Full
  texts are in GCC-COPYING3.txt and GCC-RUNTIME-EXCEPTION.txt. Upstream:
  https://gcc.gnu.org/git/?p=gcc.git;a=tree;f=libgomp
* macOS: LLVM libomp, Apache-2.0 with LLVM exceptions, plus the notices in
  LLVM-OpenMP-LICENSE.txt. Upstream: https://github.com/llvm/llvm-project/tree/main/openmp
* Windows: Microsoft vcomp140.dll, copied unmodified from the Visual Studio
  redistributable OpenMP directory. This component is proprietary Microsoft
  Distributable Code, governed by the Visual Studio license and redistribution
  terms: https://visualstudio.microsoft.com/license-terms/ and
  https://learn.microsoft.com/visualstudio/releases/2022/redistribution

The wheel repair tools copy these dependencies and preserve their dependency
relationships. Platform C libraries and the C++ standard library are not
replaced by this project. The C++ SDK is specific to the named platform,
architecture and compiler ABI; it is not a cross-toolchain binary interface.
