#!/bin/bash
#SBATCH --job-name=job_p
#SBATCH --nodes=1
#SBATCH --time=1-00:00:00
#SBATCH --partition=gpu-long
#SBATCH --output=output_p.log
#SBATCH --error=error_p.log

# Load necessary modules
module purge
module load gerrychain/0.2.17 

# run python script
python generate_pa250.py