#include <myproject/distances.hpp>
#include <omp.h>
#include <limits>
#include <stdexcept>
namespace myproject {
namespace {
void check_threads(int threads) {
    if (threads < 0) throw std::invalid_argument("threads must be nonnegative");
}
void check_size(std::size_t a, std::size_t b) {
    if (b && a > static_cast<std::size_t>(std::numeric_limits<std::ptrdiff_t>::max()) / b)
        throw std::overflow_error("array size exceeds ptrdiff_t range");
}
} // namespace
int max_threads() noexcept { return omp_get_max_threads(); }
int parallel_threads(int threads) {
    check_threads(threads);
    int observed = 1;
    const int requested = threads ? threads : max_threads();
#pragma omp parallel num_threads(requested) reduction(max:observed)
    { observed = omp_get_num_threads(); }
    return observed;
}
void pairwise_squared_distances(const double* samples, std::size_t rows,
    const double* centroids, std::size_t centers, std::size_t features,
    double* output, int threads) {
    check_threads(threads);
    check_size(rows, features);
    check_size(centers, features);
    check_size(rows, centers);
    if (!rows || !centers) return;
    if (!output || (features && (!samples || !centroids)))
        throw std::invalid_argument("nonempty arrays require valid buffers");
    const int requested = threads ? threads : max_threads();
    const auto count = static_cast<std::ptrdiff_t>(rows);
#pragma omp parallel for schedule(static) num_threads(requested)
    for (std::ptrdiff_t i = 0; i < count; ++i) {
        for (std::size_t j = 0; j < centers; ++j) {
            double sum = 0;
            for (std::size_t k = 0; k < features; ++k) {
                const double delta = samples[i * features + k] - centroids[j * features + k];
                sum += delta * delta;
            }
            output[i * centers + j] = sum;
        }
    }
}
} // namespace myproject
