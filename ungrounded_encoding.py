# Irfansha Shaik, 15.11.2020, Aarhus

from variable_dispatcher import VarDispatcher as vd
from pddl import PDDL_Parser

class UngroundedEncoding():
  # XXX to be updated:
  def generate_initial_gate(self, constraints_extract):
    self.encoding.append(['# Initial gate:'])
    temp_initial_gate = []
    for i in range(len(constraints_extract.state_vars)):
      state_var = constraints_extract.state_vars[i]
      if state_var in constraints_extract.initial_state:
        temp_initial_gate.append(self.states_gen.states[0][i])
      else:
        temp_initial_gate.append(-self.states_gen.states[0][i])

    # Generating initial gate variable:
    [self.initial_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['and', self.initial_output_gate, temp_initial_gate])
  # XXX to be updated:
  def generate_goal_gate(self, constraints_extract, k):
    self.encoding.append(['# Goal gate:'])
    temp_goal_gate = []
    for i in range(len(constraints_extract.state_vars)):
      state_var = constraints_extract.state_vars[i]
      if state_var in constraints_extract.goal_state[0]:
        temp_goal_gate.append(self.states_gen.states[k][i])
      elif state_var in constraints_extract.goal_state[1]:
        temp_goal_gate.append(-self.states_gen.states[k][i])

    # Generating initial gate variable:
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
    temp_final_list.extend(self.transition_step_output_gates)
    temp_final_list.append(self.goal_output_gate)
    self.encoding.append(['# Final gate:'])

    # Generating final gate variable:
    [self.final_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['and', self.final_output_gate, temp_final_list])

  def generate_quantifier_blocks(self, k):
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
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in self.split_forall_vars) + ')'])

    self.quantifier_block.append(['# Object forall variables :'])
    for obj_vars in self.forall_vars:
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


  def __init__(self, constraints_extract, tfun, k):
    self.var_dis = vd()
    self.quantifier_block = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.transition_step_output_gates = []
    self.final_output_gate = 0 # final output gate can never be 0

    self.predicates = []
    self.gen_predicate_vars(tfun, k)

    self.action_with_parameter_vars = []
    self.gen_action_with_parameter_vars(constraints_extract.bin_object_type_vars_dict, constraints_extract.action_vars, tfun, k)

    self.forall_vars = []
    self.gen_forall_vars(tfun.obj_forall_vars)

    self.split_forall_vars = self.var_dis.get_vars(len(tfun.split_predicates_forall_vars))
    #print(self.split_forall_vars)

    #self.generate_initial_gate(constraints_extract)

    self.generate_k_transitions(tfun, k)

    #self.generate_goal_gate(constraints_extract, k)

    self.generate_final_gate()

    self.generate_quantifier_blocks(k)
