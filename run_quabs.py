# Irfansha Shaik, 01.10.2020, Aarhus.

import os

class Quabs():

  def run(self):
    command = self.solver_path + " --partial-assignment " + self.input_file_path + " > " + self.output_file_path
    os.system(command)


  # parsing the qbf solver output (assuming quabs):
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

  def extract_plan(self, actions, action_vars):
    for step_actions in actions:
      for i in range(len(step_actions)):
        if self.sol_map[step_actions[i]] == 1:
          self.plan.append(action_vars[i])

  def print_plan(self):
    for action in self.plan:
      print(action)

  def __init__(self, input_file_path, output_file_path, solver_path):
    self.input_file_path = input_file_path
    self.output_file_path = output_file_path
    self.solver_path = solver_path
    self.sol_map = {}
    self.plan = []
    self.sat = -1 # sat value is never -1, either 1 or 0 for sat and unsat