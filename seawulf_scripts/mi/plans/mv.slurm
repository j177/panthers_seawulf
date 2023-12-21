#!/bin/bash
#SBATCH --job-name=job_mv
#SBATCH --nodes=1
#SBATCH --time=8:00:00
#SBATCH --partition=v100
#SBATCH --output=output_mv.log
#SBATCH --error=error_mv.log

# load necessary modules
module purge
module load gerrychain/0.2.17 

# run python script
python generate_mi250.py