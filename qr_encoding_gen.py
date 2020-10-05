# Irfansha Shaik, 30.09.2020, Aarhus

from variable_dispatcher import VarDispatcher as vd
from state_gen import StateGen as sg
from gates_gen import StateGatesGen as sgg

class QREncoding():

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

  def generate_forall_var(self, n):
    self.forall_vars_first = self.var_dis.get_vars(n)
    self.forall_vars_second = self.var_dis.get_vars(n)

  def generate_if_block_for_transition(self, n, k):
    states_gg = sgg(self.var_dis.next_var, self.encoding)
    eq_output_gates = []
    for i in range(k):
      step_eq_output_gates = []
      self.encoding.append(['# Eq gate between S' + str(i) + ':(' + ', '.join(str(x) for x in self.states_gen.states[i]) + ') and'])
      self.encoding.append(['#                 X1:('+ ', '.join(str(x) for x in self.forall_vars_first) + ')'])
      for j in range(n):
        states_gg.eq_gate(self.states_gen.states[i][j], self.forall_vars_first[j])
        step_eq_output_gates.append(states_gg.output_gate)
      # and between individual eq gates:
      states_gg.and_gate(step_eq_output_gates)
      first_gate = states_gg.output_gate

      step_eq_output_gates = []
      self.encoding.append(['# Eq gate between S' + str(i+1) + ':(' + ', '.join(str(x) for x in self.states_gen.states[i+1]) + ') and'])
      self.encoding.append(['#                 X2:('+ ', '.join(str(x) for x in self.forall_vars_second) + ')'])
      for j in range(n):
        states_gg.eq_gate(self.states_gen.states[i+1][j], self.forall_vars_second[j])
        step_eq_output_gates.append(states_gg.output_gate)
      # and between individual eq gates:
      states_gg.and_gate(step_eq_output_gates)
      second_gate = states_gg.output_gate
      eq_output_gates.append((first_gate, second_gate))
    or_gates_list = []
    for i in range(k):
      self.encoding.append(['# S' + str(i) + ' == X1 and S' + str(i+1) + ' == X2' ])
      states_gg.and_gate([eq_output_gates[i][0], eq_output_gates[i][1]])
      or_gates_list.append(states_gg.output_gate)
    self.encoding.append(['# or gate for if condition:'])
    states_gg.or_gate(or_gates_list)
    self.if_tfun_gate = states_gg.output_gate
    self.var_dis.set_next_var(states_gg.next_gate)

  def generate_if_then_transition(self, tfun):
    # First generating transition function:
    self.action_vars = self.var_dis.get_vars(tfun.num_action_vars)

    # Generating auxilary vars:
    aux_vars = self.var_dis.get_vars(tfun.num_aux_vars)

    # Appending transition output gates:
    transition_output_gate = aux_vars[-1]

    # Appending variables for the new transition function:
    transition_vars = []

    transition_vars.extend(self.forall_vars_first)
    transition_vars.extend(self.forall_vars_second)

    transition_vars.extend(self.action_vars)
    transition_vars.extend(aux_vars)
    #print(step_transition_vars)

    self.encoding.append(['# Transition function from X1 to X2 :'])
    self.encoding.append(['# X1 vars : (' + ', '.join(str(x) for x in self.forall_vars_first) + ')'])
    self.encoding.append(['# X2 vars : (' + ', '.join(str(x) for x in self.forall_vars_second) + ')'])
    action_vars_string = 'action variables : ' + ','.join(str(x) for x in self.action_vars)
    self.encoding.append(['# ' + action_vars_string])

    aux_vars_string = 'auxilary variables : ' + ','.join(str(x) for x in aux_vars)
    self.encoding.append(['# ' + aux_vars_string])

    tfun.gates_gen.new_gate_gen(self.encoding, transition_vars)
    # Now generating if then gate for transition:
    self.encoding.append(['# If then transition gate :'])
    [self.if_then_tfun_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['or', self.if_then_tfun_gate , [-self.if_tfun_gate, transition_output_gate]])


  def generate_final_gate(self):
    temp_final_list = []
    temp_final_list.append(self.initial_output_gate)
    temp_final_list.append(self.if_then_tfun_gate)
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
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in self.forall_vars_first) + ')'])
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in self.forall_vars_second) + ')'])
    self.quantifier_block.append(['# Actions variables :'])
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
    self.forall_vars_first = []
    self.forall_vars_second = []
    self.quantifier_block = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.if_tfun_gate = 0 # if transition gate can never be 0
    self.if_then_tfun_gate = 0 # if then transition gate can never be 0
    self.final_output_gate = 0 # final output gate can never be 0

    # generating k+1 states, since k steps:
    self.states_gen = sg(self.var_dis, tfun.num_state_vars, k)
    #print(states_gen.states)

    self.generate_forall_var(tfun.num_state_vars)

    self.generate_initial_gate(constraints_extract)

    self.generate_goal_gate(constraints_extract, k)

    self.generate_if_block_for_transition(tfun.num_state_vars, k)

    self.generate_if_then_transition(tfun)

    self.generate_final_gate()

    self.generate_quantifier_blocks()
