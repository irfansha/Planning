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

def gen_new_arguments(domain, problem, k, args, file_name):
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
    elif( arg == "encoding_out"):
      new_command =  new_command + ' --encoding_out ' + args.encoding_out + "_" + file_name + "_" + str(k)
    elif( arg == "solver_out"):
      new_command = new_command + ' --solver_out ' + args.solver_out + "_" + file_name + "_" + str(k)
    elif(arg == "preprocessed_encoding_out"):
      new_command = new_command + ' --preprocessed_encoding_out ' + args.preprocessed_encoding_out + "_" + file_name + "_" + str(k)
    elif(arg == "plan_out"):
      new_command = new_command + ' --plan_out ' + args.plan_out + "_" + file_name + "_" + str(k)
    elif(arg == "encoding_intermediate_out"):
      new_command = new_command + ' --encoding_intermediate_out ' + args.encoding_intermediate_out + "_" + file_name + "_" + str(k)
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
      # Handing testcases with no solution:
      if (k >= 100):
        print("Large K\n")
        break
      k = k + args.step
      # Assuming linux system:
      problem_name = problem_filepath.split("/")
      file_name = problem_name[-1]
      file_name = file_name.strip(".pddl")
      # domain and problem files are new:
      command_arguments = gen_new_arguments(domain_filepath, problem_filepath, k, args, file_name)
      # command = 'python3 main.py -d ' + domain_filepath + ' -p ' + problem_filepath + ' -e ' + args.e + ' --run ' + str(args.run) + ' -k ' + str(k) + ' --testing ' + str(args.testing) + ' --verbosity_level 0 --time_limit ' + str(args.time_limit) + ' --preprocessing ' + str(args.preprocessing) + ' --parameters_overlap ' + str(args.parameters_overlap) + ' --solver_type ' + str(args.solver_type)
      command = 'python3 main.py ' + command_arguments
      plan_status = os.popen(command).read()
      ls = plan_status.strip("\n").split("\n")
      for line in ls:
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
          elif ('Memory out occurred' in plan_status):
              return 1


# Main:
def run(args):
    # Checking if directory exists:
    if not Path(args.dir).is_dir():
      print("Invalid directory path: " + args.dir)
      exit
    files_list = glob.glob(args.dir + "*")
    files_list.sort(key=natural_keys)

    for file_path in files_list:
      if ('domain' in file_path):
        domain_filepath = file_path
        break

    count = 0

    # Running each instances with time limit:
    for file_path in files_list:
        # We assume rest of the testcases are too big as well:
        if (count > 4):
          break
        # Only considering problem files:
        if ('domain' not in file_path and '.py' not in file_path):
          timed_out = run_instance(domain_filepath, file_path, args)
          if (timed_out):
            count = count + 1
            continue