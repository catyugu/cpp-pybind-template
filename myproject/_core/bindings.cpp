#include <myproject/distances.hpp>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
namespace py = pybind11;
using Matrix = py::array_t<double, py::array::c_style>;
PYBIND11_MODULE(_core, m) {
    m.doc() = "C++17/OpenMP numerical kernels (private extension)";
    m.def("squared_distances", [](const Matrix& x, const Matrix& c, int threads) {
        if (x.ndim() != 2 || c.ndim() != 2 || x.shape(1) != c.shape(1))
            throw py::value_error("expected matrices with the same feature count");
        py::array_t<double> result({x.shape(0), c.shape(0)});
        const double* samples = x.data();
        const double* centers = c.data();
        double* output = result.mutable_data();
        const auto rows = x.shape(0), count = c.shape(0), features = x.shape(1);
        {
            py::gil_scoped_release release;
            myproject::pairwise_squared_distances(samples, rows, centers,
                count, features, output, threads);
        }
        return result;
    }, py::arg("samples").noconvert(), py::arg("centroids").noconvert(), py::arg("threads") = 0);
    m.def("max_threads", &myproject::max_threads);
    m.def("parallel_threads", &myproject::parallel_threads, py::arg("threads") = 0,
        py::call_guard<py::gil_scoped_release>());
}
