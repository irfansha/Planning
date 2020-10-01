# Irfansha Shaik, 30.09.2020, Aarhus

from variable_dispatcher import VarDispatcher as vd
from state_gen import StateGen as sg

class SatEncoding():

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


  def generate_k_transitions(self, tfun, k):
    # Generating transition function for each step:
    for i in range(k):
      # Generating action vars:
      step_action_vars = self.var_dis.get_vars(tfun.num_action_vars)
      self.action_vars.append(step_action_vars)
      #print(step_action_vars)

      # Generating auxilary vars:
      step_aux_vars = self.var_dis.get_vars(tfun.num_aux_vars)

      # Appending transition output gates:
      self.transition_step_output_gates.append(step_aux_vars[-1])

      # Appending variables for the new transition function:
      step_transition_vars = []

      step_transition_vars.extend(self.states_gen.states[i])
      step_transition_vars.extend(self.states_gen.states[i+1])

      step_transition_vars.extend(step_action_vars)
      step_transition_vars.extend(step_aux_vars)
      #print(step_transition_vars)

      self.encoding.append(['# Transition function from S' + str(i) + ' to S' + str(i+1) + ':'])

      S_1_string = 'S_' + str(i) + ' vars : ' + ','.join(str(x) for x in self.states_gen.states[i])
      self.encoding.append(['# ' + S_1_string])

      S_2_string = 'S_' + str(i+1) + ' vars : ' + ','.join(str(x) for x in self.states_gen.states[i+1])
      self.encoding.append(['# ' + S_2_string])

      action_vars_string = 'action variables : ' + ','.join(str(x) for x in step_action_vars)
      self.encoding.append(['# ' + action_vars_string])

      aux_vars_string = 'auxilary variables : ' + ','.join(str(x) for x in step_aux_vars)
      self.encoding.append(['# ' + aux_vars_string])

      tfun.gates_gen.new_gate_gen(self.encoding, step_transition_vars)


  def generate_final_gate(self):
    temp_final_list = []
    temp_final_list.append(self.initial_output_gate)
    temp_final_list.extend(self.transition_step_output_gates)
    temp_final_list.append(self.goal_output_gate)
    self.encoding.append('# Final gate:')

    # Generating final gate variable:
    [self.final_output_gate] = self.var_dis.get_vars(1)
    self.encoding.append(['and', self.final_output_gate, temp_final_list])

  def __init__(self, constraints_extract, tfun, k):
    self.var_dis = vd()
    self.action_vars = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.transition_step_output_gates = []
    self.final_output_gate = 0 # final output gate can never be 0

    # generating k+1 states, since k steps:
    self.states_gen = sg(self.var_dis, tfun.num_state_vars, k)
    #print(states_gen.states)

    self.generate_initial_gate(constraints_extract)

    self.generate_k_transitions(tfun, k)

    self.generate_goal_gate(constraints_extract, k)

    self.generate_final_gate()

    #print(transition_step_output_gates)
    for gate in self.encoding:
      print(gate)
