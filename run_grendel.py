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
  parser.add_argument("-e", type =int, help="UE/SAT [0/1], default 0", default = 0)
  parser.add_argument("--ue", type =int, help="UE/UE+ [0/1], default 0", default = 1)
  parser.add_argument("--tf", type =int, help="b/l [0/1], default 0", default = 0)
  parser.add_argument("--dt", type =int, help="detype [0/1], default 0", default = 1)
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
                       "Hiking/", "SATELLITE/", "storage/", "termes/", "termes-opt18/",
                      "Thoughtful/", "tidybot-opt11-strips/",
                      "visitall-opt11-strips/", "visitall-sat11-strips/", "ZenoTravel/"]
      test_domain_path = "./Final_benchmarks/typed_benchmarks/"
    else:
      test_domains = ["blocks/", "driverlog/", "grid/", "logistics00/", "mystery/", "zenotravel/",
                      "blocks-3op/", "gripper/", "miconic/", "no-mprime/", "satellite/",
                      "depot/", "freecell/", "hanoi/", "movie/", "no-mystery/", "mprime/", "mystery/"]
      test_domain_path = "./Final_benchmarks/untyped_benchmarks/"

  else:
    test_domains = ["visitall-opt11-strips/"]
    test_domain_path = "./test_benchmarks/"

  if (args.e == 0):
    encoding_variants = ["UG_po", "UG_po_pre"]
  else:
    #encoding_variants = ["SAT"]
    encoding_variants = ["M-SAT"]

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
      f = open("run_" + encoding + "_"+ str(args.ue) + "_" + str(args.tf) + "_" + str(args.dt) + "_" + domain_name + ".sh", "w")

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


      if(encoding == 'UG'):
        if (args.ue == 0):
          options = " -e UE "
        else:
          options = " -e UE+ "
      elif(encoding == 'UG_po'):
        if (args.ue == 0):
          options = " -e UE --parameters_overlap 1 "
        else:
          options = " -e UE+ --parameters_overlap 1 "
      elif(encoding == 'UG_po_pre'):
        if (args.ue == 0):
          options = " -e UE --preprocessing 2 --run 2 --parameters_overlap 1 "
        else:
          options = " -e UE+ --preprocessing 2 --run 2 --parameters_overlap 1 "
      elif(encoding == 'SAT'):
        if (args.tf == 0):
          options = " -e SAT --solver_type 5 -t b "
        else:
          options = " -e SAT --solver_type 5 -t l "
      elif(encoding == 'M-SAT'):
        options = " -e M-seq --solver_type 5 --run 1"

      if (args.dt == 1):
        options += ' --de_type 1 '
      else:
        options += ' --de_type 0 '

      f.write("time python3 main.py --dir " + test_domain_path + domain + default_file_names + options + " --run_benchmarks 1 --time_limit 5000 > " + args.output_dir + "out_" + encoding + "_" + str(args.ue) + "_" + str(args.tf) + "_" + str(args.dt) + "_" + domain_name + "_$SLURM_JOB_ID\n")

      command = 'sbatch run_' + encoding + "_"+ str(args.ue) + "_" + str(args.tf) + "_" + str(args.dt) + "_" + domain_name + ".sh"



      f.write("\necho '========= Job finished at `date` =========='\n")
      #f.write("\nrm ./intermediate_files/* \n")
      f.close()


      print(command)
      #os.popen(command)
