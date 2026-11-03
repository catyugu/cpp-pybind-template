#include <myproject/distances.hpp>
#include <iostream>
#ifdef _WIN32
#define NOMINMAX
#include <windows.h>
#include <cstdlib>
#include <filesystem>
#endif
int main() {
    const double samples[]{0, 0, 2, 3}, centers[]{0, 0};
    double distances[2]{};
    myproject::pairwise_squared_distances(samples, 2, centers, 1, 2, distances, 2);
    if (distances[0] != 0 || distances[1] != 13 || myproject::parallel_threads(2) != 2)
        return 1;
#ifdef _WIN32
    if (std::getenv("MYPROJECT_CHECK_BUNDLED")) {
        wchar_t runtime[MAX_PATH]{}, executable[MAX_PATH]{};
        const auto module = GetModuleHandleW(L"vcomp140.dll");
        if (!module || !GetModuleFileNameW(module, runtime, MAX_PATH)
            || !GetModuleFileNameW(nullptr, executable, MAX_PATH)
            || std::filesystem::path(runtime).parent_path()
                != std::filesystem::path(executable).parent_path()) return 2;
    }
#endif
    std::cout << "Relocated C++17 SDK: correct distances, two OpenMP threads\n";
}
