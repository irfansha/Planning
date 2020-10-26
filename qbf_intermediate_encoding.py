# Irfansha Shaik, 21.10.2020, Aarhus

from variable_dispatcher import VarDispatcher as vd
from state_gen import StateGen as sg
from gates_gen import StateGatesGen as sgg
import math

class QIEncoding():

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

  def generate_k_conditions(self, n, k):
    states_gg = sgg(n)
    for i in range(k):
      bin_string = format(i,'0' + str(self.log_k) + 'b')
      temp_condition = []
      for j in range(self.log_k):
        if bin_string[j] == '0':
          temp_condition.append(-self.forall_vars[j])
        else:
          temp_condition.append(self.forall_vars[j])
      [if_condition_gate] = self.var_dis.get_vars(1)

      first_aux_vars = self.var_dis.get_vars(states_gg.aux_vars)
      states_gg.new_gate_gen(self.encoding, 'X1', 'S'+ str(i), self.transition_first_state, self.states_gen.states[i], first_aux_vars)
      first_gate = first_aux_vars[-1]

      second_aux_vars = self.var_dis.get_vars(states_gg.aux_vars)
      states_gg.new_gate_gen(self.encoding, 'X2', 'S'+ str(i+1), self.transition_second_state, self.states_gen.states[i+1], second_aux_vars)
      second_gate = second_aux_vars[-1]

      self.encoding.append(['# If condition number: ' + str(i)])
      self.encoding.append(['and', if_condition_gate, temp_condition])

      self.encoding.append(['# If then condition for ' + 'X1 and S'+ str(i) + ':'])
      [first_if_then_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['or', first_if_then_gate, [-if_condition_gate, first_gate]])
      self.condition_output_gates.append(first_if_then_gate)

      self.encoding.append(['# If then condition for ' + 'X2 and S'+ str(i+1) + ':'])
      [second_if_then_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['or', second_if_then_gate, [-if_condition_gate, second_gate]])
      self.condition_output_gates.append(second_if_then_gate)

  def generate_transition_function(self, tfun):
    # First generating transition function:
    self.action_vars = self.var_dis.get_vars(tfun.num_action_vars)

    # Generating auxilary vars:
    aux_vars = self.var_dis.get_vars(tfun.num_aux_vars)

    # Appending transition output gates:
    self.transition_output_gate = aux_vars[-1]

    tfun.gates_gen.new_gate_gen(self.encoding, 'X1', 'X2', self.transition_first_state, self.transition_second_state, self.action_vars, aux_vars)

  def generate_final_gate(self):
    temp_final_list = []
    temp_final_list.append(self.initial_output_gate)
    temp_final_list.extend(self.condition_output_gates)
    temp_final_list.append(self.transition_output_gate)
    temp_final_list.append(self.goal_output_gate)
    self.encoding.append(['# Final gate:'])

    # Generating final gate variable:
    [self.final_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['and', self.final_output_gate, temp_final_list])

  def generate_quantifier_blocks(self):
    self.quantifier_block.append(['# State variables :'])
    for states in self.states_gen.states:
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in states) + ')'])

    self.quantifier_block.append(['# Forall variables :'])
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in self.forall_vars) + ')'])

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

  def __init__(self, constraints_extract, tfun, k):
    self.var_dis = vd()
    self.action_vars = []
    self.quantifier_block = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.condition_output_gates = []
    self.transition_output_gate = 0 # transition output gate can never be 0
    self.final_output_gate = 0 # final output gate can never be 0

    # generating k+1 states, since k steps:
    self.states_gen = sg(self.var_dis, tfun.num_state_vars, k)

    self.log_k = int(math.log2(k))
    assert(math.pow(2,self.log_k) == k)

    self.forall_vars = self.var_dis.get_vars(self.log_k)

    self.transition_first_state = self.var_dis.get_vars(tfun.num_state_vars)

    self.transition_second_state = self.var_dis.get_vars(tfun.num_state_vars)

    self.generate_initial_gate(constraints_extract)

    self.generate_k_conditions(tfun.num_state_vars, k)

    self.generate_transition_function(tfun)

    self.generate_goal_gate(constraints_extract, k)

    self.generate_final_gate()

    self.generate_quantifier_blocks()