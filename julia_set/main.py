import numpy as np


def concatenate_rows(rows_top, rows_bottom: np.array) -> np.array:
    return np.concatenate((rows_top, rows_bottom), axis=1)


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
