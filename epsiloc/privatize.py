from epsiloc.utils.fetch import fetch_dataset
from epsiloc.utils.save import save_dataset
from epsiloc.mechanisms.discrete import discrete_laplace
from epsiloc.mechanisms.continuous import laplace
from epsiloc.mechanisms.categorical import k_randomized_response

def privatize(dataset_path: str):
    metadata, data = fetch_dataset(dataset_path)

    data_private: list[list[any]] = []

    for i in range(len(data)):
        row_private: list[any] = []
        for j in range(len(metadata)):
            value = data[i][j]
            meta = metadata[j]
            if isinstance(value, int):
                row_private.append(discrete_laplace(value, **meta))
            elif isinstance(value, float):
                row_private.append(laplace(value, **meta))
            elif isinstance(value, str):
                row_private.append(k_randomized_response(value, **meta))
        data_private.append(row_private)

    save_dataset(data_private, dataset_path)
