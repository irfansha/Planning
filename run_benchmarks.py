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

def gen_new_arguments(domain, problem, k, args):
  new_command = ''
  for arg in vars(args):
    # We set these separately:
    if (arg == 'version'):
      continue
    elif (arg == 'd'):
      new_command += ' -d ' + domain
    elif(arg == 'p'):
      new_command += ' -p ' + problem
    elif(arg == 'k'):
      new_command += ' -k ' + str(k)
    elif(arg == "verbosity_level"):
      new_command += ' --verbosity_level 0'
    elif( arg == "run_benchmarks"):
      new_command += ' --run_benchmarks 0'
    elif (len(arg) == 1):
      new_command += ' -' + str(arg) + ' ' + str(getattr(args, arg))
    else:
      new_command += ' --' + str(arg) + ' ' + str(getattr(args, arg))
  return(new_command)

def run_instance(domain_filepath, problem_filepath, args):
    print("---------------------------------------------------------------------------------------------")
    print("Running " + problem_filepath)
    print("---------------------------------------------------------------------------------------------")
    k = 0
    while(1):
      k = k + 5
      # domain and problem files are new:
      command_arguments = gen_new_arguments(domain_filepath, problem_filepath, k, args)
      # command = 'python3 main.py -d ' + domain_filepath + ' -p ' + problem_filepath + ' -e ' + args.e + ' --run ' + str(args.run) + ' -k ' + str(k) + ' --testing ' + str(args.testing) + ' --verbosity_level 0 --time_limit ' + str(args.time_limit) + ' --preprocessing ' + str(args.preprocessing) + ' --parameters_overlap ' + str(args.parameters_overlap) + ' --solver_type ' + str(args.solver_type)
      command = 'python3 main.py ' + command_arguments
      plan_status = os.popen(command).read()
      ls = plan_status.strip("\n").split("\n")
      for line in ls:
        if ("Encoding time" in line or "Solving time" in line or 'Preprocessing' in line or "Namespace" in line):
          print(line)
      if ("Plan found" in plan_status):
          print("Plan found for length: " + str(k))
          if (args.testing != 0 and args.run == 2):
            if ("Plan valid" in plan_status):
              print("Plan valid\n")
            else:
              print("Plan invalid! Error. <---------------------------------------\n")
          return 0
      else:
          print("Plan not found for length: " + str(k) + "\n")
          if ('Time out' in plan_status):
              print("Time out occured\n")
              return 1


# Main:
def run(args):
    # Checking if directory exists:
    if not Path(args.dir).is_dir():
      print("Invalid directory path: " + args.dir)
      exit
    files_list = glob.glob(args.dir + "*")
    files_list.sort(key=natural_keys)

    domain_filepath = args.dir + "domain.pddl"


    # Running each instances with time limit:
    for file_path in files_list:
        # Only considering problem files:
        if ('domain' not in file_path and '.py' not in file_path):
          timed_out = run_instance(domain_filepath, file_path, args)
          if (timed_out):
            continue