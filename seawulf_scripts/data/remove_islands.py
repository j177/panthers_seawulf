import json
from networkx.readwrite import json_graph
from networkx import is_connected, connected_components
from gerrychain import Graph

# load the graph from JSON
graph = Graph.from_json("graph_mi_vtd.json")

# identify and remove nodes in non-largest connected components
components = list(connected_components(graph))
biggest_component_size = max(len(c) for c in components)
problem_components = [c for c in components if len(
    c) != biggest_component_size]

for component in problem_components:
    for node in component:
        graph.remove_node(node)

# check if the graph is still connected
print(is_connected(graph))

graph.to_json("MI_VTDs_without_islands.json")


# save the modified graph
# with open("PA_VTDs_without_islands.json", "w") as json_file:
#     json.dump(graph_data, json_file, indent=2)
