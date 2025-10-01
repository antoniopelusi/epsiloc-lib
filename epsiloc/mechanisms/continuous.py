import numpy as np

def laplace(
    x: float,
    epsilon: float,
    min: float,
    max: float,
    rejection_sampling: bool,
    decimal_places: int
) -> float:
    if epsilon <= 0:
        raise ValueError("epsilon must be > 0.")

    sensitivity: float = max - min
    scale: float = sensitivity / epsilon

    if rejection_sampling:
        while True:
            noise: float = np.random.laplace(0.0, scale)
            y: float = x + noise
            if min <= y <= max:
                break
    else:
        noise: float = np.random.laplace(0.0, scale)
        y: float = x + noise

    y = round(y, decimal_places)

    return y
