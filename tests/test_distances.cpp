#include <myproject/distances.hpp>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>
void require(bool condition) {
    if (!condition) throw std::runtime_error("C++ SDK test failed");
}
int main() {
    const double x[]{0, 0, 2, 3, 9, 9}, c[]{0, 0, 10, 10};
    const std::vector<double> expected{0, 200, 13, 113, 162, 2};
    for (int threads : {1, 2}) {
        std::vector<double> output(6);
        myproject::pairwise_squared_distances(x, 3, c, 2, 2, output.data(), threads);
        require(output == expected);
    }
    require(myproject::parallel_threads(2) == 2);
    myproject::pairwise_squared_distances(nullptr, 0, nullptr, 0, 0, nullptr);
    double zero = 1;
    myproject::pairwise_squared_distances(nullptr, 1, nullptr, 1, 0, &zero, 1);
    require(zero == 0);
    bool rejected = false;
    try { myproject::parallel_threads(-1); }
    catch (const std::invalid_argument&) { rejected = true; }
    require(rejected);
    rejected = false;
    try { myproject::pairwise_squared_distances(x,
        std::numeric_limits<std::size_t>::max(), c, 2, 2, &zero); }
    catch (const std::overflow_error&) { rejected = true; }
    require(rejected);
    std::cout << "C++17/OpenMP kernel and input checks passed\n";
}
