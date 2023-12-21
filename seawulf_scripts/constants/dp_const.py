MI_VTD = "data/MI_VTDs.json"
NY_VTD = "data/NY_VTDs.json"
PA_VTD = "data/PA_VTDs.json"

states = {"Michigan": "mi", "New York": "ny", "Penn": "pa"}
small_ensemble = 250
large_ensemble = 5000
epsilon = 0.02
pop_deivation = 0.05
node_repeats = 2
total_steps = 10000

# mi - 14
mi_num_dp = list(range(1, 15))

# ny - 27
ny_num_dp = list(range(1, 28))

# pa - 18
pa_num_dp = list(range(1, 19))
