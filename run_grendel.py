# Irfansha Shaik, 24.01.2021, Aarhus.

import os
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
  args = parser.parse_args()

  if (args.only_testing == 0):
    competition_domains = ["IPC2/Blocks/", "IPC2/Elevator/", "IPC3/DriverLog/",
                           "IPC3/ZenoTravel/" , "IPC4/SATELLITE/", "IPC5/rovers/"]

    competition_domain_path = "./competition_benchmarks/"
  else:
    competition_domains = ["DriverLog/"]
    competition_domain_path = "./test_benchmarks/"

  encoding_variants = ["UG", "UG_po", "UG_po_pre", "SAT"]



  for encoding in encoding_variants:
    for domain in competition_domains:

      competition_domain = domain.split("/")
      domain_name = competition_domain[-2]

      # Generate batch script:
      if (encoding == "UG"):
        f = open("run_UG_"+ domain_name + ".sh", "w")
      elif (encoding == "UG_po"):
        f = open("run_UG_po_"+ domain_name + ".sh", "w")
      elif (encoding == "UG_po_pre"):
        f = open("run_UG_po_pre_"+ domain_name + ".sh", "w")
      elif (encoding == "SAT"):
        f = open("run_SAT_"+ domain_name + ".sh", "w")


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
        f.write("time python3 main.py --dir " + competition_domain_path + domain + default_file_names + " --run_benchmarks 1 --time_limit 5000 > out_UG_" + domain_name + "_$SLURM_JOB_ID\n")
        command = 'sbatch ' + "run_UG_"+ domain_name + ".sh"
      elif(encoding == 'UG_po'):
        f.write("time python3 main.py --dir " + competition_domain_path + domain + default_file_names + " --parameters_overlap 1 --run_benchmarks 1 --time_limit 5000 > out_UG_po_" + domain_name + "_$SLURM_JOB_ID\n")
        command = 'sbatch ' + "run_UG_po_"+ domain_name + ".sh"
      elif(encoding == 'UG_po_pre'):
        f.write("time python3 main.py --dir " + competition_domain_path + domain + default_file_names + " --preprocessing 1 --run 1 --parameters_overlap 1 --run_benchmarks 1 --time_limit 5000 > out_UG_po_pre_" + domain_name + "_$SLURM_JOB_ID\n")
        command = 'sbatch ' + "run_UG_po_pre_"+ domain_name + ".sh"
      elif(encoding == 'SAT'):
        f.write("time python3 main.py --dir " + competition_domain_path + domain + default_file_names + " --run_benchmarks 1 -e SAT --solver_type 5 --time_limit 5000 > out_SAT_" + domain_name + "$SLURM_JOB_ID\n")
        command = 'sbatch ' + "run_SAT_"+ domain_name + ".sh"

      f.write("\necho '========= Job finished at `date` =========='\n")
      #f.write("\nrm ./intermediate_files/* \n")
      f.close()


      print(command)
      #os.popen(command)
