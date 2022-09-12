import os
import sys

from tilebox_processing.cache import GoogleStorageCache, LocalCache
from tilebox_processing.tasks import current_task_id, new_task

from julia_set.main import concatenate_rows, calculate_julia, save_figure

OUTPUT_CLUSTER = os.getenv("JULIA_OUTPUT_CLUSTER", "default")
COMPUTE_CLUSTER = os.getenv("JULIA_COMPUTE_CLUSTER", "default")

if os.getenv("TILEBOX_CACHE_DIRECTORY"):
    cache = LocalCache()
else:
    cache = GoogleStorageCache()


def calculate_julia_task():
    """ calculate starts """
    print("started calculation of julia sub-set")
    size, start, end, name = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]

    if size * (end - start) < 500_000:
        arr = calculate_julia(size, start, end)
        cache.save(current_task_id(), arr, "output")
        if size == end - start:
            new_task("save-figure", current_task_id(), size, name, cluster=OUTPUT_CLUSTER)
    else:
        mid = int(start + (end - start) / 2)
        task1 = new_task("calculate-julia", size, start, mid, name, cluster=COMPUTE_CLUSTER)
        task2 = new_task("calculate-julia", size, mid, end, name, cluster=COMPUTE_CLUSTER)
        task3 = new_task("combine-outputs", current_task_id(), task1, task2, dependencies=[task1, task2],
                         cluster=COMPUTE_CLUSTER)
        if size == end - start:  # final task
            print("saving figure")
            new_task("save-figure", current_task_id(), size, name, dependencies=[task3], cluster=OUTPUT_CLUSTER)


def combine_outputs_task():
    target, task1, task2 = sys.argv[1], sys.argv[2], sys.argv[3]

    print("combining output of previous tasks")
    arr1 = cache.load(task1, "output")
    arr2 = cache.load(task2, "output")

    cache.save(target, concatenate_rows(arr1, arr2), "output")


def save_figure_task():
    task = sys.argv[1]
    imsize = int(sys.argv[2])
    name = sys.argv[3]
    print(f"saving figure... to {name}")
    arr = cache.load(task, "output")

    save_figure(name, imsize, imsize, imsize, arr)
