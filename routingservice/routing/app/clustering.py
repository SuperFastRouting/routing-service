import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering

def hierarchal_cluster_nodes(nodes, num_clusters):
    """Perform hierarchal clustering on a set of nodes (lon, lat)
    
    Parameters:
    nodes (list[tuple]): Nodes to be clustered
    num_cluster (int): Number of clusters

    Returns:
    clustered_nodes (list[tuple]): List of clusters
    """

    hierarchal_cluster = AgglomerativeClustering(n_clusters=num_clusters, metric='euclidean', linkage='ward')
    cluster_labels = hierarchal_cluster.fit_predict(nodes)

    clusters = []
    for i in range(0, num_clusters):
        clusters.append(np.where(cluster_labels == i)[0])

    return clusters
