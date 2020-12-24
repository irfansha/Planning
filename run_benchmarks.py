# Irfansha Shaik, 24.12.2020, Aarhus.

import argparse, textwrap
import glob
import re
import os
from pathlib import Path



def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def run_instance(domain_filepath, problem_filepath, args):
    print("Running " + problem_filepath)
    k = 2
    while(1):
      k = k*2
      command = 'python3 main.py -d ' + domain_filepath + ' -p ' + problem_filepath + ' -e ' + args.e + ' --run 2 -k ' + str(k) + ' --testing ' + str(args.testing) + ' --verbosity_level 0 --time_limit ' + str(args.time_limit)
      plan_status = os.popen(command).read()
      if ("Plan found" in plan_status):
          print("Plan found for length: " + str(k))
          if (args.testing != 0):
            if ("Plan valid" in plan_status):
              print("Plan valid")
            else:
              print("Plan invalid! Error. <---------------------------------------")
          return 0
      else:
          print("Plan not found for length: " + str(k))
          if ('Time out' in plan_status):
              print("Time out occured")
              return 1


# Main:
def run(args):
    # Checking if directory exists:
    if not Path(args.dir).is_dir():
      print("Invalid directory path: " + args.dir)
      exit
    files_list = glob.glob(args.dir + "*")
    files_list.sort(key=natural_keys)

    print(files_list)

    domain_filepath = args.dir + "domain.pddl"


    # Running each instances with time limit:
    for file_path in files_list:
        # Only considering problem files:
        if ('domain' not in file_path):
          timed_out = run_instance(domain_filepath, file_path, args)
          if (timed_out):
            continue