#include <myproject/distances.hpp>
#include <iostream>
#include <vector>
int main() {
    const std::vector<double> samples{0, 0, 2, 3, 9, 9}, centers{0, 0, 10, 10};
    std::vector<double> distances(6);
    myproject::pairwise_squared_distances(samples.data(), 3, centers.data(), 2, 2,
        distances.data(), 2);
    for (std::size_t i = 0; i < 3; ++i)
        std::cout << distances[2 * i] << ", " << distances[2 * i + 1] << '\n';
    std::cout << "OpenMP team: " << myproject::parallel_threads(2) << '\n';
}
