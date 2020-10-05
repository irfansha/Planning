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

  # XXX not complete yet
  def extract_qr_plan(self, states, constraints, n, k):
    for i in range(k):
      temp_plan = []
      add_effects = []
      del_effects = []
      for j in range(n):
        if (self.sol_map[states[i][j]] != self.sol_map[states[i+1][j]]):
          if (self.sol_map[states[i][j]] == 1 and self.sol_map[states[i+1][j]] == -1):
            del_effects.append(constraints.state_vars[j])
          else:
            add_effects.append(constraints.state_vars[j])
      for action in constraints.action_list:
        valid_action = 1
        for pre_neg in action.negative_preconditions:
          var_index = constraints.state_vars.index(pre_neg)
          #if states[i][var_index] in self.sol_map:
          if self.sol_map[states[i][var_index]] == 1:
            valid_action = 0
            break
        for pre_pos in action.positive_preconditions:
          var_index = constraints.state_vars.index(pre_pos)
          #if states[i][var_index] in self.sol_map:
          if self.sol_map[states[i][var_index]] == -1:
            valid_action = 0
            break
        # XXX plan extract not complete:
        for pos_pos in action.add_effects:
          var_index = constraints.state_vars.index(pos_pos)
          #if states[i][var_index] in self.sol_map:
          if self.sol_map[states[i][var_index]] == -1:
            valid_action = 0
            break
        for pos_neg in action.del_effects:
          var_index = constraints.state_vars.index(pos_neg)
          #if states[i][var_index] in self.sol_map:
          if self.sol_map[states[i][var_index]] == 1:
            valid_action = 0
            break
        for add_effect in add_effects:
          if add_effect not in action.add_effects:
            valid_action = 0
            break
        for del_effect in del_effects:
          if del_effect not in action.del_effects:
            valid_action = 0
            break
        if (valid_action):
          temp_plan = (action.name, tuple(action.parameters))
          self.plan.append(temp_plan)
          break

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
