#!/bin/bash
#SBATCH --job-name=job_hp_final
#SBATCH --nodes=1
#SBATCH --time=1-23:59:59
#SBATCH --partition=gpu-long
#SBATCH --output=output_hp_final.log
#SBATCH --error=error_hp_final.log

module load anaconda/3

# run python script
python hammingDistance_v3_pa.py