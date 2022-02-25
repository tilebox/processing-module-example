import os
import subprocess
import sys
from typing import List, Optional

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np


def env():
    print(os.environ)


def calculate_julia():
    """ calculate starts """
    print("started calculation of julia sub-set")
    size, start, end = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])

    if size * (end - start) < 500_000:
        arr = julia(size, start, end)
        np.save("output.npy", arr)
    else:
        mid = int(start + (end - start) / 2)
        task1 = new_task("calculate-julia", size, start, mid)
        task2 = new_task("calculate-julia", size, mid, end)
        task3 = new_task("combine-outputs", task1, task2, data_dependencies=[task1, task2])
        if size == end - start:  # final task
            new_task("save-figure", task3, size, data_dependencies=[task3])


def concatenate_rows(rows_top, rows_bottom: np.array) -> np.array:
    return np.concatenate((rows_top, rows_bottom), axis=1)


def save_figure():
    task = sys.argv[1]
    imsize = int(sys.argv[2])
    arr = np.load(f"../{task}/output.npy")

    im_width, im_height = imsize, imsize

    x_min, x_max = -1.5, 1.5
    x_width = x_max - x_min
    y_min, y_max = -1.5, 1.5
    y_height = y_max - y_min

    # Create the image
    fig, ax = plt.subplots(figsize=(20, 20))
    ax.imshow(arr, interpolation='nearest', cmap=cm.hot)
    # Set the tick labels to the coordinates of z0 in the complex plane
    xtick_labels = np.linspace(x_min, x_max, int(x_width / 0.5))
    ax.set_xticks([(x - x_min) / x_width * im_width for x in xtick_labels])
    ax.set_xticklabels(['{:.1f}'.format(xtick) for xtick in xtick_labels])
    ytick_labels = np.linspace(y_min, y_max, int(y_height / 0.5))
    ax.set_yticks([(y - y_min) / y_height * im_height for y in ytick_labels])
    ax.set_yticklabels(['{:.1f}'.format(ytick) for ytick in ytick_labels])
    filename = f"../julia-{im_width}x{im_height}.png"  # TODO update
    plt.savefig(filename)

    # Upload the image
    # client = storage.Client()
    # bucket_name = "demo-worker-output"  # TODO update
    # bucket = client.bucket(bucket_name)
    # blob = bucket.blob(filename)
    # blob.upload_from_filename(filename)
    # print(f"file uploaded to {bucket_name}/{filename}")


def combine_outputs() -> np.array:
    task1, task2 = sys.argv[1], sys.argv[2]

    arr1 = np.load(f"../{task1}/output.npy")
    arr2 = np.load(f"../{task2}/output.npy")

    np.save("output.npy", concatenate_rows(arr1, arr2))


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
            shade = 1 - np.sqrt(nit / nit_max)
            ratio = nit / nit_max
            arr[ix, iy - start] = ratio
    return arr


def new_task(command: str, *args, logical_dependencies: Optional[List[str]] = None,
             data_dependencies: Optional[List[str]] = None) -> str:
    """new_task dispatches a new task and returns the task identifier as a string"""

    cmd = ["adler-x-task", "create-task"]
    if logical_dependencies is not None:
        cmd.append("--logically-depends-on")
        cmd.append(",".join(logical_dependencies))
    if data_dependencies is not None:
        cmd.append("--depends-on-data-from")
        cmd.append(",".join(data_dependencies))

    cmd.append("--")
    cmd.append(command)
    for arg in args:
        cmd.append(str(arg))

    identifier = subprocess.check_output(cmd).decode('UTF-8').strip()
    print("submitted command: ", cmd, "\nreceived task id: ", identifier)
    return identifier
