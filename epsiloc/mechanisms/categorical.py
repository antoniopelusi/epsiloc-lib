import numpy as np

def _map_to_index(x: str, categories: list[str]) -> int:
    if x not in categories:
        raise ValueError(f"{x} is not in categories")
    return categories.index(x)

def _map_to_category(index: int, categories: list[str]) -> str:
    if not (0 <= index < len(categories)):
        raise ValueError(f"Index {index} out of bounds")
    return categories[index]

def k_randomized_response(
    x: str,
    epsilon: float,
    categories: list[str]
) -> str:
    k = len(categories)
    idx = _map_to_index(x, categories)

    p = np.exp(epsilon) / (np.exp(epsilon) + k - 1)
    if np.random.random() < p:
        noisy_idx = idx
    else:
        j = np.random.randint(k - 1)
        noisy_idx = j if j < idx else j + 1

    return _map_to_category(noisy_idx, categories)
