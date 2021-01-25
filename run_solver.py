# Irfansha Shaik, 01.10.2020, Aarhus.

import subprocess


class RunSolver():

  def run(self):
    if (self.solver_type == 1):
      self.run_quabs()
      if not self.timed_out:
        self.parse_quabs_output()
    elif(self.solver_type == 2):
      self.run_caqe(self.input_file_path)
      if not self.timed_out:
        self.parse_caqe_output()
        if (self.preprocessing == 1 and self.sat != 0 and self.plan_extract == 2):
          self.generate_encoding_with_solution()
          self.run_caqe(self.preprocessed_extraction_file)
          self.parse_caqe_output()
    elif(self.solver_type == 3):
      self.run_depqbf()
      if not self.timed_out:
        self.parse_depqbf_output()
    elif(self.solver_type == 4):
      self.change_to_dimacs()
      self.run_minisat()
      if not self.timed_out:
        self.parser_minisat_output()
    else:
      print("Work in progress!")



  def run_quabs(self):
    command = self.solver_path + " --partial-assignment " + self.input_file_path + " > " + self.output_file_path
    try:
      subprocess.run([command], shell = True, timeout=self.time_limit)
    except subprocess.TimeoutExpired:
      self.timed_out = True
      print("Time out after " + str(self.time_limit)+ " seconds.")

  def run_caqe(self, input_file_path):
    if (self.preprocessing == 2):
      assert(self.plan_extract != 2)
      command = self.solver_path + " --preprocessor bloqqer " + input_file_path + " > " + self.output_file_path
    else:
      command = self.solver_path + " --qdo --dependency-schemes " + str(self.dependency_schemes) + " " + input_file_path + " > " + self.output_file_path
    try:
      subprocess.run([command], shell = True, timeout=self.time_limit)
    except subprocess.TimeoutExpired:
      self.timed_out = True
      print("Time out after " + str(self.time_limit)+ " seconds.")

  def run_depqbf(self):
    command = self.solver_path + " --qdo --no-dynamic-nenofex " + self.input_file_path + " > " + self.output_file_path
    try:
      subprocess.run([command], shell = True, timeout=self.time_limit)
    except subprocess.TimeoutExpired:
      self.timed_out = True
      print("Time out after " + str(self.time_limit)+ " seconds.")

  def run_minisat(self):
    command = self.solver_path + " " + self.input_file_path + " " + self.output_file_path
    try:
      subprocess.run([command], shell = True, timeout=self.time_limit)
    except subprocess.TimeoutExpired:
      self.timed_out = True
      print("Time out after " + str(self.time_limit)+ " seconds.")



  def change_to_dimacs(self):
    f = open(self.input_file_path, 'r')
    lines = f.readlines()
    f.close()

    # replacing lines without beginning e:
    print(lines[1][:2])
    assert("e " == lines[1][:2])
    lines[1] = lines[1][2:-1]
    assert("e " == lines[2][:2])
    lines[2] = lines[2][2:]
    lines[1] = lines[1]+lines[2]

    f = open(self.input_file_path, 'w')
    for i in range(len(lines)):
      if (i != 2):
        f.write(lines[i])
    f.close()

  def generate_encoding_with_solution(self):
    #print(self.sol_map)
    f_read = open(self.unpreprocessed_input_file_path, 'r')
    lines = f_read.readlines()
    f_read.close()

    split_line = lines[0].strip("\n").split(" ")


    exists_vars = lines[1]

    split_exists_vars = exists_vars.split(" ")

    count = 0

    for var, value in self.sol_map.items():
      if (str(var) in split_exists_vars):
        count = count + 1

    # Updating clause count:
    # ----------------------------------------------------------------
    split_line[3] = str(int(split_line[3]) + count)

    joined_line = ' '.join(split_line)

    lines[0] = joined_line + "\n"
    # ----------------------------------------------------------------

    #print(exists_vars)

    #print(split_exists_vars)

    f_write = open(self.preprocessed_extraction_file, 'w+')

    for line in lines:
      # Avoiding empty line:
      if (line != "\n"):
        f_write.write(line)

    for var, value in self.sol_map.items():
      if (str(var) in split_exists_vars):
        if value > 0:
          clause = str(var) + " 0\n"
        else:
          clause = str(-var) + " 0\n"
        f_write.write(clause)

    f_write.close()




  # parsing the quabs solver output:
  def parse_quabs_output(self):
    f = open(self.output_file_path, 'r')
    lines = f.readlines()
    result = lines.pop(0).strip("\n")
    if (result != 'r UNSAT'):
      self.sat = 1
      literals = result.split(" ")
      literals.pop()
      literals.pop(0)
      for literal in literals:
        if int(literal) > 0:
          self.sol_map[int(literal)] = 1
        else:
          self.sol_map[-int(literal)] = -1
    else:
      self.sat = 0

  # parsing the caqe solver output:
  def parse_caqe_output(self):
    f = open(self.output_file_path, 'r')
    lines = f.readlines()
    lines.pop(0)
    early_result = lines.pop(0)
    if ('c Unsatisfiable' in early_result):
      self.sat = 0
      return
    elif ('c Satisfiable' in early_result and self.plan_extract == 1):
      self.sat = 1
      return
    result = lines.pop().strip("\n")
    if (result != 'c Unsatisfiable'):
      self.sat = 1
      if (self.plan_extract == 1):
        return
      for line in lines:
        temp = line.split(" ")
        if (temp != ['\n']):
          literal = temp[1]
          if int(literal) > 0:
            self.sol_map[int(literal)] = 1
          else:
            self.sol_map[-int(literal)] = -1
    else:
      self.sat = 0

  # parsing the caqe solver output:
  def parse_depqbf_output(self):
    f = open(self.output_file_path, 'r')
    lines = f.readlines()
    header = lines.pop(0)
    parsed_header = header.split(" ")
    if (parsed_header[2] == '0'):
      self.sat = 0
      return
    else:
      self.sat = 1
      if (self.plan_extract == 1):
        return
      for line in lines:
        temp = line.split(" ")
        if (temp != ['\n']):
          literal = temp[1]
        if int(literal) > 0:
          self.sol_map[int(literal)] = 1
        else:
          self.sol_map[-int(literal)] = -1


  def parser_minisat_output(self):
    f = open(self.output_file_path, 'r')
    lines = f.readlines()
    header = lines.pop(0)
    if (header != "SAT\n"):
      self.sat = 0
    else:
      self.sat = 1
      assignment = lines.pop(0)
      vars = assignment.split(" ")
      vars.pop()
      for var in vars:
        literal = var
        if int(literal) > 0:
          self.sol_map[int(literal)] = 1
        else:
          self.sol_map[-int(literal)] = -1

  def __init__(self, args):
    if (args.preprocessing != 1):
      self.input_file_path = args.encoding_out
    else:
      self.input_file_path = args.preprocessed_encoding_out
      self.preprocessed_extraction_file = './intermediate_files/encoding_with_preprocessed_solution'
    self.unpreprocessed_input_file_path = args.encoding_out
    self.output_file_path = args.solver_out
    self.solver_type = args.solver_type
    self.time_limit = args.time_limit
    self.plan_extract = args.run
    self.preprocessing = args.preprocessing
    self.dependency_schemes = args.dependency_schemes
    # By default timeout not occured yet:
    self.timed_out = False
    if (self.solver_type == 1):
      self.solver_path = './solvers/qbf/quabs'
    elif(self.solver_type == 2):
      self.solver_path = './solvers/qbf/caqe'
    elif(self.solver_type == 3):
      self.solver_path = './solvers/qbf/depqbf'
    elif(self.solver_type == 4):
      self.solver_path = './solvers/sat/MiniSat_v1.14_linux'
    self.sol_map = {}
    self.sat = -1 # sat value is never -1, either 1 or 0 for sat and unsat
