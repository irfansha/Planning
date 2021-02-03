# Irfansha Shaik, 29.01.2021, Aarhus.


import argparse, textwrap
import glob
import re
import os
from pathlib import Path



def atoi(text):
  return int(text) if text.isdigit() else text

def natural_keys(text):
  return [ atoi(c) for c in re.split(r'(\d+)', text) ]


def parse_file(file_path, output_dir):
  f = open(file_path, 'r')
  lines = f.readlines()
  f.close()
  header_line = lines.pop(0)

  # extracting the file name without whole path assuming linux:
  parsed_file_path = file_path.split("/")
  file_name = parsed_file_path[-1] + "_extract.R"

  # Opening out file in the out directory:
  f_out = open(output_dir + file_name, "w+")
  f_out.write("# " + header_line)

  encoding_time = 0
  solving_time = 0
  k = 0
  cur_testcase = ''
  time_out_flag = 0

  for line in lines:
    # Resetting for new testcase:
    if ("Running" in line):
      parsed_line = line.strip("\n").split(" ")
      # Writing previous testcase stats to file:
      if (len(cur_testcase) != 0):
        if (time_out_flag == 0):
          f_out.write( cur_testcase + " " + str(k) + " " + str(encoding_time) + " " + str(solving_time) + "\n")
        else:
          f_out.write( cur_testcase + " " + str(k) + " " + str(encoding_time) + " TO \n")
      else:
        f_out.write("Testcase k encoding_time solving_time\n")
      encoding_time = 0
      solving_time = 0
      time_out_flag = 0
      k = 0
      cur_testcase = parsed_line[-1]
    elif("Time out occured" in line):
      time_out_flag = 1
    elif ("Encoding time" in line):
      parsed_line = line.strip("\n").split(" ")
      if (time_out_flag == 0):
        encoding_time += float(parsed_line[-1])
    elif("Solving time" in line):
      parsed_line = line.strip("\n").split(" ")
      if (time_out_flag == 0):
        solving_time += float(parsed_line[-1])
    elif("Namespace" in line):
      parsed_line = line.strip("\n").split(", ")
      for parsed_option in parsed_line:
        if ('k=' in parsed_option):
          parsed_tokens = parsed_option.split("=")
          k = int(parsed_tokens[1])

  # Hanlding last testcase seperately:
  if (time_out_flag == 0):
    f_out.write( cur_testcase + " " + str(k) + " " + str(encoding_time) + " " + str(solving_time) + "\n")
  else:
    f_out.write( cur_testcase + " " + str(k) + " " + str(encoding_time) + " TO \n")


# Main:
if __name__ == '__main__':
  text = "Parses data files and generates R files"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--dir", help="directory path", default = 'data/')
  parser.add_argument("--output_dir", help="output directory path for generated R files", default = 'parsed_data/')
  args = parser.parse_args()

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
    parse_file(file_path, args.output_dir)