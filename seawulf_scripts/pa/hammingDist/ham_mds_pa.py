from sklearn.manifold import MDS
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import json
import numpy as np

json_file_path = '/Users/joice/Desktop/ham_dist_matrix_pa_250_FINAL.json'

with open(json_file_path, 'r') as file:
    ham_dist_matrix = json.load(file)

mds = MDS(n_components=2, random_state=0, dissimilarity='precomputed')
pos = mds.fit(ham_dist_matrix).embedding_

# calc silhouette scores for different values of k
silhouette_scores = []
for k in range(2, 15):  # Adjust the range as needed
    kmeans = KMeans(n_clusters=k, init='k-means++',
                    max_iter=300, n_init=10, random_state=0)
    labels = kmeans.fit_predict(pos)
    silhouette_avg = silhouette_score(pos, labels)
    silhouette_scores.append(silhouette_avg)

# find the optimal k based on the highest silhouette score
optimal_k = np.argmax(silhouette_scores) + 2  # Add 2 to get the actual k value

# optimal k to cluster data
kmeans_optimal = KMeans(n_clusters=optimal_k, init='k-means++',
                        max_iter=300, n_init=10, random_state=0)
labels_optimal = kmeans_optimal.fit_predict(pos)

cluster_points_list = []
largest_cluster_size = 0

for cluster_num in range(optimal_k):
    cluster_points = pos[labels_optimal == cluster_num]
    cluster_size = len(cluster_points)
    cluster_center = cluster_points.mean(axis=0)

    if cluster_size > largest_cluster_size:
        largest_cluster_size = cluster_size

    cluster_entry = {
        "id": f"pa_{cluster_num}",
        "point": {"x": cluster_center[0], "y": cluster_center[1], "size": cluster_size}
    }
    cluster_points_list.append(cluster_entry)

# normalize cluster sizes with the largest cluster size
for cluster_entry in cluster_points_list:
    cluster_entry["point"]["size_normalized"] = cluster_entry["point"]["size"] / largest_cluster_size

cluster_points_json_path = '/Users/joice/Desktop/ham_mi_cluster_coords_normalized.json'
with open(cluster_points_json_path, 'w') as cluster_points_file:
    json.dump(cluster_points_list, cluster_points_file, indent=2)

print(cluster_points_list)
