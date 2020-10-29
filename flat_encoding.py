# Irfansha Shaik, 29.10.2020, Aarhus

'''
Todos:
  1. Remove redundant last two exists states for the transition function
'''

from variable_dispatcher import VarDispatcher as vd
from state_gen import StateGen as sg
from gates_gen import StateGatesGen as sgg
import math

class FlatEncoding():

  def generate_initial_gate(self, constraints_extract):
    self.encoding.append(['# Initial gate:'])
    temp_initial_gate = []
    for i in range(len(constraints_extract.state_vars)):
      state_var = constraints_extract.state_vars[i]
      if state_var in constraints_extract.initial_state:
        temp_initial_gate.append(self.initial_state[i])
      else:
        temp_initial_gate.append(-self.initial_state[i])

    # Generating initial gate variable:
    [self.initial_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['and', self.initial_output_gate, temp_initial_gate])

  def generate_goal_gate(self, constraints_extract, k):
    self.encoding.append(['# Goal gate:'])
    temp_goal_gate = []
    for i in range(len(constraints_extract.state_vars)):
      state_var = constraints_extract.state_vars[i]
      if state_var in constraints_extract.goal_state[0]:
        temp_goal_gate.append(self.goal_state[i])
      elif state_var in constraints_extract.goal_state[1]:
        temp_goal_gate.append(-self.goal_state[i])

    # Generating initial gate variable:
    [self.goal_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['and', self.goal_output_gate, temp_goal_gate])


  def generate_zero_condition(self, n):
    transition_states_gg = sgg(n)
    # For layer 0:
    aux_vars = self.var_dis.get_vars(transition_states_gg.aux_vars)
    transition_states_gg.new_gate_gen(self.encoding, 'X0', 'X2', self.quantifier_states_gen.states[0], self.quantifier_states_gen.states[2], aux_vars)
    [if_then_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['# if then gate for X0 == X2:'])
    self.encoding.append(['or', if_then_gate, [self.forall_vars[0], aux_vars[-1]]])
    self.condition_output_gates.append(if_then_gate)

    aux_vars = self.var_dis.get_vars(transition_states_gg.aux_vars)
    transition_states_gg.new_gate_gen(self.encoding, 'X1', 'XI', self.quantifier_states_gen.states[1], self.initial_state, aux_vars)
    [if_then_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['# if then gate for X1 == XI:'])
    self.encoding.append(['or', if_then_gate, [self.forall_vars[0], aux_vars[-1]]])
    self.condition_output_gates.append(if_then_gate)

    aux_vars = self.var_dis.get_vars(transition_states_gg.aux_vars)
    transition_states_gg.new_gate_gen(self.encoding, 'X0', 'X1', self.quantifier_states_gen.states[0], self.quantifier_states_gen.states[1], aux_vars)
    [if_then_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['# if then gate for X0 == X1:'])
    self.encoding.append(['or', if_then_gate, [-self.forall_vars[0], aux_vars[-1]]])
    self.condition_output_gates.append(if_then_gate)

    aux_vars = self.var_dis.get_vars(transition_states_gg.aux_vars)
    transition_states_gg.new_gate_gen(self.encoding, 'X2', 'XG', self.quantifier_states_gen.states[2], self.goal_state, aux_vars)
    [if_then_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['# if then gate for X2 == XG:'])
    self.encoding.append(['or', if_then_gate, [-self.forall_vars[0], aux_vars[-1]]])
    self.condition_output_gates.append(if_then_gate)

  def generate_conditions(self, n):
    transition_states_gg = sgg(n)
    for i in range(1, self.log_k):
      aux_vars = self.var_dis.get_vars(transition_states_gg.aux_vars)
      transition_states_gg.new_gate_gen(self.encoding, 'X' + str(3 * i), 'X' + str((3 * i) + 2), self.quantifier_states_gen.states[3*i], self.quantifier_states_gen.states[(3*i)+2], aux_vars)
      [if_then_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['# if then gate for X' + str(3 * i) +  '==' + 'X' + str((3 * i) + 2) + ':'])
      self.encoding.append(['or', if_then_gate, [self.forall_vars[i], aux_vars[-1]]])
      self.condition_output_gates.append(if_then_gate)

      aux_vars = self.var_dis.get_vars(transition_states_gg.aux_vars)
      transition_states_gg.new_gate_gen(self.encoding, 'X' + str((3 * i) + 1), 'X' + str((3 * (i-1)) + 1), self.quantifier_states_gen.states[(3 * i) + 1], self.quantifier_states_gen.states[(3 * (i-1)) + 1], aux_vars)
      [if_then_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['# if then gate for X' + str((3 * i) + 1) + '==' + 'X' + str((3 * (i-1)) + 1)+ ':'])
      self.encoding.append(['or', if_then_gate, [self.forall_vars[i], aux_vars[-1]]])
      self.condition_output_gates.append(if_then_gate)

      aux_vars = self.var_dis.get_vars(transition_states_gg.aux_vars)
      transition_states_gg.new_gate_gen(self.encoding, 'X' + str(3 * i), 'X' + str((3 * i) + 1), self.quantifier_states_gen.states[3*i], self.quantifier_states_gen.states[(3*i)+1], aux_vars)
      [if_then_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['# if then gate for X' + str(3 * i) +  '==' + 'X' + str((3 * i) + 1) + ':'])
      self.encoding.append(['or', if_then_gate, [-self.forall_vars[i], aux_vars[-1]]])
      self.condition_output_gates.append(if_then_gate)

      aux_vars = self.var_dis.get_vars(transition_states_gg.aux_vars)
      transition_states_gg.new_gate_gen(self.encoding, 'X' + str((3 * i) + 2), 'X' + str((3 * (i-1)) + 2), self.quantifier_states_gen.states[(3 * i) + 2], self.quantifier_states_gen.states[(3 * (i-1)) + 2], aux_vars)
      [if_then_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['# if then gate for X' + str((3 * i) + 2) + '==' + 'X' + str((3 * (i-1)) + 2)+ ':'])
      self.encoding.append(['or', if_then_gate, [-self.forall_vars[i], aux_vars[-1]]])
      self.condition_output_gates.append(if_then_gate)

    aux_vars = self.var_dis.get_vars(transition_states_gg.aux_vars)
    transition_states_gg.new_gate_gen(self.encoding, 'X' + str(3*(self.log_k -1) +1), 'S1', self.quantifier_states_gen.states[-2], self.transition_first_state, aux_vars)
    self.condition_output_gates.append(aux_vars[-1])

    aux_vars = self.var_dis.get_vars(transition_states_gg.aux_vars)
    transition_states_gg.new_gate_gen(self.encoding, 'X' + str(3*(self.log_k -1) +2), 'S2', self.quantifier_states_gen.states[-1], self.transition_second_state, aux_vars)
    self.condition_output_gates.append(aux_vars[-1])
    

  def generate_transition_function(self, tfun):
    # First generating transition function:
    self.action_vars = self.var_dis.get_vars(tfun.num_action_vars)

    # Generating auxilary vars:
    aux_vars = self.var_dis.get_vars(tfun.num_aux_vars)

    # Appending transition output gates:
    self.transition_output_gate = aux_vars[-1]

    tfun.gates_gen.new_gate_gen(self.encoding, 'S1', 'S2', self.transition_first_state, self.transition_second_state, self.action_vars, aux_vars)


  def generate_extract_gates(self, num_action_vars, k):
    states_gg = sgg(num_action_vars)
    for i in range(k):
      bin_string = format(i,'0' + str(self.log_k) + 'b')
      temp_condition = []
      for j in range(self.log_k):
        if bin_string[j] == '0':
          temp_condition.append(-self.forall_vars[j])
        else:
          temp_condition.append(self.forall_vars[j])
      [if_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['and', if_gate, temp_condition])

      aux_vars = self.var_dis.get_vars(states_gg.aux_vars)
      states_gg.new_gate_gen(self.encoding, 'a' + str(i), 'a', self.extraction_action_vars_gen.states[i], self.action_vars, aux_vars)

      [if_then_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['or', if_then_gate,[-if_gate, aux_vars[-1]]])
      self.extract_output_gates.append(if_then_gate)

  def generate_final_gate(self, extraction):
    temp_final_list = []
    temp_final_list.append(self.initial_output_gate)
    temp_final_list.extend(self.condition_output_gates)
    if (extraction):
      temp_final_list.extend(self.extract_output_gates)
    temp_final_list.append(self.transition_output_gate)
    temp_final_list.append(self.goal_output_gate)
    self.encoding.append(['# Final gate:'])

    # Generating final gate variable:
    [self.final_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['and', self.final_output_gate, temp_final_list])

  def generate_quantifier_blocks(self, extraction):
    if (extraction):
      self.quantifier_block.append(['# Extraction action variables :'])
      for states in self.extraction_action_vars_gen.states:
        self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in states) + ')'])

    self.quantifier_block.append(['# Initial state variables :'])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.initial_state) + ')'])

    self.quantifier_block.append(['# Goal state variables :'])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.goal_state) + ')'])

    self.quantifier_block.append(['# Quantifier state variables and forall variables:'])
    for i in range(self.log_k):
      self.quantifier_block.append(['# Layer ' + str(i) + ':'])
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.quantifier_states_gen.states[3*i]) + ')'])
      self.quantifier_block.append(['forall(' + str(self.forall_vars[i]) + ')'])
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.quantifier_states_gen.states[3*i + 1]) + ')'])
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.quantifier_states_gen.states[3*i + 2]) + ')'])

    self.quantifier_block.append(['# Transition state variables X1, X2 :'])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.transition_first_state) + ')'])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.transition_second_state) + ')'])

    self.quantifier_block.append(['# Action variables :'])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.action_vars) + ')'])

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

  def __init__(self, constraints_extract, tfun, k, extraction):
    self.var_dis = vd()
    self.action_vars = []
    self.quantifier_block = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.condition_output_gates = []
    self.extract_output_gates = []
    self.if_blocks = []
    self.transition_output_gate = 0 # transition output gate can never be 0
    self.final_output_gate = 0 # final output gate can never be 0

    self.initial_state = self.var_dis.get_vars(tfun.num_state_vars)
    self.goal_state = self.var_dis.get_vars(tfun.num_state_vars)


    # CTE encoding results in makespan of 2^(k+1)
    # We use 0 ... log_k -1 for consistency:
    self.log_k = int(math.log2(k))
    assert(math.pow(2,self.log_k) == k)

    # sg generates k+1 states, so using k - 1 as parameter:
    self.quantifier_states_gen = sg(self.var_dis, tfun.num_state_vars, (3*self.log_k)-1)


    # We only use log_k forall variables:
    self.forall_vars = self.var_dis.get_vars(self.log_k)

    self.transition_first_state = self.var_dis.get_vars(tfun.num_state_vars)

    self.transition_second_state = self.var_dis.get_vars(tfun.num_state_vars)

    # generating k actions variables for extraction:
    self.extraction_action_vars_gen = sg(self.var_dis, tfun.num_action_vars, k-1)

    self.generate_initial_gate(constraints_extract)

    self.generate_zero_condition(tfun.num_state_vars)

    self.generate_conditions(tfun.num_state_vars)

    self.generate_transition_function(tfun)

    if (extraction):
      self.generate_extract_gates(tfun.num_action_vars, k)

    self.generate_goal_gate(constraints_extract, k)

    self.generate_final_gate(extraction)

    self.generate_quantifier_blocks(extraction)
