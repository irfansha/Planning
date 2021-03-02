# Irfansha Shaik, 02.03.2021, Aarhus.

import argparse, textwrap
import glob
import re
import os
from pathlib import Path



def atoi(text):
  return int(text) if text.isdigit() else text

def natural_keys(text):
  return [ atoi(c) for c in re.split(r'(\d+)', text) ]


def parse_files(files, output_dir, i, j, dir_names , solvers_data_paths):
  f = open(output_dir + "data_" + dir_names[i][:-1] + "_" + solvers_data_paths[i][j][:-1] + ".R", "w")
  valid_problems = []
  # First gathering the valid problems:
  for f_data in files:
    f_temp = open(f_data, "r")
    lines = f_temp.readlines()
    for line in lines:
      if (i == 0 and "Solution found" in line):
        valid_problems.append(f_data)
        break
      elif(i == 1 and "PLAN FOUND" in line):
        valid_problems.append(f_data)
        break
      elif(i == 2 and "Plan found" in line):
        valid_problems.append(f_data)
        break

  #print(valid_problems)
  for f_data in files:
    if ("problem" not in f_data):
      stats_file = open(f_data, "r")
      stats_lines = stats_file.readlines()
      wall_time = 0
      cpu_time = 0
      max_mem = 0
      cur_instance = ''

      for line in stats_lines:
        parsed_line = line.strip("\n").split(" ")
        #print(parsed_line)
        # reset everything after printing:
        if ("------" in line):
          for valid_prob in valid_problems:
            parsed_valid_prob = valid_prob.split("_")
            if (parsed_valid_prob[-2] in cur_instance):
              f.write(cur_instance + " " + wall_time + " " + cpu_time + " " + max_mem + "\n")
          wall_time = 0
          cpu_time = 0
          max_mem = 0
          cur_instance = ''
        elif("Name" in line):
            cur_instance = parsed_line[-1]
        elif("walltime" in line):
            wall_time = parsed_line[-1]
        elif("CPU time" in line):
            cpu_time = parsed_line[-1]
        elif("Max Mem" in line):
            max_mem = parsed_line[-2]

  f.close()

# Main:
if __name__ == '__main__':
  text = "Parses data files and generates R files"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--dir", help="directory path", default = 'data/')
  parser.add_argument("--output_dir", help="output directory path for generated R files", default = 'parsed_data/')
  args = parser.parse_args()

  solvers_data_paths = [["out_FDS_alkene_data/", "out_FDS_mitexams_data/", "out_FDS_opt18_data/", "out_FDS_sat18_data/"],
                        ["out_M-final_alkene/", "out_M-final_mitexams/", "out_M-final_opt18/", "out_M-final_sat18/"],
                        ["out_alkene_data/", "out_mitexams_data/", "out_opt18_data/", "qdo_data/"]]

  dir_names = ["FDS_data/", "M-final_data/", "UE_organic_synthesis_data/"]

  # Checking if out directory exits:
  if not Path(args.output_dir).is_dir():
    print("Invalid directory path: " + args.output_dir)
    print("Creating new directory with same path.")
    os.mkdir(args.output_dir)


  # Looping through three solvers data:
  for i in range(0,3):
    for j in range(0,4):
      solver_path = args.dir + dir_names[i] + solvers_data_paths[i][j]

      # Checking if directory exists:
      if not Path(args.dir).is_dir():
        print("Invalid directory path: " + solver_path)
        exit
      files_list = glob.glob(solver_path + "*")
      files_list.sort(key=natural_keys)
      #print(files_list)

      parse_files(files_list, args.output_dir, i, j, dir_names, solvers_data_paths)