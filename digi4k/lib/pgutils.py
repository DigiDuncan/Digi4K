import pygame
import numpy as np


def greyscale(surface: pygame.Surface):
    arr = pygame.surfarray.pixels3d(surface)
    mean_arr = np.dot(arr[:, :, :], [0.216, 0.587, 0.144])
    mean_arr3d = mean_arr[..., np.newaxis]
    new_arr = np.repeat(mean_arr3d[:, :, :], 3, axis=2)
    return pygame.surfarray.make_surface(new_arr)
