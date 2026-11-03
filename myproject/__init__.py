"""Python orchestration around C++17/OpenMP kernels."""
from importlib.metadata import version
import operator
import numpy as np
from . import _core

__version__ = version("cpp-pybind-template")
__all__ = ["squared_distances", "nearest_centroids", "thread_info", "__version__"]


def squared_distances(samples, centroids, *, threads=0):
    """Return squared Euclidean distances, shape (n_samples, n_centroids).

    Inputs become C-contiguous float64 matrices. C++ releases the GIL and
    distributes sample rows over OpenMP threads. Do not mutate input arrays
    during the call. threads=0 respects the OpenMP environment.
    """
    threads = operator.index(threads)
    if threads < 0:
        raise ValueError("threads must be nonnegative")
    x, c = np.asarray(samples, dtype=np.float64), np.asarray(centroids, dtype=np.float64)
    if x.ndim != 2 or c.ndim != 2:
        raise ValueError("samples and centroids must be two-dimensional")
    if x.shape[1] != c.shape[1]:
        raise ValueError("samples and centroids must have the same feature count")
    return _core.squared_distances(np.ascontiguousarray(x), np.ascontiguousarray(c), threads)


def nearest_centroids(samples, centroids, *, threads=0):
    """Return labels, squared distances to assigned centers, and center counts.

    Python handles selection and counting. Ties select the first center.
    """
    distances = squared_distances(samples, centroids, threads=threads)
    if distances.shape[1] == 0:
        raise ValueError("nearest_centroids requires at least one centroid")
    labels = distances.argmin(axis=1)
    return (labels, distances[np.arange(len(labels)), labels],
            np.bincount(labels, minlength=distances.shape[1]))


def thread_info(*, threads=0):
    """Report the configured maximum and an observed OpenMP team's size."""
    return {"max_threads": _core.max_threads(),
            "parallel_threads": _core.parallel_threads(operator.index(threads))}
