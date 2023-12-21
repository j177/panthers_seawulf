from multiprocessing import Pool
from optimal_transport import Pair
from gerrychain import Partition, Graph
from itertools import combinations
import numpy as np
import json
import os


def calculate_distance(pair_args):
    i, j = pair_args
    plan_i = Partition(graph=Graph.from_json(
        f"mi_plan{i}.json"), assignment="CD_2020")
    plan_j = Partition(graph=Graph.from_json(
        f"mi_plan{j}.json"), assignment="CD_2020")
    return Pair(plan_i, plan_j).distance


def calculate_distances(num_partitions):
    index_pairs = list(combinations(range(num_partitions), 2))

    with Pool() as pool:
        distances = pool.map(calculate_distance, index_pairs)

    # create the distances matrix
    distance_matrix = np.zeros((num_partitions, num_partitions))
    for (i, j), distance in zip(index_pairs, distances):
        distance_matrix[i, j] = distance
        distance_matrix[j, i] = distance

    return distance_matrix


def normalize_distances(distances):
    max_value = np.max(distances)
    normalized_distances = distances / max_value
    return normalized_distances


def save_to_json(data, filename):
    with open(filename, "w") as json_file:
        json.dump(data, json_file)


if __name__ == "__main__":
    num_partitions = 2

    distances = calculate_distances(num_partitions)

    normalized_distances = normalize_distances(distances)
    normalized_distances_list = normalized_distances.tolist()
    print(normalized_distances_list)

    save_directory = ""
    save_path = os.path.join(save_directory, "opt_test_matrix.json")
    save_to_json(normalized_distances_list, save_path)
