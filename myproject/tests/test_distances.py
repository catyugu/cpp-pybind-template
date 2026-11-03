import os
from pathlib import Path
import subprocess
import sys
import numpy as np
import pytest
import myproject


@pytest.mark.parametrize("threads", [0, 1, 2])
def test_reference(threads):
    rng = np.random.default_rng(1)
    x, c = rng.normal(size=(127, 7)), rng.normal(size=(11, 7))
    reference = ((x[:, None, :] - c[None, :, :]) ** 2).sum(axis=2)
    np.testing.assert_allclose(myproject.squared_distances(x, c, threads=threads), reference,
                               rtol=1e-14, atol=1e-14)


def test_python_orchestration():
    labels, distances, counts = myproject.nearest_centroids([[0, 0], [2, 3], [9, 9]],
                                                          [[0, 0], [10, 10]], threads=2)
    np.testing.assert_array_equal(labels, [0, 0, 1])
    np.testing.assert_array_equal(distances, [0, 13, 2])
    np.testing.assert_array_equal(counts, [2, 1])


def test_layout_and_empty():
    x = np.arange(30, dtype=np.float32).reshape(5, 6)[:, ::2]
    np.testing.assert_allclose(myproject.squared_distances(x, x),
                               ((x[:, None] - x[None, :]) ** 2).sum(axis=2))
    assert myproject.squared_distances(np.empty((0, 3)), np.empty((4, 3))).shape == (0, 4)
    np.testing.assert_array_equal(myproject.squared_distances(np.empty((2, 0)),
                                                             np.empty((3, 0))), np.zeros((2, 3)))
    assert myproject.squared_distances([[1]], np.empty((0, 1))).shape == (1, 0)


@pytest.mark.parametrize("x,c", [([1], [[1]]), ([[1]], [[1, 2]])])
def test_invalid_shape(x, c):
    with pytest.raises(ValueError):
        myproject.squared_distances(x, c)


def test_invalid_threads_and_centers():
    with pytest.raises(ValueError):
        myproject.squared_distances([[1]], [[2]], threads=-1)
    with pytest.raises(TypeError):
        myproject.squared_distances([[1]], [[2]], threads=1.5)
    with pytest.raises(ValueError):
        myproject.nearest_centroids([[1]], np.empty((0, 1)))


def test_actual_openmp_team():
    assert myproject.thread_info(threads=2)["parallel_threads"] == 2


def test_import_order():
    for imports in ["import numpy; import myproject", "import myproject; import numpy"]:
        subprocess.run([sys.executable, "-c", imports +
                        "; assert myproject.thread_info(threads=2)['parallel_threads'] == 2"],
                       check=True, cwd=Path(sys.executable).parent)


@pytest.mark.skipif(not os.environ.get("MYPROJECT_TEST_BUNDLED"), reason="repaired-wheel check")
def test_runtime_is_in_distribution():
    root = Path(myproject.__file__).parent.parent
    candidates = [Path(myproject.__file__).parent, root / "cpp_pybind_template.libs"]
    runtimes = [p for directory in candidates for p in directory.rglob("*") if p.is_file() and
                p.name.lower().startswith(("libgomp", "libomp", "vcomp")) and
                any(ext in p.name for ext in (".so", ".dylib", ".dll"))]
    assert runtimes, "repaired wheel is missing its OpenMP runtime"
