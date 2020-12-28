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

  def extract_ungrounded_plan(self, action_vars, constraints, k):
    for action_step in action_vars:
      for i in range(len(action_step)):
        if (action_step[i][0] in self.sol_map):
          if (self.sol_map[action_step[i][0]] == 1):
            action_name = constraints.action_vars[i][0]
            base_action_parameters = constraints.action_vars[i][1]
            action_parameters = action_step[i][1]
            # print(action_name, action_parameters)
            obj_parameter_list = []
            for j in range(len(action_parameters)):
              parameter = action_parameters[j]
              base_parameter = base_action_parameters[j]
              base_parameter_type = base_parameter[1]
              temp = ''
              for obj_i in range(len(parameter)):
                if parameter[obj_i] in self.sol_map:
                  if self.sol_map[parameter[obj_i]] == -1:
                    temp += '0'
                  else:
                    temp += '1'
                else:
                  temp += '0'
              obj_num = int(temp, 2)
              obj_parameter_list.append(constraints.updated_objects[base_parameter_type][obj_num])
            self.plan.append([action_name, tuple(obj_parameter_list)])

  def extract_qr_plan(self, states, constraints, k):
    n = constraints.num_state_vars
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

  def print_updated_plan(self):
    for action in self.updated_format_plan:
      print(action)

  def print_to_file(self):
    f = open(self.file_path, 'w')
    for step_plan in self.updated_format_plan:
      f.write( step_plan + '\n')

  def update_format(self):
    count = 0
    for i in range(len(self.plan)):
      if (self.plan[i][0] != 'noop'):
        step_plan = self.plan[i]
        temp_string = str(count) + ': (' + step_plan[0] + ' '
        temp_list_string = ' '.join(list(step_plan[1]))
        self.updated_format_plan.append(temp_string + temp_list_string + ')')
        count += 1

  def __init__(self, sol_map, file_path):
    self.sol_map = sol_map
    self.file_path = file_path
    self.plan = []
    self.updated_format_plan = []
