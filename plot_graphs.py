# Irfansha Shaik, 03.02.2021, Aarhus

import argparse, textwrap
import glob
import re
import os
from pathlib import Path
import collections
import matplotlib.pyplot as plt



def atoi(text):
  return int(text) if text.isdigit() else text

def natural_keys(text):
  return [ atoi(c) for c in re.split(r'(\d+)', text) ]


def parse_file(file_path, output_dir, options):
  f = open(file_path, 'r')
  lines = f.readlines()
  f.close()

  # Checking if the file has same options:
  flag = 0

  header_line = lines.pop(0)
  opt1 = "e='" + options[0] + "'"
  opt2 = "parameters_overlap=" + options[1]
  opt3 = "preprocessing=" + options[2]
  opt4 = "solver_type=" + options[3]
  opt5 = "t='" + options[4] +"'"

  temp_solving_times = []

  if (opt1 in header_line and opt2 in header_line and opt3 in header_line and opt4 in header_line and opt5 in header_line):
    secondary_header = lines.pop(0)
    for line in lines:
      parsed_line = line.strip("\n").split(" ")
      if (parsed_line[-1] != 'TO'):
        temp_solving_times.append(float(parsed_line[-1]))
    return temp_solving_times
  else:
    return []


# Main:
if __name__ == '__main__':
  text = "Parses R files and plots required graphs"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--dir", help="directory path for parsed files", default = 'data/')
  parser.add_argument("--output_dir", help="output directory path for generated plots", default = 'parsed_data/')
  args = parser.parse_args()

  # versions we consider for plots:
  # [e, parameters_overlap, preprocessing, solver_type, t]
  sat_options = ['SAT', '0', '0', '5', 'b']
  UG_options = ['UE', '0', '0', '2', 'b']
  UG_po_pre_options = ['UE', '1', '1', '2', 'b']

  sat_solving_times = []
  UG_solving_times = []
  UG_po_pre_solving_times = []


  # Checking if directory exists:
  if not Path(args.dir).is_dir():
    print("Invalid directory path: " + args.dir)
    exit
  files_list = glob.glob(args.dir + "*")
  files_list.sort(key=natural_keys)

  # Checking if out directory exits:
  if not Path(args.output_dir).is_dir():
    print("Invalid directory path: " + args.output_dir)
    print("Creating new directory with same path.")
    os.mkdir(args.output_dir)

  # Parsing each file seperately:
  for file_path in files_list:
    sat_solving_times.extend(parse_file(file_path, args.output_dir, sat_options))
    UG_solving_times.extend(parse_file(file_path, args.output_dir, UG_options))
    UG_po_pre_solving_times.extend(parse_file(file_path, args.output_dir, UG_po_pre_options))


  # Gathering SAT data:
  sat_solving_times.sort()

  SAT_c = collections.Counter(sat_solving_times)
  SAT_solved_cases = []
  SAT_solved_times = []
  count = 0
  for key,value in SAT_c.items():
    SAT_solved_times.append(key)
    count += value
    SAT_solved_cases.append(count)

  # Gathering UG data:
  UG_solving_times.sort()

  UG_c = collections.Counter(UG_solving_times)
  UG_solved_cases = []
  UG_solved_times = []
  count = 0
  for key,value in UG_c.items():
    UG_solved_times.append(key)
    count += value
    UG_solved_cases.append(count)

  # Gathering UG with parameters overlap and preprocessing data:
  UG_po_pre_solving_times.sort()

  UG_po_pre_c = collections.Counter(UG_po_pre_solving_times)
  UG_po_pre_solved_cases = []
  UG_po_pre_solved_times = []
  count = 0
  for key,value in UG_po_pre_c.items():
    UG_po_pre_solved_times.append(key)
    count += value
    UG_po_pre_solved_cases.append(count)

  max_solved_cases = max(max(SAT_solved_cases), max(UG_solved_cases), max(UG_po_pre_solved_cases))
  max_solving_time = max(max(SAT_solved_times), max(UG_solved_times), max(UG_po_pre_solved_times))

  plt.plot(SAT_solved_cases, SAT_solved_times,marker='.', color='b', label = 'SAT')
  plt.plot(UG_solved_cases, UG_solved_times,marker='.', color='r', label = 'UG')
  plt.plot(UG_po_pre_solved_cases, UG_po_pre_solved_times, marker='.', color='k', label = 'UG_po_pre')
  plt.show()