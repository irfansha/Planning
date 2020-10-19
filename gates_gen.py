# Irfansha Shaik, 30.09.2020, Aarhus.

'''
Todos:
  1. XXX
'''

class TransitionGatesGen():

  # Takes list and current list of gates
  # generates OR gate:
  def or_gate(self, current_list):
    temp_gate = ['or', self.next_gate, current_list]
    self.transition_gates.append(temp_gate)
    self.output_gate = self.next_gate
    self.next_gate = self.next_gate + 1

  # Takes list and current list of gates
  # generates AND gate:
  def and_gate(self, current_list):
    temp_gate = ['and', self.next_gate, current_list]
    self.transition_gates.append(temp_gate)
    self.output_gate = self.next_gate
    self.next_gate = self.next_gate + 1

  # Takes list and current list of gates
  # generates if then gate i.e., if x then y -> y' = AND(y) and OR(-x, y'):
  def if_then_gate(self, if_gate, then_list):
    # AND gate for then list:
    if isinstance(then_list, int):
      self.or_gate([-if_gate, then_list])
    else:
      self.and_gate(then_list)
      self.or_gate([-if_gate, self.output_gate])

  # Takes list and current list of gates
  # generates if then not gate i.e., if x then -y -> -y' = AND(y) and OR(-x, -y'):
  def if_then_not_gate(self, if_gate, then_list):
    # AND gate for then list:
    if isinstance(then_list, int):
      self.or_gate([-if_gate, -then_list])
    else:
      self.and_gate(then_list)
      self.or_gate([-if_gate, -self.output_gate])


  # Takes list and current list of gates
  # generates eq gate i.e., x == y -> if x then y and if y then x:
  def eq_gate(self, x, y):
    self.if_then_gate(x,y)
    temp_first_gate = self.output_gate
    self.if_then_gate(y,x)
    self.and_gate([temp_first_gate,self.output_gate])
    self.untouched_prop_map[(x,y)] = self.output_gate



  def add_untouched_prop_gates(self, tfun):
    # for each untouch propagation eq gates are generated:
    for i in range(tfun.num_state_vars):
      # pre and post integer state variables:
      self.eq_gate(i+1, i+1+tfun.num_state_vars)

  def add_action_gates(self, tfun):
    aux_action_gates = []
    for action in tfun.integer_tfun:
      if_gate = action.pop(0)
      then_list = action.pop(0)
      for untouched_prop_list in action:
        for untouched_prop in untouched_prop_list:
          then_list.append(self.untouched_prop_map[untouched_prop])
        #print(then_gate)
      self.if_then_gate(if_gate, then_list)
      aux_action_gates.append(self.output_gate)
    self.transition_gates.append(['# final output action gate:'])
    self.and_gate(aux_action_gates)
    self.final_action_gate = self.output_gate

  def add_amo_alo_gates(self, tfun):
    aux_amo_gates = []
    for i in range(tfun.num_action_vars):
      temp_av_list = list(tfun.action_vars)
      if_gate = temp_av_list.pop(i)
      self.if_then_not_gate(if_gate, temp_av_list)
      aux_amo_gates.append(self.output_gate)
    self.transition_gates.append(['# final output AMO gate:'])
    self.and_gate(aux_amo_gates)
    amo_output_gate = self.output_gate

    self.transition_gates.append(['# ALO gate:'])
    self.or_gate(tfun.action_vars)
    alo_output_gate = self.output_gate

    self.transition_gates.append(['# final output AMO ALO gate:'])
    self.and_gate([amo_output_gate, alo_output_gate])
    self.final_amoalo_gate = self.output_gate

  def add_final_gate(self):
    self.and_gate([self.final_action_gate, self.final_amoalo_gate])
    self.final_transition_gate = self.output_gate

  def __init__(self, tfun):
    self.transition_gates = []
    self.output_gate = 0 # output gate will never be zero
    self.next_gate = 2*tfun.num_state_vars + tfun.num_action_vars + 1
    self.untouched_prop_map = {}
    self.final_action_gate = 0 # final action gate will never be zero
    self.final_amoalo_gate = 0 # final amo alo gate will never be zero
    self.final_transition_gate = 0 # final transition gate will never be zero

    self.transition_gates.append(['# Untouched Propagation gates:'])
    # Adding untouched propagation gates:
    self.add_untouched_prop_gates(tfun)

    self.transition_gates.append(['# Action gates:'])
    # Adding action gates:
    self.add_action_gates(tfun)

    self.transition_gates.append(['# AMO ALO gates:'])
    # Adding AtMostOne and AtLeastOne gates:
    self.add_amo_alo_gates(tfun)

    self.transition_gates.append(['# Final transition gate:'])
    # Adding final transition gate:
    self.add_final_gate()
    self.total_gates = self.output_gate


  def new_gate_gen(self, encoding, first_name, second_name, first_state, second_state, action_vars, aux_vars):

    # Appending variables for the new transition function:
    var_list = []

    var_list.extend(first_state)
    var_list.extend(second_state)

    var_list.extend(action_vars)
    var_list.extend(aux_vars)

    encoding.append(['# Transition function from ' + first_name + ' to ' + second_name + ':'])
    encoding.append(['# ' + first_name + ' vars : (' + ', '.join(str(x) for x in first_state) + ')'])
    encoding.append(['# ' + second_name + ' vars : (' + ', '.join(str(x) for x in second_state) + ')'])
    action_vars_string = 'action variables : ' + ','.join(str(x) for x in action_vars)
    encoding.append(['# ' + action_vars_string])

    aux_vars_string = 'auxilary variables : ' + ','.join(str(x) for x in aux_vars)
    encoding.append(['# ' + aux_vars_string])

    for gate in self.transition_gates:
      if (len(gate) != 1):
        # Indirectly mapping the list of variables to transition function:
        new_gate_name = var_list[gate[1]-1]
        new_gate_list = []
        for prev_gate in gate[2]:
          if prev_gate > 0:
            new_gate_list.append(var_list[prev_gate-1])
          else:
            new_gate_list.append(-var_list[(-prev_gate)-1])
        encoding.append([gate[0], new_gate_name, new_gate_list])
      else:
        encoding.append([gate[0]])




class StateGatesGen():

  # Takes list and current list of gates
  # generates OR gate:
  def or_gate(self, current_list):
    temp_gate = ['or', self.next_gate, current_list]
    self.base_state_gates.append(temp_gate)
    self.output_gate = self.next_gate
    self.next_gate = self.next_gate + 1

  # Takes list and current list of gates
  # generates AND gate:
  def and_gate(self, current_list):
    temp_gate = ['and', self.next_gate, current_list]
    self.base_state_gates.append(temp_gate)
    self.output_gate = self.next_gate
    self.next_gate = self.next_gate + 1

  # Takes list and current list of gates
  # generates if then gate i.e., if x then y -> y' = AND(y) and OR(-x, y'):
  def if_then_gate(self, if_gate, then_list):
    # AND gate for then list:
    if isinstance(then_list, int):
      self.or_gate([-if_gate, then_list])
    else:
      self.and_gate(then_list)
      self.or_gate([-if_gate, self.output_gate])

  # Takes list and current list of gates
  # generates if then not gate i.e., if x then -y -> -y' = AND(y) and OR(-x, -y'):
  def if_then_not_gate(self, if_gate, then_list):
    # AND gate for then list:
    if isinstance(then_list, int):
      self.or_gate([-if_gate, -then_list])
    else:
      self.and_gate(then_list)
      self.or_gate([-if_gate, -self.output_gate])


  # Takes list and current list of gates
  # generates eq gate i.e., x == y -> if x then y and if y then x:
  def eq_gate(self, x, y):
    self.if_then_gate(x,y)
    temp_first_gate = self.output_gate
    self.if_then_gate(y,x)
    self.and_gate([temp_first_gate,self.output_gate])

  # Takes lists of gates of two states and generates equality gate:
  def eq_state_gate(self):
    assert(len(self.first_state_vars) == len(self.second_state_vars))
    step_output_gates = []
    for i in range(len(self.first_state_vars)):
      self.eq_gate(self.first_state_vars[i], self.second_state_vars[i])
      step_output_gates.append(self.output_gate)
    self.and_gate(step_output_gates)

  def new_gate_gen(self, encoding, first_name, second_name, first_sv_list, second_sv_list, aux_vars_list):
    var_list = []
    var_list.extend(first_sv_list)
    var_list.extend(second_sv_list)
    var_list.extend(aux_vars_list)

    encoding.append(['# Eq gate between ' + first_name + ':(' + ', '.join(str(x) for x in first_sv_list) + ') and'])
    encoding.append(['#                 '+ second_name + ':('+ ', '.join(str(x) for x in second_sv_list) + ')'])
    encoding.append(['#          aux_gates:('+ ', '.join(str(x) for x in aux_vars_list) + ')'])
    for gate in self.base_state_gates:
      # Indirectly mapping the list of variables to new state constraint:
      new_gate_name = var_list[gate[1]-1]
      new_gate_list = []
      for prev_gate in gate[2]:
        if prev_gate > 0:
          new_gate_list.append(var_list[prev_gate-1])
        else:
          new_gate_list.append(-var_list[(-prev_gate)-1])
      encoding.append([gate[0], new_gate_name, new_gate_list])

  def __init__(self, n):
    self.base_state_gates = []
    self.first_state_vars = list(range(1,n+1))
    self.second_state_vars = list(range(n+1,2*n+1))
    self.output_gate = 0 # output gate will never be zero
    self.next_gate = 2*n+1
    self.eq_state_gate()
    self.aux_vars = self.output_gate - 2*n
    #print(self.output_gate, self.aux_vars, n)
