import os

os.environ["OMP_NUM_THREADS"] = "1"

from sklearn.manifold import MDS
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import json
import numpy as np

json_file_path = '/Users/joice/Desktop/ham_dist_matrix_mi_250_FINAL.json'

with open(json_file_path, 'r') as file:
    ham_dist_matrix = json.load(file)

mds = MDS(n_components=2, random_state=0, dissimilarity='precomputed')
pos = mds.fit(ham_dist_matrix).embedding_

# calculate silhouette scores for different values of k
silhouette_scores = []
for k in range(2, 15):  # Adjust the range as needed
    kmeans = KMeans(n_clusters=k, init='k-means++',
                    max_iter=300, n_init=10, random_state=0)
    labels = kmeans.fit_predict(pos)
    silhouette_avg = silhouette_score(pos, labels)
    silhouette_scores.append(silhouette_avg)

print("silouette scores", silhouette_scores)
# find the optimal k based on the highest silhouette score
optimal_k = np.argmax(silhouette_scores) + 2  # Add 2 to get the actual k value

# optimal k to cluster data
kmeans_optimal = KMeans(n_clusters=optimal_k, init='k-means++',
                        max_iter=300, n_init=10, random_state=0)
labels_optimal = kmeans_optimal.fit_predict(pos)

# create an array of objects with required structure
result_objects = []
for i in range(len(labels_optimal)):
    result_objects.append({
        'id': f'mi_{i}',
        'point': {'x': pos[i, 0], 'y': pos[i, 1]},
        'cluster': int(labels_optimal[i])
    })

print(result_objects)
# save the array of objects to a JSON file
result_json_path = '/Users/joice/Desktop/ham_mi_clusters.json'
with open(result_json_path, 'w') as result_file:
    json.dump(result_objects, result_file, indent=2)

print("K value", optimal_k)
print("labels", labels_optimal)
