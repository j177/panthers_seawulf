#!/bin/bash
#SBATCH --job-name=N_job_om_e
#SBATCH --nodes=1
#SBATCH --time=6-00:00:00
#SBATCH --partition=extended-28core
#SBATCH --output=output_N_om_e.log
#SBATCH --error=error_N_om_e.log

# load necessary modules
module purge
module load anaconda/3

# create + activate conda environment
source activate optimal_transport

# install required packages
conda install -c conda-forge cvxpy gerrychain

# run python script
python new_opt_mi.py

# deactivate conda environment
conda deactivate