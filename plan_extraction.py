# Irfansha Shaik, 30.10.2020, Aarhus.

class ExtractPlan():

  def extract_action_based_plan(self, action_vars, constraints,k):
    for i in range(k):
      temp = ''
      for j in range(len(action_vars[i])):
        if self.sol_map[action_vars[i][j]] == -1:
          temp += '0'
        else:
          temp += '1'
      action_num = int(temp, 2)
      self.plan.append([constraints.action_list[action_num].name, tuple(constraints.action_list[action_num].parameters)])
      #print(constraints.action_list[action_num])

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
          break

  def print_plan(self):
    for action in self.plan:
      print(action)

  def __init__(self, sol_map):
    self.sol_map = sol_map
    self.plan = []
