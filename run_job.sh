
#!/bin/bash
#SBATCH --job-name=Serialjob
#SBATCH --partition=q40
#SBATCH --mem=4G
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=10
#SBATCH --time=24:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=irfansha.shaik@cs.au.dk

echo "========= Job started  at `date` =========="

# Go to the directory where this job was submitted
cd $SLURM_SUBMIT_DIR

# copy inputdata and the executable to the scratch-directory
cp * /scratch/$SLURM_JOB_ID

# change directory to the local scratch-directory, and run:
cd /scratch/$SLURM_JOB_ID
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
python3 main.py --run_benchmarks 1 --dir=data/ > out

# copy home the outputdata:
cp out $SLURM_SUBMIT_DIR/out.$SLURM_JOB_ID

echo "========= Job finished at `date` =========="
#