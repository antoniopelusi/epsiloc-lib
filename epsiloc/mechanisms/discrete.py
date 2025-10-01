import numpy as np

def discrete_laplace(
    x: int,
    epsilon: float,
    min: int,
    max: int,
    rejection_sampling: bool
) -> int:
    if epsilon <= 0:
        raise ValueError("epsilon must be > 0.")

    sensitivity: int = max - min
    alpha: float = np.exp(-epsilon / sensitivity)
    p: float = 1 - alpha

    if rejection_sampling:
        while True:
            g1: int = np.random.geometric(p) - 1
            g2: int = np.random.geometric(p) - 1
            noise: int = g1 - g2
            y: int = x + noise
            if min <= y <= max:
                break
    else:
        g1: int = np.random.geometric(p) - 1
        g2: int = np.random.geometric(p) - 1
        noise: int = g1 - g2
        y: int = x + noise

    return y
