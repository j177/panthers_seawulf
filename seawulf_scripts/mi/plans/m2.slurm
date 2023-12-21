#!/bin/bash
#SBATCH --job-name=job_m2
#SBATCH --nodes=1
#SBATCH --time=7-00:00:00
#SBATCH --partition=extended-28core
#SBATCH --output=output_jobm2.log
#SBATCH --error=error_m2.log

# load necessary modules
module purge
module load gerrychain/0.2.17 

# run Python script
python generate_mi2000.py