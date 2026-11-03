#pragma once
#include <cstddef>
#include <myproject/export.hpp>
namespace myproject {
// Row-major arrays; output has rows * centers elements. Buffers must not
// overlap. threads=0 uses the OpenMP environment's thread policy.
MYPROJECT_API void pairwise_squared_distances(
    const double* samples, std::size_t rows, const double* centroids,
    std::size_t centers, std::size_t features, double* output, int threads = 0);
MYPROJECT_API int max_threads() noexcept;
MYPROJECT_API int parallel_threads(int threads = 0);
} // namespace myproject
