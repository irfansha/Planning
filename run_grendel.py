# Irfansha Shaik, 24.01.2021, Aarhus.

import os
from pathlib import Path
import argparse

# Main:
if __name__ == '__main__':
  text = "Generates and dispatches batch jobs for various domains and parameter sweep"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--partition", help="partition name", default = 'q48')
  parser.add_argument("--nodes", help="no of nodes", default = '1')
  parser.add_argument("--mem", help="mem in GB, default 0 i.e. all of it", default = '0')
  parser.add_argument("--time", help="estimated time in hours", default = '24')
  parser.add_argument("--mail_type", help="mail type", default = 'END')
  parser.add_argument("--mail_user", help="mail", default = 'irfansha.shaik@cs.au.dk')
  parser.add_argument("--only_testing", type =int, help=" only for testing purposes", default = 0)
  parser.add_argument("--typed", type =int, help=" typed/untyped domains [1/0] default 1", default = 1)
  parser.add_argument("--output_dir", help="directory path for output files", default = 'out_data/')
  args = parser.parse_args()

  if (args.only_testing == 0):
    if (args.typed == 1):
      test_domains = ["Blocks/", "DriverLog/", "Elevator/", "FreeCell/",
                      "rovers/", "SATELLITE/", "termes/", "termes-opt18/",
                      "Thoughtful/", "tidybot-opt11-strips/", "Visitall/",
                      "visitall-opt11-strips/", "visitall-sat11-strips/", "ZenoTravel/"]
      test_domain_path = "./typed_benchmarks/"
    else:
      test_domains = ["blocks/", "driverlog/", "grid/", "logistics00/", "mystery/", "rovers-02/", "zenotravel/",
                      "blocks-3op/", "ferry/", "gripper/", "miconic/", "no-mprime/", "satellite/",
                      "depot/", "freecell/", "hanoi/", "movie/", "no-mystery/", "tsp/"]
      test_domain_path = "./untyped_benchmarks/"

  else:
    test_domains = ["visitall-opt11-strips/"]
    test_domain_path = "./test_benchmarks/"

  encoding_variants = ["UG", "UG_po", "UG_po_pre", "SAT", "SATL"]

  # Checking if out directory exits:
  if not Path(args.output_dir).is_dir():
    print("Invalid directory path: " + args.output_dir)
    print("Creating new directory with same path.")
    os.mkdir(args.output_dir)

  for encoding in encoding_variants:
    for domain in test_domains:

      test_domain = domain.split("/")
      domain_name = test_domain[-2]

      # Generate batch script:
      if (encoding == "UG"):
        f = open("run_UG_"+ domain_name + ".sh", "w")
      elif (encoding == "UG_po"):
        f = open("run_UG_po_"+ domain_name + ".sh", "w")
      elif (encoding == "UG_po_pre"):
        f = open("run_UG_po_pre_"+ domain_name + ".sh", "w")
      elif (encoding == "SAT"):
        f = open("run_SAT_"+ domain_name + ".sh", "w")
      elif (encoding == "SATL"):
        f = open("run_SATL_"+ domain_name + ".sh", "w")


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

      default_file_names = ' --encoding_out /scratch/$SLURM_JOB_ID/encoding_$SLURM_JOB_ID --solver_out /scratch/$SLURM_JOB_ID/solver_out_$SLURM_JOB_ID --preprocessed_encoding_out /scratch/$SLURM_JOB_ID/preprocessed_$SLURM_JOB_ID --plan_out /scratch/$SLURM_JOB_ID/plan_$SLURM_JOB_ID --encoding_intermediate_out /scratch/$SLURM_JOB_ID/intermediate_$SLURM_JOB_ID '


      if(encoding == 'UG'):
        f.write("time python3 main.py --dir " + test_domain_path + domain + default_file_names + " --run_benchmarks 1 --time_limit 5000 > " + args.output_dir + "out_UG_" + domain_name + "_$SLURM_JOB_ID\n")
        command = 'sbatch ' + "run_UG_"+ domain_name + ".sh"
      elif(encoding == 'UG_po'):
        f.write("time python3 main.py --dir " + test_domain_path + domain + default_file_names + " --parameters_overlap 1 --run_benchmarks 1 --time_limit 5000 > " + args.output_dir + "out_UG_po_" + domain_name + "_$SLURM_JOB_ID\n")
        command = 'sbatch ' + "run_UG_po_"+ domain_name + ".sh"
      elif(encoding == 'UG_po_pre'):
        f.write("time python3 main.py --dir " + test_domain_path + domain + default_file_names + " --preprocessing 1 --run 1 --parameters_overlap 1 --run_benchmarks 1 --time_limit 5000 > " + args.output_dir + "out_UG_po_pre_" + domain_name + "_$SLURM_JOB_ID\n")
        command = 'sbatch ' + "run_UG_po_pre_"+ domain_name + ".sh"
      elif(encoding == 'SAT'):
        f.write("time python3 main.py --dir " + test_domain_path + domain + default_file_names + " --run_benchmarks 1 -e SAT --solver_type 5 --time_limit 5000 > " + args.output_dir + "out_SAT_" + domain_name + "$SLURM_JOB_ID\n")
        command = 'sbatch ' + "run_SAT_"+ domain_name + ".sh"
      elif(encoding == 'SATL'):
        f.write("time python3 main.py --dir " + test_domain_path + domain + default_file_names + " --run_benchmarks 1 -e SAT -t l --solver_type 5 --time_limit 5000 > " + args.output_dir + "out_SATL_" + domain_name + "$SLURM_JOB_ID\n")
        command = 'sbatch ' + "run_SATL_"+ domain_name + ".sh"


      f.write("\necho '========= Job finished at `date` =========='\n")
      #f.write("\nrm ./intermediate_files/* \n")
      f.close()


      print(command)
      #os.popen(command)
