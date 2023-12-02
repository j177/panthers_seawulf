from gerrychain import (GeographicPartition, Partition, Graph, MarkovChain,
                        proposals, updaters, constraints, accept, Election)
from gerrychain.proposals import recom
from functools import partial
from networkx import is_connected, connected_components
from multiprocessing import Pool

# In order to run a markov chain, we need an adjacency graph of our VTD geometries
# and partition of our adjacency graph into district.
# This will be the INITIAL STATE of markov chain
graph = Graph.from_json("./graph_mi_2020_without_islands.json")

# for debugging islands
# components = list(connected_components(graph))
# arr = [len(c) for c in components]
# print(arr)
# biggest_component_size = max(len(c) for c in components)
# problem_components = [c for c in components if len(
#     c) != biggest_component_size]
# for component in problem_components:
#     for node in component:
#         graph.remove_node(node)
# print(is_connected(graph))
# graph.to_json("./graph_mi_2020_without_islands.json")

elections = [
    Election("GEN20", {"Democratic": "G20PREDBID", "Republican": "G20PRERTRU"})]
my_updaters = {"population": updaters.Tally("TOT_POP21", alias="population")}
election_updaters = {election.name: election for election in elections}
my_updaters.update(election_updaters)


def generate_district_plan(seed):
    initial_partition = GeographicPartition(
        graph, assignment="CD_2020", updaters=my_updaters)

    # ReCom proposal
    # Needs to know the ideal population for the districts so speed can be improved by bailing early on
    # unbalanced partitions
    ideal_population = sum(
        initial_partition["population"].values()) / len(initial_partition)

    # we use functools.partial to bind the extra parameters (pop_col, pop_target, epsilon, node_repeats)
    # of the recom proposal

    proposal = partial(recom,
                       pop_col="TOT_POP21",
                       pop_target=ideal_population,
                       epsilon=0.05,
                       node_repeats=2)

    compactness_bound = constraints.UpperBound(
        lambda p: len(p["cut_edges"]),
        2*len(initial_partition["cut_edges"])
    )

    pop_constraint = constraints.within_percent_of_ideal_population(
        initial_partition, 0.10)

    chain = MarkovChain(
        proposal=proposal,
        constraints=[
            pop_constraint,
            compactness_bound
        ],
        accept=accept.always_accept,
        initial_state=initial_partition,
        total_steps=10000
    )

    # Run the Markov Chain
    final_partition = None
    for step, partition in enumerate(chain):
        # Store the current partition
        final_partition = partition

    # DEBUGGING ONLY
    if step % 100 == 0:
        print(f"Step {step}/{len(chain)}")
        print("Current population deviation:", pop_constraint(partition))

    # Convert the final partition to a GeoDataFrame
    final_partition.graph.to_json(f"result_{state_name}_{plan_num}")


if __name__ == "__main__":
    # Set the target number of district plans to generate
    target_plans = 250

    # Create a pool of worker processes
    pool = Pool()
    seeds = range(target_plans)
    pool.map(generate_district_plan, seeds)
