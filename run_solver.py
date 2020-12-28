# Irfansha Shaik, 01.10.2020, Aarhus.

import subprocess


class RunSolver():

  def run(self):
    if (self.solver_type == 1):
      self.run_quabs()
      if not self.timed_out:
        self.parse_quabs_output()
    elif(self.solver_type == 2):
      self.run_caqe()
      if not self.timed_out:
        self.parse_caqe_output()
    else:
      print("Work in progress!")


  def run_quabs(self):
    command = self.solver_path + " --partial-assignment " + self.input_file_path + " > " + self.output_file_path
    try:
      subprocess.run([command], shell = True, timeout=self.time_limit)
    except subprocess.TimeoutExpired:
      self.timed_out = True
      print("Time out after " + str(self.time_limit)+ " seconds.")

  def run_caqe(self):
    command = self.solver_path + " --qdo " + self.input_file_path + " > " + self.output_file_path
    try:
      subprocess.run([command], shell = True, timeout=self.time_limit)
    except subprocess.TimeoutExpired:
      self.timed_out = True
      print("Time out after " + str(self.time_limit)+ " seconds.")

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
    result = lines.pop().strip("\n")
    if (result != 'c Unsatisfiable'):
      self.sat = 1
      if (self.plan_extract == 1):
        print("here")
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


  def __init__(self, input_file_path, output_file_path, solver_type, solver_path, time_limit, plan_extract):
    self.input_file_path = input_file_path
    self.output_file_path = output_file_path
    self.solver_type = solver_type
    self.time_limit = time_limit
    self.plan_extract = plan_extract
    # By default timeout not occured yet:
    self.timed_out = False
    if (self.solver_type == 1):
      self.solver_path = './solvers/qbf/quabs'
    elif(self.solver_type == 2):
      self.solver_path = './solvers/qbf/caqe'
    else:
      self.solver_path = solver_path
    self.sol_map = {}
    self.sat = -1 # sat value is never -1, either 1 or 0 for sat and unsat
