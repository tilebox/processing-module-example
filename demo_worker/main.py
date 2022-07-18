import sys

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from tilebox_processing.cache import LocalCache
from tilebox_processing.tasks import new_task, current_task_id

cache = LocalCache()


def calculate_julia():
    """ calculate starts """
    print("started calculation of julia sub-set")
    size, start, end, name = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]

    if size * (end - start) < 500_000:
        arr = julia(size, start, end)
        cache.save(current_task_id(), arr, "output")
        if size == end - start:
            new_task("save-figure", current_task_id(), size, name)
    else:
        mid = int(start + (end - start) / 2)
        task1 = new_task("calculate-julia", size, start, mid, name)
        task2 = new_task("calculate-julia", size, mid, end, name)
        task3 = new_task("combine-outputs", current_task_id(), task1, task2, dependencies=[task1, task2])
        if size == end - start:  # final task
            print("saving figure")
            new_task("save-figure", current_task_id(), size, name, dependencies=[task3])


def concatenate_rows(rows_top, rows_bottom: np.array) -> np.array:
    return np.concatenate((rows_top, rows_bottom), axis=1)


def save_figure():
    task = sys.argv[1]
    imsize = int(sys.argv[2])
    name = sys.argv[3]
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


def combine_outputs():
    target, task1, task2 = sys.argv[1], sys.argv[2], sys.argv[3]

    print("combining output of previous tasks")
    arr1 = cache.load(task1, "output")
    arr2 = cache.load(task2, "output")

    cache.save(target, concatenate_rows(arr1, arr2), "output")


def julia(imsize, start, end: int) -> np.array:
    # Image width and height; parameters for the plot
    im_width, im_height = imsize, end - start

    c = complex(-0.1, 0.65)
    z_abs_max = 10
    nit_max = 1000
    x_min, x_max = -1.5, 1.5
    x_width = x_max - x_min
    y_min, y_max = -1.5, 1.5
    y_min_subset = -1.5 + (y_max - y_min) * (start / imsize)
    y_max_subset = -1.5 + (y_max - y_min) * (end / imsize)
    y_height = y_max_subset - y_min_subset

    arr = np.zeros((im_width, im_height))
    for ix in range(im_width):
        for iy in range(start, end):
            nit = 0
            # Map pixel position to a point in the complex plane
            z = complex(ix / im_width * x_width + x_min,
                        iy / im_height * y_height + y_min)
            # Do the iterations
            while abs(z) <= z_abs_max and nit < nit_max:
                z = z ** 2 + c
                nit += 1
            ratio = nit / nit_max
            arr[ix, iy - start] = ratio
    return arr
