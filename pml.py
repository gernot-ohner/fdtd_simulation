import numpy as np
import math



def pml(size, eps, mu, thickness=10):
    """Creates matrices for the electric (sigma_x, sigma_y) and magnetic (sigma_mx, sigma_my) conductivities on
    at the border of the computational domain. Computes the values for these matrices at a given position.
    Returns these matrices.
    :type thickness: int"""
    sizeX, sizeY = size
    m = 3
    R0 = 1e-5
    sigma_x = np.zeros((self.nx, self.ny))
    sigma_y = np.zeros((self.nx, self.ny))
    sigmamax = -math.log(R0) * (m + 1) / (np.sqrt(mu / eps) * 2 * thickness * self.ds) / self.p
    for n in range(thickness):
        sigma_x[n, :] = ((thickness - n) / thickness) ** m * sigmamax[n, :]
        sigma_x[-n - 1, :] = ((thickness - n) / thickness) ** m * sigmamax[-n - 1, :]

        sigma_mx[n, :] = ((thickness - n + 0.5) / thickness) ** m * sigmamax[n, :]
        sigma_mx[-n - 1, :] = ((thickness - n - 0.5) / thickness) ** m * sigmamax[-n - 1, :]

        sigma_y[:, n] = ((thickness - n) / thickness) ** m * sigmamax[:, n]
        sigma_y[:, -n - 1] = ((thickness - n) / thickness) ** m * sigmamax[:, -n - 1]

        sigma_my[:, n] = ((thickness - n + 0.5) / thickness) ** m * sigmamax[:, n]
        sigma_my[:, -n - 1] = ((thickness - n - 0.5) / thickness) ** m * sigmamax[:, -n - 1]
    return sigma_x, sigma_y, sigma_y * mu / eps, sigma_x * mu / eps