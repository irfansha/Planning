# Irfansha Shaik, 16.02.2021, Aarhus.

'''
Dispatches batch jobs of state-of-the-art grounded planners on Organic synthesis benchmarks
(can be extended to other domains later)
'''

import glob
import re
import os
from pathlib import Path
import argparse, textwrap



def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


# Main:
if __name__ == '__main__':
  text = "Generates and dispatches batch jobs for various domains and parameter sweep with SOA planners"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--partition", help="partition name", default = 'q48')
  parser.add_argument("--nodes", help="no of nodes", default = '1')
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
  parser.add_argument("--planner", help=textwrap.dedent('''
                                  Planners:
                                  M = madagascar
                                  FDS  = Fast Downward soup 18
                                  D  = Delfi'''))


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



    files_list = glob.glob(benchmarks_path + test_domain_path + domain_name + "/*")
    files_list.sort(key=natural_keys)

    for file_path in files_list:
      if ('domain' in file_path):
        domain_filepath = file_path
      else:
        problem_filepath = file_path


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


    if (args.planner == 'FDS'):
      options = " --alias seq-sat-fdss-1   --overall-time-limit 5000s --overall-memory-limit 300g --portfolio-single-plan --sas-plan /scratch/$SLURM_JOB_ID/plan_$SLURM_JOB_ID "
      f.write("time python3 downward/fast-downward.py " + options + domain_filepath + " " + problem_filepath + " > "+ args.output_dir + "out_" + domain_name + "_$SLURM_JOB_ID\n")

    command = 'sbatch run_' + domain_name + ".sh"



    f.write("\necho '========= Job finished at `date` =========='\n")
    #f.write("\nrm ./intermediate_files/* \n")
    f.close()


    print(command)
    #os.popen(command)
