# Irfansha Shaik, 24.10.2020, Aarhus

from variable_dispatcher import VarDispatcher as vd
from state_gen import StateGen as sg
from gates_gen import StateGatesGen as sgg
import math

'''
Todos:
1. Extraction is wrong and giving different answers, to be updated.
'''

class CTEncoding():

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



  def generate_zero_condition(self, tfun):
    # Layer = 0:
    if_block = []
    for i in range(self.log_k - 1):
      if_block.append(-self.forall_vars[i])
    self.if_blocks.append(if_block)
    [if_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['and', if_output_gate, if_block])

    step_action_vars = self.var_dis.get_vars(tfun.num_action_vars)
    self.action_vars.append(step_action_vars)

    # Generating auxilary vars:
    step_aux_vars = self.var_dis.get_vars(tfun.num_aux_vars)

    transition_output_gate = step_aux_vars[-1]

    tfun.gates_gen.new_gate_gen(self.encoding, 'X_I', 'X_0', self.initial_state, self.quantifier_states_gen.states[0], step_action_vars, step_aux_vars)

    [if_then_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['# if then gate for X_I and X_0:'])
    self.encoding.append(['or', if_then_gate, [-if_output_gate, transition_output_gate]])

    self.condition_output_gates.append(if_then_gate)

    if_block = []
    for i in range(self.log_k - 1):
      if_block.append(self.forall_vars[i])
    self.if_blocks.append(if_block)
    [if_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['and', if_output_gate, if_block])

    step_action_vars = self.var_dis.get_vars(tfun.num_action_vars)
    self.action_vars.append(step_action_vars)

    # Generating auxilary vars:
    step_aux_vars = self.var_dis.get_vars(tfun.num_aux_vars)

    transition_output_gate = step_aux_vars[-1]

    tfun.gates_gen.new_gate_gen(self.encoding, 'X_0', 'X_G', self.quantifier_states_gen.states[0], self.goal_state, step_action_vars, step_aux_vars)

    [if_then_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['# if then gate for X_0 and X_G:'])
    self.encoding.append(['or', if_then_gate, [-if_output_gate, transition_output_gate]])

    self.condition_output_gates.append(if_then_gate)

  def generate_conditions(self, tfun):
    for i in range(1, self.log_k):
      if_block = []
      for j in range(1,i):
        if_block.append(self.forall_vars[j-1])
      if_block.append(-self.forall_vars[i-1])
      self.if_blocks.append(if_block)
      [if_output_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['and', if_output_gate, if_block])

      step_action_vars = self.var_dis.get_vars(tfun.num_action_vars)
      self.action_vars.append(step_action_vars)

      # Generating auxilary vars:
      step_aux_vars = self.var_dis.get_vars(tfun.num_aux_vars)

      transition_output_gate = step_aux_vars[-1]

      tfun.gates_gen.new_gate_gen(self.encoding, 'X_0', 'X_' + str(i), self.quantifier_states_gen.states[0], self.quantifier_states_gen.states[i], step_action_vars, step_aux_vars)

      [if_then_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['# if then gate for X_0 and X_' + str(i) +':'])
      self.encoding.append(['or', if_then_gate, [-if_output_gate, transition_output_gate]])

      self.condition_output_gates.append(if_then_gate)

      if_block = []
      for j in range(1,i):
        if_block.append(-self.forall_vars[j-1])
      if_block.append(self.forall_vars[i-1])
      self.if_blocks.append(if_block)
      [if_output_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['and', if_output_gate, if_block])

      step_action_vars = self.var_dis.get_vars(tfun.num_action_vars)
      self.action_vars.append(step_action_vars)

      # Generating auxilary vars:
      step_aux_vars = self.var_dis.get_vars(tfun.num_aux_vars)

      transition_output_gate = step_aux_vars[-1]

      tfun.gates_gen.new_gate_gen(self.encoding, 'X_' + str(i), 'X_0', self.quantifier_states_gen.states[i], self.quantifier_states_gen.states[0], step_action_vars, step_aux_vars)

      [if_then_gate] = self.var_dis.get_vars(1)
      self.encoding.append(['# if then gate for X_' + str(i) +' and X_0:'])
      self.encoding.append(['or', if_then_gate, [-if_output_gate, transition_output_gate]])

      self.condition_output_gates.append(if_then_gate)

  def generate_extract_gates(self, num_action_vars, k):
    states_gg = sgg(num_action_vars)
    for i in range(int(k/2)):
      bin_string = format(i,'0' + str(self.log_k) + 'b')
      temp_condition = []
      for j in range(1,self.log_k):
        if bin_string[j] == '0':
          temp_condition.append(-self.forall_vars[-j])
        else:
          temp_condition.append(self.forall_vars[-j])
      set_temp_condition = set(temp_condition)
      count = 0
      for l_index in range(len(self.if_blocks)):
        if(set(self.if_blocks[l_index]).issubset(set_temp_condition)):
          assert(count < 2)
          aux_vars = self.var_dis.get_vars(states_gg.aux_vars)
          states_gg.new_gate_gen(self.encoding, 'a' + str(2*i + count), 'XXX', self.extraction_action_vars_gen.states[2*i + count], self.action_vars[l_index], aux_vars)
          self.extract_output_gates.append(aux_vars[-1])
          count = count + 1

  def generate_final_gate(self, extraction):
    temp_final_list = []
    temp_final_list.append(self.initial_output_gate)
    temp_final_list.extend(self.condition_output_gates)
    if (extraction):
      temp_final_list.extend(self.extract_output_gates)
    #temp_final_list.append(self.transition_output_gate)
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
    for i in range(1,self.log_k):
      self.quantifier_block.append(['# Layer ' + str(self.log_k - i) + ':'])
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.quantifier_states_gen.states[-i]) + ')'])
      self.quantifier_block.append(['forall(' + str(self.forall_vars[-i]) + ')'])
    self.quantifier_block.append(['# Layer 0:'])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.quantifier_states_gen.states[0]) + ')'])

    self.quantifier_block.append(['# Action variables :'])
    for states in self.action_vars:
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in states) + ')'])

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
    #self.transition_output_gate = 0 # transition output gate can never be 0
    self.final_output_gate = 0 # final output gate can never be 0

    self.initial_state = self.var_dis.get_vars(tfun.num_state_vars)
    self.goal_state = self.var_dis.get_vars(tfun.num_state_vars)


    # CTE encoding results in makespan of 2^(k+1)
    # We use 0 ... log_k -1 for consistency:
    self.log_k = int(math.log2(k))
    assert(math.pow(2,self.log_k) == k)

    # sg generates k+1 states, so using k -1 as parameter:
    self.quantifier_states_gen = sg(self.var_dis, tfun.num_state_vars, self.log_k-1)


    # We only use log_k -1 forall variables:
    self.forall_vars = self.var_dis.get_vars(self.log_k - 1)

    # generating k actions variables for extraction:
    self.extraction_action_vars_gen = sg(self.var_dis, tfun.num_action_vars, k-1)

    self.generate_initial_gate(constraints_extract)

    self.generate_zero_condition(tfun)

    self.generate_conditions(tfun)

    if (extraction):
      self.generate_extract_gates(tfun.num_action_vars, k)

    self.generate_goal_gate(constraints_extract, k)

    self.generate_final_gate(extraction)

    self.generate_quantifier_blocks(extraction)
