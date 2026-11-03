#include <myproject/distances.hpp>
#include <iostream>
int main() {
    const double samples[]{0, 0, 2, 3}, centers[]{0, 0};
    double distances[2]{};
    myproject::pairwise_squared_distances(samples, 2, centers, 1, 2, distances, 2);
    if (distances[0] != 0 || distances[1] != 13 || myproject::parallel_threads(2) != 2)
        return 1;
    std::cout << "Relocated C++17 SDK: correct distances, two OpenMP threads\n";
}
