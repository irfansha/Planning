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


def parse_file(file_path, output_dir, options, data_dict):
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


  if (opt1 in header_line and opt2 in header_line and opt3 in header_line and opt4 in header_line and opt5 in header_line):
    secondary_header = lines.pop(0)
    for line in lines:
      parsed_line = line.strip("\n").split(" ")
      if (parsed_line[-1] != 'TO'):
        data_dict[parsed_line[0]] = float(parsed_line[-1])


# Main:
if __name__ == '__main__':
  text = "Parses R files and plots required graphs"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--dir", help="directory path for parsed files", default = 'data/')
  parser.add_argument("--output_dir", help="output directory path for generated plots", default = 'parsed_data/')
  args = parser.parse_args()

  # versions we consider for plots:
  # [e, parameters_overlap, preprocessing, solver_type, t]
  #sat_options = ['SAT', '0', '0', '5', 'b']
  sat_options = ['M-seq', '0', '0', '5', 'b']
  #UG_options = ['UE', '0', '0', '2', 'b']
  UG_po_options = ['UE+', '1', '0', '2', 'b']
  UG_po_pre_options = ['UE+', '1', '2', '2', 'b']

  sat_solving_times = {}
  #UG_solving_times = []
  UG_po_solving_times = {}
  UG_po_pre_solving_times = {}


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
    parse_file(file_path, args.output_dir, sat_options, sat_solving_times)
    #UG_solving_times.extend(parse_file(file_path, args.output_dir, UG_options))
    parse_file(file_path, args.output_dir, UG_po_options, UG_po_solving_times)
    parse_file(file_path, args.output_dir, UG_po_pre_options, UG_po_pre_solving_times)

  All_instances_list = []


  # listing all instances:
  for line in sat_solving_times.keys():
    if (line not in All_instances_list):
      All_instances_list.append(line)

  for line in UG_po_solving_times.keys():
    if (line not in All_instances_list):
      All_instances_list.append(line)

  for line in UG_po_pre_solving_times.keys():
    if (line not in All_instances_list):
      All_instances_list.append(line)


  All_instances_dict = {}

  # Noting all the times:
  for instance in All_instances_list:
    if (instance not in sat_solving_times):
      sat = 6000
    else:
      sat = sat_solving_times[instance]
    if (instance not in UG_po_solving_times):
      ug_po = 6000
    else:
      ug_po = UG_po_solving_times[instance]
    if (instance not in UG_po_pre_solving_times):
      ug_po_pre = 6000
    else:
      ug_po_pre = UG_po_pre_solving_times[instance]
    All_instances_dict[instance] = [sat, ug_po, ug_po_pre]


  # Plotting M-SAT and UG_po_pre:
  # M-SAT on x axis and UG_po_pre on y axis:
  x_data = []
  y_data = []

  '''
  for key,value in All_instances_dict.items():
    # SAT is at position 0:
    x_data.append(value[0])
    # UG po pre is at position 2:
    y_data.append(value[2])
    if (value[0] >= value[2]):
      print(key, value)
  '''

  #'''
  for key,value in All_instances_dict.items():
    # UG pre is at position 2:
    x_data.append(value[2])
    # UG is at position 1:
    y_data.append(value[1])
  #'''

  plt.scatter(x_data, y_data, marker = '+')
  '''
  plt.xlabel("Time for M-simple (in sec) ")
  plt.ylabel("Time for UG-bloqqer-qdo (in sec)")
  '''
  plt.grid()
  #'''
  plt.xlabel("Time for UG-bloqqer-qdo (in sec) ")
  plt.ylabel("Time for UG (in sec)")
  #'''
  #plt.legend()
  plt.show()