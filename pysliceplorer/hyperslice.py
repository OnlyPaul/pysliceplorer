import json
import matplotlib.pyplot as plt
import numpy as np


class Slice2d:
    def __init__(self, plot, dim, x_grid, y_grid):
        self.__plot = plot
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.dim = dim

    def data(self, x, y):
        # check if x or y is more than dim-1 (index out of bound)
        if x > self.dim-1 or y > self.dim-1:
            raise Exception('Trying to get non-exist data. Axis number should not exceed {}'.format(self.dim-1))
        elif x < 0 or y < 0:
            raise Exception('Cannot achieve plot data at negative index')
        return self.__plot[(x, y)]

    def to_json(self):
        json_dict = {
            'x_grid': self.x_grid.tolist(),
            'y_grid': self.y_grid.tolist(),
            'dim': self.dim,
            'entries': {}
        }
        for i in range(0, self.dim):
            json_dict['entries'][i] = {}
            for j in range(0, self.dim):
                json_dict['entries'][i][j] = self.__plot[(i, j)]
        return json.dumps(json_dict)


# hyperslice(function_spec, focus_point), which has function_spec spreading to
# f: function defined from outer program
# mn, mx: min and max range of computation
# dim: number of dimension of the function, f
def hyperslice_core(f, mn, mx, dim: int, fpoint, n_seg: int=100):
    # raising simple exceptions to avoid standard errors
    if mx <= mn:
        raise Exception('Input min exceeds max value. (Error: min >= max)')

    if len(fpoint) < dim:
        raise Exception('Focus point does not contain enough dimensions. (Error: len(fpoint) < dim)')

    if dim < 2:
        raise Exception('Sliceplorer does not support less than 2 dimensions. (Error: dim < 2)')

    if n_seg <= 0:
        raise Exception('Number of linear space must be positive integer.')

    # vectorize the function so that it works with numpy array
    # and generate meshgrid for the slice
    f_vec = np.vectorize(f)
    x = np.linspace(mn, mx, n_seg)
    y = np.linspace(mn, mx, n_seg)
    xx, yy = np.meshgrid(x, y)

    result = {}
    for i in range(0, dim):
        for j in range(0, dim):
            # construct the parameters for each pair of 2 free dimensions
            # e.g. if focus point = c(0, 0, 0), there will be parg = [xx, yy, 0] and so on
            # then, we sample the function based on xx and yy meshgrid, store, and represent as Slice2d object
            parg = []

            for k in range(0, dim):
                if k == i and k != j:
                    parg.append(xx)
                elif k == j and k != i:
                    parg.append(yy)
                elif k == i and k == j:
                    parg.append(xx)
                else:
                    parg.append(fpoint[k])

            v = f_vec(*parg)
            result[(i, j)] = v.tolist()

    return Slice2d(result, dim, xx, yy)


def hyperslice(f, mn, mx, dim, fpoint, n_seg=100, output=None):
    if not output:
        output = "fig.png"

    calc_data = hyperslice_core(f, mn, mx, dim, fpoint, n_seg)

    fig, axs = plt.subplots(dim, dim)

    for i in range(0, dim):
        for j in range(0, dim):
            if i == 0:
                x_string = 'x' + str(j + 1)
                axs[i, j].set(xlabel=x_string)
                axs[i, j].xaxis.set_label_position('top')

            if j == 0:
                y_string = 'x' + str(dim - i)
                axs[i, j].set(ylabel=y_string)

            axs[i, j].pcolormesh(calc_data.x_grid, calc_data.y_grid,
                                 calc_data.data(j, dim - i - 1), cmap='pink')

    fig.tight_layout()
    plt.savefig(output, dpi=200)
