## https://blog.paperspace.com/clustering-using-the-genetic-algorithm/

import numpy
import matplotlib.pyplot
import pygad


num_clusters = None
feature_vector_length = None
data = None


def euclidean_distance(X, Y):
    return numpy.sqrt(numpy.sum(numpy.power(X - Y, 2), axis=1))


def cluster_data(solution, solution_idx):
    global num_clusters, feature_vector_length, data
    cluster_centers = []
    all_clusters_dists = []
    clusters = []
    clusters_sum_dist = []

    for clust_idx in range(num_clusters):
        cluster_centers.append(
            solution[
                feature_vector_length
                * clust_idx : feature_vector_length
                * (clust_idx + 1)
            ]
        )
        cluster_center_dists = euclidean_distance(data, cluster_centers[clust_idx])
        all_clusters_dists.append(numpy.array(cluster_center_dists))

    cluster_centers = numpy.array(cluster_centers)
    all_clusters_dists = numpy.array(all_clusters_dists)

    cluster_indices = numpy.argmin(all_clusters_dists, axis=0)
    for clust_idx in range(num_clusters):
        clusters.append(numpy.where(cluster_indices == clust_idx)[0])
        if len(clusters[clust_idx]) == 0:
            clusters_sum_dist.append(0)
        else:
            clusters_sum_dist.append(
                numpy.sum(all_clusters_dists[clust_idx, clusters[clust_idx]])
            )

    clusters_sum_dist = numpy.array(clusters_sum_dist)

    return (
        cluster_centers,
        all_clusters_dists,
        cluster_indices,
        clusters,
        clusters_sum_dist,
    )


def fitness_func(solution, solution_idx):
    _, _, _, _, clusters_sum_dist = cluster_data(solution, solution_idx)

    fitness = 1.0 / (numpy.sum(clusters_sum_dist) + 0.00000001)

    return fitness


def cluster(X, _num_clusters=None):
    global num_clusters, feature_vector_length, data
    data = X

    num_clusters = _num_clusters
    feature_vector_length = data.shape[1]
    num_genes = num_clusters * feature_vector_length

    ga_instance = pygad.GA(
        num_generations=100,
        sol_per_pop=10,
        init_range_low=0,
        init_range_high=20,
        num_parents_mating=5,
        keep_parents=2,
        num_genes=num_genes,
        fitness_func=fitness_func,
        suppress_warnings=True,
    )

    ga_instance.run()

    (
        best_solution,
        best_solution_fitness,
        best_solution_idx,
    ) = ga_instance.best_solution()
    print("Best solution is {bs}".format(bs=best_solution))
    print("Fitness of the best solution is {bsf}".format(bsf=best_solution_fitness))
    print(
        "Best solution found after {gen} generations".format(
            gen=ga_instance.best_solution_generation
        )
    )

    (
        cluster_centers,
        all_clusters_dists,
        cluster_indices,
        clusters,
        clusters_sum_dist,
    ) = cluster_data(best_solution, best_solution_idx)

    for cluster_idx in range(num_clusters):
        cluster_x = data[clusters[cluster_idx], 0]
        cluster_y = data[clusters[cluster_idx], 1]
        matplotlib.pyplot.scatter(cluster_x, cluster_y)
        matplotlib.pyplot.scatter(
            cluster_centers[cluster_idx, 0],
            cluster_centers[cluster_idx, 1],
            linewidths=5,
        )
    matplotlib.pyplot.title("Clustering using PyGAD")
    matplotlib.pyplot.show()

    return cluster_indices
