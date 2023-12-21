from gerrychain import (Partition, Graph, MarkovChain,
                        updaters, constraints, accept, tree)
from gerrychain.proposals import recom
from functools import partial
from multiprocessing import Pool
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from constants import dp_const
import pandas as pd
import os
import random


class DistrictPlanGenerator:
    def __init__(self, state, graph, num_districts, random_initial_partition, ideal_population, pop_col, seed, ensemble_output_path, plan_output_path, dis_geo_output_path):
        self.state = state
        self.graph = graph
        self.num_districts = num_districts
        self.random_initial_partition = random_initial_partition
        self.ideal_population = ideal_population
        self.pop_col = pop_col
        self.seed = seed
        self.ensemble_output_path = ensemble_output_path
        self.plan_output_path = plan_output_path
        self.dis_geo_output_path = dis_geo_output_path

    def process_iteration(self, plan_number):
        if self.seed is not None:
            random.seed(self.seed + plan_number)
        node_updaters = {}
        node_attr = ["CD_2020", "Republican", "Democrat", "TOTAL_POP", "HISP_POP", "WHITE_POP", "BLACK_POP",
                     "NATIVE_POP", "ASIAN_POP", "PACIF_POP", "OTHER_POP", "2MORE_POP", "TOTAL_VAP", "HISP_VAP", "BLACK_VAP"]
        for attr in node_attr:
            node_updaters[attr] = updaters.Tally(attr)

        initial_partition = Partition(
            graph=self.graph, assignment="CD_2020", updaters=node_updaters)

        if self.random_initial_partition:
            random_assignment = tree.recursive_tree_part(
                graph=self.graph, parts=self.num_districts, pop_target=self.ideal_population, pop_col=self.pop_col, epsilon=dp_const.epsilon)
            initial_partition.assignment.update(random_assignment)

        proposal = partial(recom, pop_col=self.pop_col,
                           pop_target=self.ideal_population, epsilon=dp_const.epsilon, node_repeats=dp_const.node_repeats)

        pop_constraint = constraints.within_percent_of_ideal_population(
            initial_partition, dp_const.pop_deivation, pop_key=self.pop_col)

        chain = MarkovChain(proposal=proposal,
                            constraints=[pop_constraint],
                            accept=accept.always_accept,
                            initial_state=initial_partition,
                            total_steps=dp_const.total_steps
                            )
        for new_partition in chain:
            pass

        plan_data = []
        plan_geo = []

        for part in new_partition.parts:
            precinct_geometries = []
            for precinct_id in new_partition.parts[part]:
                precinct_geometry = new_partition.graph.nodes[precinct_id]["geometry"]
                new_partition.graph.nodes[precinct_id]["CD_2020"] = part
                shapely_geometry = shape(precinct_geometry)
                precinct_geometries.append(shapely_geometry)

            district_geometry = unary_union(precinct_geometries)
            district_geojson = mapping(district_geometry)
            plan_geo.append({"geometry": district_geojson})
            plan_data.append({
                "district_id": part,
                "dem": new_partition["Democrat"][part],
                "rep": new_partition["Republican"][part],
                "pop": new_partition["TOTAL_POP"][part],

                "hispanic": new_partition["HISP_POP"][part],
                "white": new_partition["WHITE_POP"][part],
                "black": new_partition["BLACK_POP"][part],
                "native": new_partition["NATIVE_POP"][part],
                "asian": new_partition["ASIAN_POP"][part],
                "pacific": new_partition["PACIF_POP"][part],
                "other": new_partition["OTHER_POP"][part],
                "two_more": new_partition["2MORE_POP"][part],

                "vap_pop": new_partition["TOTAL_VAP"][part],
                "hisp_vap": new_partition["HISP_VAP"][part],
                "black_vap": new_partition["BLACK_VAP"][part]

            })
        data_dict = {
            "plans": plan_data
        }
        # saves partition of the generated district plan
        new_partition.graph.to_json(os.path.join(self.plan_output_path,
                                                 f"{self.state}_plan{plan_number}.json"))

        # saves geometry of the generated district plan
        geo_df = pd.DataFrame(plan_geo)
        geo_df.to_json(os.path.join(
            self.dis_geo_output_path, f"{self.state}_plan{plan_number}_geometry.json"))

        return data_dict

    def run(self, target_plans):
        shared_list = []

        with Pool() as pool:
            results = pool.map(self.process_iteration,
                               range(0, target_plans))
            shared_list.extend(results)

        shared_df = pd.DataFrame(shared_list)
        df_json_file_path = f"{self.state}_{target_plans}_ensemble.json"
        shared_df.to_json(os.path.join(
            self.ensemble_output_path, df_json_file_path), indent=2)


if __name__ == "__main__":
    state = dp_const.states["Michigan"]
    graph = Graph.from_json(dp_const.MI_VTD)
    num_districts = dp_const.mi_num_dp
    random_initial_partition = True
    ideal_population = sum(
        graph.nodes[node]["TOTAL_POP"] for node in graph.nodes) / len(num_districts)
    pop_col = "TOTAL_POP"
    seed = 17
    
    ensemble_output_path = '/gpfs/scratch/joifan/ensembles/'
    plan_output_path = '/gpfs/scratch/joifan/mi_plans/'
    dis_geo_output_path = '/gpfs/scratch/joifan/mi_geo/'

    gen = DistrictPlanGenerator(
        state=state, graph=graph, num_districts=num_districts, random_initial_partition=random_initial_partition, ideal_population=ideal_population, pop_col=pop_col, seed=seed, ensemble_output_path=ensemble_output_path, plan_output_path=plan_output_path, dis_geo_output_path=dis_geo_output_path)
    gen.run(target_plans=250)
