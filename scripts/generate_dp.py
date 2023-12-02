from gerrychain import (GeographicPartition, Partition, Graph,
                        MarkovChain, proposals, updaters, constraints, accept, Election)
from gerrychain.proposals import recom
from functools import partial
from gerrychain.updaters import cut_edges
from multiprocessing import Pool
from constants import dp_const
import json

vtdGraph = Graph.from_json(dp_const.MICHIGAN)
elections = [
    Election("GEN20", {"Democratic": "G20PREDBID", "Republican": "G20PRERTRU"})]
my_updaters = {"population": updaters.Tally("TOT_POP21", alias="population")}
election_updaters = {election.name: election for election in elections}
my_updaters.update(election_updaters)


def generate_district_plan(seed):
    initial_partition = GeographicPartition(
        vtdGraph, assignment="CD_2020", updaters=my_updaters)

    # print("initial partition", initial_partition["population"])

    ideal_population = sum(
        initial_partition["population"].values()) / len(initial_partition)

    proposal = partial(recom,
                       pop_col="TOT_POP21",
                       pop_target=ideal_population,
                       epsilon=0.05,
                       node_repeats=2
                       )

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

    final_partition = None
    for state in chain:
        final_partition = state

    # print("final_partition", final_partition["population"])

    final_partition.graph.to_json(f"mi_dp_{seed}.json")


if __name__ == "__main__":
    target_plans = dp_const.small_ensemble
    pool = Pool()
    seeds = range(target_plans)
    pool.map(generate_district_plan, seeds)
    pool.close()
    pool.join()
