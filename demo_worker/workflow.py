import os
import sys

import numpy as np
from matplotlib import pyplot as plt, cm as cm
from tilebox_processing.cache import GoogleStorageCache
from tilebox_processing.tasks import current_task_id, new_task

from demo_worker.main import concatenate_rows, julia

OUTPUT_CLUSTER = os.getenv("JULIA_OUTPUT_CLUSTER", "default")
COMPUTE_CLUSTER = os.getenv("JULIA_COMPUTE_CLUSTER", "default")

cache = GoogleStorageCache()


def combine_outputs():
    target, task1, task2 = sys.argv[1], sys.argv[2], sys.argv[3]

    print("combining output of previous tasks")
    arr1 = cache.load(task1, "output")
    arr2 = cache.load(task2, "output")

    cache.save(target, concatenate_rows(arr1, arr2), "output")


def save_figure():
    task = sys.argv[1]
    imsize = int(sys.argv[2])
    name = sys.argv[3]
    print(f"saving figure... to {name}")
    arr = cache.load(task, "output")

    im_width, im_height = imsize, imsize

    x_min, x_max = -1.5, 1.5
    x_width = x_max - x_min
    y_min, y_max = -1.5, 1.5
    y_height = y_max - y_min

    # Create the image
    fig, ax = plt.subplots(figsize=(imsize / 100, imsize / 100), dpi=100)
    ax.imshow(arr, interpolation='nearest', cmap=cm.hot)
    # Set the tick labels to the coordinates of z0 in the complex plane
    xtick_labels = np.linspace(x_min, x_max, int(x_width / 0.5))
    ax.set_xticks([(x - x_min) / x_width * im_width for x in xtick_labels])
    ax.set_xticklabels(['{:.1f}'.format(xtick) for xtick in xtick_labels])
    ytick_labels = np.linspace(y_min, y_max, int(y_height / 0.5))
    ax.set_yticks([(y - y_min) / y_height * im_height for y in ytick_labels])
    ax.set_yticklabels(['{:.1f}'.format(ytick) for ytick in ytick_labels])
    plt.savefig(f"{name}")


def calculate_julia():
    """ calculate starts """
    print("started calculation of julia sub-set")
    size, start, end, name = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]

    if size * (end - start) < 500_000:
        arr = julia(size, start, end)
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
