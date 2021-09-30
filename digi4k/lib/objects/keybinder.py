from pygame.constants import K_d, K_f, K_j, K_k


class KeyBinder:
    def __init__(self):
        self.left = K_d
        self.down = K_f
        self.up = K_j
        self.right = K_k

    def key_to_bind(self, key):
        for k, v in vars(self):
            if key == v:
                return k
        return None
