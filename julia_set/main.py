import numpy as np
from matplotlib import pyplot as plt, cm as cm


def calculate_julia(imsize, start, end: int) -> np.array:
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


def concatenate_rows(rows_top, rows_bottom: np.array) -> np.array:
    return np.concatenate((rows_top, rows_bottom), axis=1)


def save_figure(name, im_height, im_width, imsize, arr):
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
