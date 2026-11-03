# AppleClang needs both a preprocessing flag and the external libomp headers.
# The build owner supplies OpenMP_ROOT (e.g. brew --prefix libomp).
if(APPLE AND CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang")
    find_path(OpenMP_CXX_INCLUDE_DIR omp.h HINTS "${OpenMP_ROOT}/include" "$ENV{OpenMP_ROOT}/include")
    find_library(OpenMP_omp_LIBRARY omp HINTS "${OpenMP_ROOT}/lib" "$ENV{OpenMP_ROOT}/lib")
    set(OpenMP_CXX_FLAGS "-Xclang -fopenmp")
    set(OpenMP_CXX_LIB_NAMES omp)
endif()
