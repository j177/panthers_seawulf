import os
import json
import numpy as np
import multiprocessing

def extract_information(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        nodes = data.get('nodes', [])
        return nodes

def calculate_difference_sum(args):
    nodes1, nodes2 = args
    difference_sum = 0
    for node1 in nodes1:
        for node2 in nodes2:
            if node1.get('id') == node2.get('id') and node1.get('CD_2020') != node2.get('CD_2020'):
                difference_sum += 1
                break
    return difference_sum

def normalize_matrix(matrix):
    max_value = np.max(matrix)
    normalized_matrix = matrix / max_value
    return normalized_matrix

def process_file(i, file_path, folder_path, file_list, matrix_size):
    differences = []
    
    nodes1 = extract_information(file_path)

    # use multiprocessing to calculate differences in parallel
    with multiprocessing.Pool() as pool:
        args_list = [(nodes1, extract_information(os.path.join(folder_path, file_list[j]))) for j in range(matrix_size) if i != j]
        differences = pool.map(calculate_difference_sum, args_list)

    return differences

def main():
    folder_path = "/gpfs/scratch/joifan/mi_plans_simplified/"
    output_dir = "/gpfs/scratch/joifan/"
    file_list = os.listdir(folder_path)

    matrix_size = len(file_list)
    matrix = np.zeros((matrix_size, matrix_size), dtype=int)

    os.makedirs(output_dir, exist_ok=True)
    matrix_file_path = "ham_dist_matrix_mi_250_FINAL.json"

    for i in range(matrix_size):
        differences = process_file(i, os.path.join(folder_path, file_list[i]), folder_path, file_list, matrix_size)

        for j, diff in enumerate(differences):
            matrix[i, j] = diff

    norm_matrix = normalize_matrix(matrix)
    matrix_as_list = norm_matrix.tolist()
    print(matrix_as_list)

    with open(os.path.join(output_dir, matrix_file_path), 'w') as json_file:
        json.dump(matrix_as_list, json_file)

if __name__ == "__main__":
    main()
