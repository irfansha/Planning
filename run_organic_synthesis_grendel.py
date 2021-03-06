# Irfansha Shaik, 10.02.2021, Aarhus.

import os
from pathlib import Path
import argparse, textwrap

# Main:
if __name__ == '__main__':
  text = "Generates and dispatches batch jobs for various domains and parameter sweep"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--partition", help="partition name", default = 'q48')
  parser.add_argument("--nodes", help="no of nodes", default = '1')
  parser.add_argument("--encoding", help="[M-seq/UE]", default = 'UE')
  parser.add_argument("--mem", help="mem in GB, default 0 i.e. all of it", default = '0')
  parser.add_argument("--time", help="estimated time in hours", default = '24')
  parser.add_argument("--mail_type", help="mail type", default = 'END')
  parser.add_argument("--mail_user", help="mail", default = 'irfansha.shaik@cs.au.dk')
  parser.add_argument("--output_dir", help="directory path for output files", default = 'out_data/')
  parser.add_argument("--problem_set", help=textwrap.dedent('''
                                  problem set to run:
                                  sat18 = organic-synthesis-sat18
                                  opt18 = organic-synthesis-opt18
                                  alkene  = Alkene_problem
                                  mitexams  = OrganicSynthesisMITexamsBenchmark'''))

  args = parser.parse_args()

  benchmarks_path = "Organic_synthesis_complete_benchmarks/run_benchmarks_datasets/"

  if (args.problem_set == "sat18"):
    test_domain_path = "organic-synthesis-sat18/"
  elif (args.problem_set == "opt18"):
    test_domain_path = "organic-synthesis-opt18/"
  elif(args.problem_set == "alkene"):
    test_domain_path = "Alkene_problem/"
  elif(args.problem_set == "mitexams"):
    test_domain_path = "OrganicSynthesisMITexamsBenchmark/"

  # Checking if out directory exits:
  if not Path(args.output_dir).is_dir():
    print("Invalid directory path: " + args.output_dir)
    print("Creating new directory with same path.")
    os.mkdir(args.output_dir)

  for i in range(1, 21):
    # Alkene only has 18 problems:
    if (args.problem_set == "alkene" and i >= 19):
      continue
    # domain name with 0 padding:
    domain_name = "problem" + str(i).zfill(2)

    # Generate batch script:
    f = open("run_" + domain_name + ".sh", "w")

    f.write("#!/bin/bash\n")
    f.write("#SBATCH --partition=" + args.partition + "\n")
    f.write("#SBATCH --nodes=" + args.nodes + "\n")
    f.write("#SBATCH --mem=" + args.mem + "\n")
    # Exclusive flag:
    f.write("#SBATCH --exclusive\n")
    f.write("#SBATCH --time=" + args.time + ":00:00" + "\n")
    f.write("#SBATCH --mail-type=" + args.mail_type + "\n")
    f.write("#SBATCH --mail-user=" + args.mail_user + "\n\n")

    f.write("echo '========= Job started  at `date` =========='\n\n")

    f.write("cd $SLURM_SUBMIT_DIR\n\n")

    default_file_names = ' --dd_out /scratch/$SLURM_JOB_ID/dd_out_$SLURM_JOB_ID --dp_out /scratch/$SLURM_JOB_ID/dp_out_$SLURM_JOB_ID --encoding_out /scratch/$SLURM_JOB_ID/encoding_$SLURM_JOB_ID --solver_out /scratch/$SLURM_JOB_ID/solver_out_$SLURM_JOB_ID --preprocessed_encoding_out /scratch/$SLURM_JOB_ID/preprocessed_$SLURM_JOB_ID --plan_out /scratch/$SLURM_JOB_ID/plan_$SLURM_JOB_ID --encoding_intermediate_out /scratch/$SLURM_JOB_ID/intermediate_$SLURM_JOB_ID '

    if (args.encoding == 'UE'):
      options = " -e UE+ --preprocessing 2 --run 2 --parameters_overlap 1 --de_type 1 --step 1 --run_benchmarks 1 --time_limit 21600 > "
    elif (args.encoding == 'M-seq'):
      options = " -e M-seq --solver_type 5 --run 1 --step 1 --run_benchmarks 1 --time_limit 21600 > "

    f.write("time python3 main.py --dir " + benchmarks_path + test_domain_path + domain_name + "/ " + default_file_names + options + args.output_dir + "out_" + domain_name + "_$SLURM_JOB_ID\n")

    command = 'sbatch run_' + domain_name + ".sh"



    f.write("\necho '========= Job finished at `date` =========='\n")
    #f.write("\nrm ./intermediate_files/* \n")
    f.close()


    print(command)
    #os.popen(command)
