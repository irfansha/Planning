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

  def extract_qr_plan(self, states, constraints, n, k):
    current_states = []
    for i in range(k+1):
      temp_pos_var = []
      temp_neg_var = []
      for j in range(n):
        if self.sol_map[states[i][j]] == 1:
          temp_pos_var.append(constraints.state_vars[j])
        else:
          temp_neg_var.append(constraints.state_vars[j])
      current_states.append([temp_pos_var, temp_neg_var])
    for i in range(k):
      for action in constraints.action_list:
        valid_action = 1
        current_state = [list(current_states[i][0]), list(current_states[i][1])]
        # precondition must satisfy:
        for pos_pre_cond in action.positive_preconditions:
          if pos_pre_cond not in current_state[0]:
            valid_action = 0
            break
        for neg_pre_cond in action.negative_preconditions:
          if neg_pre_cond not in current_state[1]:
            valid_action = 0
            break
        # applying action current state:
        for add_state in action.add_effects:
          if add_state not in current_state[0]:
            current_state[0].append(add_state)
          if add_state in current_state[1]:
            current_state[1].remove(add_state)
        for del_state in action.del_effects:
          if del_state not in current_state[1]:
            current_state[1].append(del_state)
          if del_state in current_state[0]:
            current_state[0].remove(del_state)
        current_state[0].sort()
        current_state[1].sort()
        if (current_state != current_states[i+1]):
          valid_action = 0
        if (valid_action):
          self.plan.append([action.name, tuple(action.parameters)])

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
