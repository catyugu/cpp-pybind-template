"""Prepare data and summarize in Python; run the hot loop in C++/OpenMP."""
import argparse
from time import perf_counter
import numpy as np
from myproject import nearest_centroids, thread_info

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--samples", type=int, default=100_000)
parser.add_argument("--threads", type=int, default=2)
args = parser.parse_args()
rng = np.random.default_rng(42)
samples, centroids = rng.normal(size=(args.samples, 16)), rng.normal(size=(32, 16))
start = perf_counter()
labels, distances, counts = nearest_centroids(samples, centroids, threads=args.threads)
print(thread_info(threads=args.threads))
print(f"Assigned {len(labels)} samples in {perf_counter() - start:.3f}s")
print(f"Mean squared distance: {distances.mean():.6f}")
print("Samples per center:", counts)
