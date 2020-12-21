# Irfansha Shaik, 15.11.2020, Aarhus

from variable_dispatcher import VarDispatcher as vd
from pddl import PDDL_Parser
import copy
import math

class UngroundedEncoding():

  def test_predicate(self, predicate, predicate_type_list, obj_dict, state):
    if (len(predicate_type_list) + 1 == len(state)):
      temp_name = state[0]
      for i in range(len(predicate_type_list)):
        if (state[i+1] not in obj_dict[predicate_type_list[i]]):
          return False
        else:
          temp_name += '_' + predicate_type_list[i]
      if (predicate == temp_name):
        return True
      else:
        return False
    else:
      return False

  def generate_initial_gate(self, constraints_extract, splitvars_flag):
    self.encoding.append(['# Initial gate:'])
    base_predicates = list(constraints_extract.predicates)
    temp_initial_gate = []
    initial_state = constraints_extract.initial_state
    # For zero-arg predicates:
    if 0 in constraints_extract.predicate_dict.keys():
      self.encoding.append(['# Zero predicate gates:'])
      zero_predicates = constraints_extract.predicate_dict[0]
      zero_then_gate = []
      for predicate in zero_predicates:
        if [predicate] in initial_state:
          zero_then_gate.append(self.predicates[0][base_predicates.index(predicate)])
        else:
          zero_then_gate.append(-self.predicates[0][base_predicates.index(predicate)])

      if (splitvars_flag == 1):
        zero_if_gate = []
        for var in self.split_forall_vars:
          zero_if_gate.append(-var)
        [if_output_gate] = self.var_dis.get_vars(1)
        self.encoding.append(['and', if_output_gate, zero_if_gate])

      [then_output_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['and', then_output_gate, zero_then_gate])
      [if_then_output_gate] = self.var_dis.get_vars(1)

      # Only if spplit variable are present, we consider if block:
      if (splitvars_flag == 1):
        self.encoding.append(['or', if_then_output_gate, [-if_output_gate, then_output_gate]])
      else:
        self.encoding.append(['and', if_then_output_gate, [then_output_gate]])
      temp_initial_gate.append(if_then_output_gate)

    for i in range(1, constraints_extract.max_predicate_args+1):
      step_all_predicate_gates = []
      if i in constraints_extract.predicate_dict.keys():
        self.encoding.append(['# Step ' + str(i) + ' predicate gates:'])
        for predicate in constraints_extract.predicate_dict[i]:
          predicate_type_list = list(constraints_extract.predicates[predicate].values())
          param_list = []
          for state in constraints_extract.base_initial_state:
            if (self.test_predicate(predicate, predicate_type_list, constraints_extract.updated_objects, state)):
              param_list.append(state[1:])
          temp_forall_vars_map = copy.deepcopy(self.forall_vars_map)
          predicate_forall_vars = []
          for predicate_type in predicate_type_list:
            temp_forall_vars = temp_forall_vars_map[predicate_type].pop(0)
            predicate_forall_vars.append(temp_forall_vars)
          param_list_gate = []
          for param in param_list:
            param_gate = []
            for j in range(len(param)):
              obj_position = constraints_extract.updated_objects[predicate_type_list[j]].index(param[j])
              bin_string = format(obj_position,'0' + str(len(predicate_forall_vars[j])) + 'b')
              temp_condition = []
              for k in range(len(predicate_forall_vars[j])):
                if bin_string[k] == '0':
                  temp_condition.append(-predicate_forall_vars[j][k])
                else:
                  temp_condition.append(predicate_forall_vars[j][k])
              [temp_condition_gate] = self.var_dis.get_vars(1)
              self.encoding.append(['and', temp_condition_gate, temp_condition])
              param_gate.append(temp_condition_gate)
              #print(param[j], obj_position, predicate_forall_vars[j], temp_condition)
            [param_output_gate] = self.var_dis.get_vars(1)
            self.encoding.append(['and', param_output_gate, param_gate])
            #print(param_gate, param)
            param_list_gate.append(param_output_gate)
          if len(param_list_gate) == 0:
            step_all_predicate_gates.append(-self.predicates[0][base_predicates.index(predicate)])
          else:
            [param_list_output_gate] = self.var_dis.get_vars(1)
            self.encoding.append(['or', param_list_output_gate, param_list_gate])
            # If the param list output gate is true then predicate holds, else not:
            [if_param_list_true_gate] = self.var_dis.get_vars(1)
            [if_param_list_false_gate] = self.var_dis.get_vars(1)
            cur_predicate_var = self.predicates[0][base_predicates.index(predicate)]
            self.encoding.append(['or', if_param_list_true_gate, [-param_list_output_gate, cur_predicate_var]])
            self.encoding.append(['or', if_param_list_false_gate, [param_list_output_gate, -cur_predicate_var]])
            step_all_predicate_gates.append(if_param_list_true_gate)
            step_all_predicate_gates.append(if_param_list_false_gate)
        [step_then_output_gate] = self.var_dis.get_vars(1)
        self.encoding.append(['and', step_then_output_gate, step_all_predicate_gates])
        if (splitvars_flag == 1):
          bin_string = format(i,'0' + str(len(self.split_forall_vars)) + 'b')
          temp_condition = []
          for k in range(len(self.split_forall_vars)):
            if bin_string[k] == '0':
              temp_condition.append(-self.split_forall_vars[k])
            else:
              temp_condition.append(self.split_forall_vars[k])
          [step_if_output_gate] = self.var_dis.get_vars(1)
          self.encoding.append(['and', step_if_output_gate, temp_condition])
        [step_if_then_output_gate] = self.var_dis.get_vars(1)
        # Same as above, if condition is only considered if splitvars are used:
        if (splitvars_flag == 1):
          self.encoding.append(['or', step_if_then_output_gate, [-step_if_output_gate,step_then_output_gate]])
        else:
          self.encoding.append(['and', step_if_then_output_gate, [step_then_output_gate]])
        temp_initial_gate.append(step_if_then_output_gate)
    # Generating initial gate variable:
    [self.initial_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['and', self.initial_output_gate, temp_initial_gate])

  def generate_goal_gate(self, constraints_extract, goal_step, splitvars_flag):
    self.encoding.append(['# Goal gate:'])
    base_predicates = list(constraints_extract.predicates)
    temp_goal_gate = []
    goal_state = constraints_extract.goal_state
    #print(goal_state)
    # For zero-arg predicates:
    if 0 in constraints_extract.predicate_dict.keys():
      self.encoding.append(['# Zero predicate gates:'])
      zero_predicates = constraints_extract.predicate_dict[0]
      zero_then_gate = []
      for predicate in zero_predicates:
        if [predicate] in goal_state[0]:
          zero_then_gate.append(self.predicates[goal_step][base_predicates.index(predicate)])
        elif [predicate] in goal_state[1]:
          zero_then_gate.append(-self.predicates[goal_step][base_predicates.index(predicate)])

      if (splitvars_flag == 1):
        zero_if_gate = []
        for var in self.split_forall_vars:
          zero_if_gate.append(-var)
        [if_output_gate] = self.var_dis.get_vars(1)
        self.encoding.append(['and', if_output_gate, zero_if_gate])

      [then_output_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['and', then_output_gate, zero_then_gate])
      [if_then_output_gate] = self.var_dis.get_vars(1)

      # Only if spplit variable are present, we consider if block:
      if (splitvars_flag == 1):
        self.encoding.append(['or', if_then_output_gate, [-if_output_gate, then_output_gate]])
      else:
        self.encoding.append(['and', if_then_output_gate, [then_output_gate]])
      temp_goal_gate.append(if_then_output_gate)

    for i in range(1, constraints_extract.max_predicate_args+1):
      step_all_predicate_gates = []
      if i in constraints_extract.predicate_dict.keys():
        self.encoding.append(['# Step ' + str(i) + ' predicate gates:'])
        for predicate in constraints_extract.predicate_dict[i]:
          predicate_type_list = list(constraints_extract.predicates[predicate].values())
          pos_param_list = []
          neg_param_list = []
          for state in constraints_extract.base_goal_state[0]:
            if (self.test_predicate(predicate, predicate_type_list, constraints_extract.updated_objects, state)):
              pos_param_list.append(state[1:])
          # Handling negative goals:
          for state in constraints_extract.base_goal_state[1]:
            if (self.test_predicate(predicate, predicate_type_list, constraints_extract.updated_objects, state)):
              neg_param_list.append(state[1:])
          temp_forall_vars_map = copy.deepcopy(self.forall_vars_map)
          predicate_forall_vars = []
          predicate_type_list = list(constraints_extract.predicates[predicate].values())
          for predicate_type in predicate_type_list:
            temp_forall_vars = temp_forall_vars_map[predicate_type].pop(0)
            predicate_forall_vars.append(temp_forall_vars)
          pos_param_list_gate = []
          neg_param_list_gate = []
          for param in pos_param_list:
            param_gate = []
            for j in range(len(param)):
              obj_position = constraints_extract.updated_objects[predicate_type_list[j]].index(param[j])
              bin_string = format(obj_position,'0' + str(len(predicate_forall_vars[j])) + 'b')
              temp_condition = []
              for k in range(len(predicate_forall_vars[j])):
                if bin_string[k] == '0':
                  temp_condition.append(-predicate_forall_vars[j][k])
                else:
                  temp_condition.append(predicate_forall_vars[j][k])
              [temp_condition_gate] = self.var_dis.get_vars(1)
              self.encoding.append(['and', temp_condition_gate, temp_condition])
              param_gate.append(temp_condition_gate)
              #print(param[j], obj_position, predicate_forall_vars[j], temp_condition)
            [param_output_gate] = self.var_dis.get_vars(1)
            self.encoding.append(['and', param_output_gate, param_gate])
            #print(param_gate, param)
            pos_param_list_gate.append(param_output_gate)
          for param in neg_param_list:
            param_gate = []
            for j in range(len(param)):
              obj_position = constraints_extract.updated_objects[predicate_type_list[j]].index(param[j])
              bin_string = format(obj_position,'0' + str(len(predicate_forall_vars[j])) + 'b')
              temp_condition = []
              for k in range(len(predicate_forall_vars[j])):
                if bin_string[k] == '0':
                  temp_condition.append(-predicate_forall_vars[j][k])
                else:
                  temp_condition.append(predicate_forall_vars[j][k])
              [temp_condition_gate] = self.var_dis.get_vars(1)
              self.encoding.append(['and', temp_condition_gate, temp_condition])
              param_gate.append(temp_condition_gate)
              #print(param[j], obj_position, predicate_forall_vars[j], temp_condition)
            [param_output_gate] = self.var_dis.get_vars(1)
            self.encoding.append(['and', param_output_gate, param_gate])
            #print(param_gate, param)
            neg_param_list_gate.append(param_output_gate)
          if len(pos_param_list_gate) != 0:
            [pos_param_list_output_gate] = self.var_dis.get_vars(1)
            self.encoding.append(['or', pos_param_list_output_gate, pos_param_list_gate])
            [if_param_list_pos_gate] = self.var_dis.get_vars(1)
            cur_predicate_var = self.predicates[goal_step][base_predicates.index(predicate)]
            self.encoding.append(['or', if_param_list_pos_gate, [-pos_param_list_output_gate, cur_predicate_var]])
            step_all_predicate_gates.append(if_param_list_pos_gate)
          if len(neg_param_list_gate) != 0:
            [neg_param_list_output_gate] = self.var_dis.get_vars(1)
            self.encoding.append(['or', neg_param_list_output_gate, neg_param_list_gate])
            [if_param_list_neg_gate] = self.var_dis.get_vars(1)
            cur_predicate_var = self.predicates[goal_step][base_predicates.index(predicate)]
            self.encoding.append(['or', if_param_list_neg_gate, [-neg_param_list_output_gate, -cur_predicate_var]])
            step_all_predicate_gates.append(if_param_list_neg_gate)
        [step_then_output_gate] = self.var_dis.get_vars(1)
        self.encoding.append(['and', step_then_output_gate, step_all_predicate_gates])

        if (splitvars_flag == 1):
          bin_string = format(i,'0' + str(len(self.split_forall_vars)) + 'b')
          temp_condition = []
          for k in range(len(self.split_forall_vars)):
            if bin_string[k] == '0':
              temp_condition.append(-self.split_forall_vars[k])
            else:
              temp_condition.append(self.split_forall_vars[k])
          [step_if_output_gate] = self.var_dis.get_vars(1)
          self.encoding.append(['and', step_if_output_gate, temp_condition])
        [step_if_then_output_gate] = self.var_dis.get_vars(1)
        # Same as above, if condition is only considered if splitvars are used:
        if (splitvars_flag == 1):
          self.encoding.append(['or', step_if_then_output_gate, [-step_if_output_gate,step_then_output_gate]])
        else:
          self.encoding.append(['and', step_if_then_output_gate, [step_then_output_gate]])
        temp_goal_gate.append(step_if_then_output_gate)

    # Generating goal gate variable:
    [self.goal_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['and', self.goal_output_gate, temp_goal_gate])



  def generate_k_transitions(self, tfun, k):
    # Generating transition function for each step:
    for i in range(k):
      # Generating auxilary vars:
      step_aux_vars = self.var_dis.get_vars(tfun.num_aux_vars)
      # Appending transition output gates:
      self.transition_step_output_gates.append(step_aux_vars[-1])

      tfun.gates_gen.new_gate_gen(self.encoding, 'S_' + str(i), 'S_' + str(i+1), self.predicates[i], self.predicates[i+1], self.action_with_parameter_vars[i], self.forall_vars, self.split_forall_vars, step_aux_vars)


  def generate_final_gate(self):
    temp_final_list = []
    temp_final_list.append(self.initial_output_gate)
    temp_final_list.append(-self.if_existential_output_gate)
    temp_final_list.append(self.final_transition_gate)
    #temp_final_list.extend(self.transition_step_output_gates)
    temp_final_list.append(self.goal_output_gate)
    self.encoding.append(['# Final gate:'])

    # Generating final gate variable:
    [self.final_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['and', self.final_output_gate, temp_final_list])

  def generate_quantifier_blocks(self, k, splitvars_flag):
    self.quantifier_block.append(['# Action variables :'])
    for i in range(k):
      self.quantifier_block.append(['# Time step' + str(i) + ' :'])
      for action_vars in self.action_with_parameter_vars[i]:
        main_action_var = action_vars[0]
        self.quantifier_block.append(['# Main action variable :'])            # XXX add name directly later
        self.quantifier_block.append(['exists(' + str(main_action_var) + ')'])
        action_parameters = action_vars[1]
        self.quantifier_block.append(['# Parameter variables :'])
        for parameter in action_parameters:
          self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in parameter) + ')'])
    self.quantifier_block.append(['# Split forall variables :'])
    if (splitvars_flag == 1):
      self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in self.split_forall_vars) + ')'])
    else:
      self.quantifier_block.append(['# forall(' + ', '.join(str(x) for x in self.split_forall_vars) + ')'])
    self.quantifier_block.append(['# Object forall variables :'])
    for obj_type_vars in self.forall_vars:
      for obj_vars in obj_type_vars:
        self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in obj_vars) + ')'])

    self.quantifier_block.append(['# Predicate variables :'])

    for i in range(k+1):
      self.quantifier_block.append(['# Time step' + str(i) + ' :'])
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.predicates[i]) + ')'])


  def print_gate(self, gate):
    if len(gate) == 1:
      print(gate[0])
    else:
      print(str(gate[1]) + ' = ' + gate[0] + '(' + ', '.join(str(x) for x in gate[2]) + ')')

  def print_gate_tofile(self, gate, f):
    if len(gate) == 1:
      f.write(gate[0] + '\n')
    else:
      f.write(str(gate[1]) + ' = ' + gate[0] + '(' + ', '.join(str(x) for x in gate[2]) + ') \n')

  def print_encoding_tofile(self, file_path):
    f = open(file_path, 'w')
    for gate in self.quantifier_block:
      self.print_gate_tofile(gate, f)
    f.write('output(' + str(self.final_output_gate) + ') \n')
    for gate in self.encoding:
      self.print_gate_tofile(gate, f)

  def print_encoding(self):
    for gate in self.quantifier_block:
      self.print_gate(gate)
    print('output(' + str(self.final_output_gate) + ')')
    for gate in self.encoding:
      self.print_gate(gate)

  # Generating k sets of action vars for k steps:
  def gen_action_with_parameter_vars(self, object_type_dict, action_vars, tfun, k):
    for i in range(k):
      step_action_with_parameter_vars = []
      for action_var in action_vars:
        [action_name_var] = self.var_dis.get_vars(1)
        parameter_vars = []
        for parameter in action_var[1]:
          parameter_vars.append(self.var_dis.get_vars(object_type_dict[parameter[1]]))
        step_action_with_parameter_vars.append([action_name_var, parameter_vars])
      self.action_with_parameter_vars.append(step_action_with_parameter_vars)

    #for actions in self.action_with_parameter_vars:
    #  for action in actions:
    #    print(action)
    #  print("\n")

  # Generating k+1 states for k steps:
  def gen_predicate_vars(self, tfun, k):
    for i in range(k+1):
      step_predicate_vars = self.var_dis.get_vars(tfun.num_predicates)
      self.predicates.append(step_predicate_vars)

  # Generates required variables for each type of object:
  def gen_forall_vars(self, obj_forall_vars):
    for obj_type, obj_var_list in obj_forall_vars.items():
      temp_var_list = []
      for var in obj_var_list:
        new_vars = self.var_dis.get_vars(len(var))
        temp_var_list.append(new_vars)
      self.forall_vars.append(temp_var_list)
      self.forall_vars_map[obj_type] = temp_var_list

  def gen_if_existential_gate(self, updated_objects, base_action_vars, k):
    if_existential_output_list = []
    for i in range(k):
      for j in range(len(self.action_with_parameter_vars[i])):
        cur_base_action_vars = base_action_vars[j]
        action_vars = self.action_with_parameter_vars[i][j]
        main_action_var = action_vars[0]
        cur_base_main_action_var = cur_base_action_vars[0]
        num_action_parameters = len(action_vars[1])
        for k in range(num_action_parameters):
          parameter = action_vars[1][k]
          base_parameter = cur_base_action_vars[1][k]
          # Extracting parameter type crudely:
          parameter_type = base_parameter[1]
          num_objects = len(updated_objects[parameter_type])
          upper_bound = int(math.pow(2, len(parameter)))
          bin_len = len(parameter)
          for obj_num in range(num_objects+1, upper_bound+1):
            # Due to binary represetation:
            cur_obj = obj_num -1
            bin_string = format(cur_obj,'0' + str(bin_len) + 'b')
            temp_condition = []
            for j in range(bin_len):
              if bin_string[j] == '0':
                temp_condition.append(-parameter[j])
              else:
                temp_condition.append(parameter[j])
            [temp_gate] = self.var_dis.get_vars(1)
            self.encoding.append(['and', temp_gate, temp_condition])
            if_existential_output_list.append(temp_gate)
    self.encoding.append(['# Gates for avoiding extra objects in parameters:'])
    [self.if_existential_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['or', self.if_existential_output_gate, if_existential_output_list])

  def gen_conditional_transition_gates(self, updated_objects):
    forall_condition_gate_list = []
    for forall_var_type, vars_list in self.forall_vars_map.items():
      num_objects = len(updated_objects[forall_var_type])
      for var_list in vars_list:
        bin_len = len(var_list)
        if (len(vars_list) != 0):
          upper_bound = int(math.pow(2, bin_len))
          for i in range(num_objects+1, upper_bound+1):
            # Due to binary represetation:
            cur_obj = i -1
            bin_string = format(cur_obj,'0' + str(bin_len) + 'b')
            temp_condition = []
            for j in range(bin_len):
              if bin_string[j] == '0':
                temp_condition.append(-var_list[j])
              else:
                temp_condition.append(var_list[j])
            [temp_gate] = self.var_dis.get_vars(1)
            self.encoding.append(['and', temp_gate, temp_condition])
            forall_condition_gate_list.append(temp_gate)
    self.encoding.append(['# If condition gates for extra objects:'])

    # Generating final gate variable:
    [if_condition_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['or', if_condition_gate, forall_condition_gate_list])

    self.encoding.append(['# All transition gates:'])
    [then_final_transition_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['and', then_final_transition_output_gate, self.transition_step_output_gates])

    self.encoding.append(['# Final if not then gate for transition gates:'])
    [self.final_transition_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['or',self.final_transition_gate, [if_condition_gate, then_final_transition_output_gate]])


  def __init__(self, constraints_extract, tfun, k, splitvars_flag):
    self.var_dis = vd()
    self.quantifier_block = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.transition_step_output_gates = []
    self.if_existential_output_gate = 0 # existential final gate can never be 0
    self.final_transition_gate = 0 # final transition gate can never be 0
    self.final_output_gate = 0 # final output gate can never be 0

    self.predicates = []
    self.gen_predicate_vars(tfun, k)

    self.action_with_parameter_vars = []
    self.gen_action_with_parameter_vars(constraints_extract.bin_object_type_vars_dict, constraints_extract.action_vars, tfun, k)

    self.forall_vars = []
    self.forall_vars_map = {}
    self.gen_forall_vars(tfun.obj_forall_vars)

    self.split_forall_vars = self.var_dis.get_vars(len(tfun.split_predicates_forall_vars))
    #print(self.split_forall_vars)

    self.generate_k_transitions(tfun, k)

    self.generate_initial_gate(constraints_extract, splitvars_flag)
    self.generate_goal_gate(constraints_extract, k, splitvars_flag)

    self.gen_conditional_transition_gates(constraints_extract.updated_objects)

    self.gen_if_existential_gate(constraints_extract.updated_objects, constraints_extract.action_vars, k)

    self.generate_final_gate()

    self.generate_quantifier_blocks(k, splitvars_flag)
