#!/bin/bash
#SBATCH --job-name=job_p2
#SBATCH --nodes=1
#SBATCH --time=7-00:00:00
#SBATCH --partition=extended-28core
#SBATCH --output=output_p2.log
#SBATCH --error=error_p2.log

# Load necessary modules
module purge
module load gerrychain/0.2.17 

# run python script
python generate_pa2000.py