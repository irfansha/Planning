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
  parser.add_argument("--mail_type", help="mail type", default = 'ALL')
  parser.add_argument("--mail_user", help="mail", default = 'irfansha.shaik@cs.au.dk')
  args = parser.parse_args()

  competition_domains = ["IPC2/Blocks/", "IPC2/Elevator/", "IPC3/DriverLog/",
                         "IPC3/ZenoTravel/" , "IPC4/Satellite/", "IPC5/Rovers/"]

  competition_domain_path = "./competition_benchmarks/"

  encodings = ["UG", "SAT"]

  encoding = "UG"

  for domain in competition_domains:

    competition_domain = domain.split("/")
    domain_name = competition_domain[1]

    # Generate batch script:
    f = open("run_UG_"+ domain_name + ".sh", "w")

    f.write("#!/bin/bash\n")
    f.write("SBATCH --partition=" + args.partition + "\n")
    f.write("SBATCH --nodes=" + args.nodes + "\n")
    f.write("SBATCH --mem=" + args.mem + "\n")
    # Exclusive flag:
    f.write("SBATCH --exclusive\n")
    f.write("SBATCH --time=" + args.time + ":10:00" + "\n")
    f.write("SBATCH --mail-type=" + args.mail_type + "\n")
    f.write("SBATCH --mail-user=" + args.mail_user + "\n\n")

    f.write("echo '========= Job started  at `date` =========='\n\n")

    f.write("cd $SLURM_SUBMIT_DIR\n\n")



    if (encoding == 'UG'):
      f.write("time python3 main.py --dir " + competition_domain_path + domain + " --run_benchmarks 1 --preprocessing 1 --parameters_overlap 1 --time_limit 5 > out_UG_" + domain_name + "\n")

    f.write("\necho '========= Job finished at `date` =========='\n")
    f.close()

    command = 'sbatch ' + "run_UG_"+ domain_name + ".sh"
    os.popen(command)
