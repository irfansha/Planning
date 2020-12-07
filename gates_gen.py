# Irfansha Shaik, 30.09.2020, Aarhus.

'''
Todos:
  1. XXX
'''

import math
from collections import Counter

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

class TransitionGatesGenWithoutAmoAlo():

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
    # In addition to action gates, we also include extra binary output gate:
    final_gates = list(aux_action_gates)
    final_gates.append(-self.extra_binary_final_ouput_gate)
    self.and_gate(final_gates)
    self.final_action_gate = self.output_gate


  def aux_action_vars(self, tfun):
    for i in range(tfun.num_aux_action_vars):
      bin_string = format(i,'0' + str(self.num_binary_action_vars) + 'b')
      temp_condition = []
      for j in range(self.num_binary_action_vars):
        if bin_string[j] == '0':
          temp_condition.append(-self.binary_action_vars[j])
        else:
          temp_condition.append(self.binary_action_vars[j])
      temp_gate = ['and', tfun.aux_action_vars[i], temp_condition]
      self.transition_gates.append(temp_gate)
    for i in range(tfun.num_aux_action_vars, int(math.pow(2,self.num_binary_action_vars))):
      bin_string = format(i,'0' + str(self.num_binary_action_vars) + 'b')
      temp_condition = []
      for j in range(self.num_binary_action_vars):
        if bin_string[j] == '0':
          temp_condition.append(-self.binary_action_vars[j])
        else:
          temp_condition.append(self.binary_action_vars[j])
      self.and_gate(temp_condition)
      self.extra_binary_output_gates.append(self.output_gate)
    #print(self.binary_action_vars)

  def binary_final_gate_gen(self):
    self.or_gate(self.extra_binary_output_gates)
    self.extra_binary_final_ouput_gate = self.output_gate

  def __init__(self, tfun):
    self.transition_gates = []
    self.output_gate = 0 # output gate will never be zero

    self.num_aux_action_vars = tfun.num_aux_action_vars

    self.num_binary_action_vars = math.ceil(math.log2(self.num_aux_action_vars))

    self.binary_action_vars = list(range(2*tfun.num_state_vars + self.num_aux_action_vars + 1, 2*tfun.num_state_vars + self.num_aux_action_vars + self.num_binary_action_vars+1))

    self.next_gate = 2*tfun.num_state_vars + self.num_aux_action_vars + self.num_binary_action_vars + 1

    self.extra_binary_output_gates = []
    self.aux_action_vars(tfun)

    self.extra_binary_final_ouput_gate = 0 # can never be 0
    self.binary_final_gate_gen()

    self.untouched_prop_map = {}
    self.final_action_gate = 0 # final action gate will never be zero

    self.transition_gates.append(['# Untouched Propagation gates:'])
    # Adding untouched propagation gates:
    self.add_untouched_prop_gates(tfun)

    self.transition_gates.append(['# Action gates:'])
    # Adding action gates:
    self.add_action_gates(tfun)

    # Adding final transition gate:
    self.total_gates = self.output_gate

  def new_gate_gen(self, encoding, first_name, second_name, first_state, second_state, action_vars, aux_vars):

    # Appending variables for the new transition function:
    var_list = []

    var_list.extend(first_state)
    var_list.extend(second_state)

    # Rearranging binary variables and auxilary action variables to allow ordering:
    aux_action_vars = aux_vars[:self.num_aux_action_vars]

    var_list.extend(aux_action_vars)

    var_list.extend(action_vars)
    var_list.extend(aux_vars[self.num_aux_action_vars:])

    encoding.append(['# Transition function from ' + first_name + ' to ' + second_name + ':'])
    encoding.append(['# ' + first_name + ' vars : (' + ', '.join(str(x) for x in first_state) + ')'])
    encoding.append(['# ' + second_name + ' vars : (' + ', '.join(str(x) for x in second_state) + ')'])
    action_vars_string = 'action variables : ' + ','.join(str(x) for x in action_vars)
    encoding.append(['# ' + action_vars_string])

    aux_action_vars_string = 'auxilary action variables : ' + ','.join(str(x) for x in aux_action_vars)
    encoding.append(['# ' + aux_action_vars_string])

    aux_vars_string  = 'auxilary variables :' + ','.join(str(x) for x in aux_vars[self.num_aux_action_vars:])
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


class UngroundedTransitionGatesGen():

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

  # Takes list and current list of gates
  # generates eq gate i.e., x == y -> if x then y and if y then x:
  def eq_forall_var_gate(self, x, y):
    self.if_then_gate(x,y)
    temp_first_gate = self.output_gate
    self.if_then_gate(y,x)
    self.and_gate([temp_first_gate,self.output_gate])


  # Takes lists of gates of two object vars and generates equality gate:
  def eq_forall_vars_gate(self, first_vars, second_vars):
    assert(len(first_vars) == len(second_vars))
    self.transition_gates.append(['# forall vars equality gates:'])
    self.transition_gates.append(['# vars : (' + ', '.join(str(x) for x in first_vars) + ')'])
    self.transition_gates.append(['# vars : (' + ', '.join(str(x) for x in second_vars) + ')'])
    step_output_gates = []
    for i in range(len(first_vars)):
      self.eq_forall_var_gate(first_vars[i], second_vars[i])
      step_output_gates.append(self.output_gate)
    self.and_gate(step_output_gates)


  def add_untouched_prop_gates(self, tfun):
    # for each untouch propagation eq gates are generated:
    # We simply use noop untouched pairs as they cover all:
    for (predicate1, predicate2) in tfun.integer_tfun[-1][2]:
      # pre and post integer state variables:
      self.eq_gate(predicate1, predicate2)

  def gen_split_predicate_if_gate(self, i, split_predicates_forall_vars):
    bin_string = format(i,'0' + str(len(split_predicates_forall_vars)) + 'b')
    temp_condition = []
    for j in range(len(split_predicates_forall_vars)):
      if bin_string[j] == '0':
        temp_condition.append(-split_predicates_forall_vars[j])
      else:
        temp_condition.append(split_predicates_forall_vars[j])
    self.and_gate(temp_condition)

  # XXX
  def get_forall_vars_for_parameters(self, action_if_vars, parameter_map, obj_forall_vars):
    temp_type_list = []
    temp_forall_dict = {}
    forall_vars = []
    for parameter in action_if_vars[2]:
      temp_type_list.append(parameter_map[tuple(parameter)])
    for obj_type, count in Counter(temp_type_list).items():
      temp_forall_dict[obj_type] = obj_forall_vars[obj_type][:count]
    for parameter in action_if_vars[2]:
      # We get the corresponding forall variables for the parameter type:
      temp_forall_vars = temp_forall_dict[parameter_map[tuple(parameter)]].pop(0)
      forall_vars.append(temp_forall_vars)
    # Temp dictionary must be empty:
    for obj_type, var_list in temp_forall_dict.items():
      assert(len(var_list) == 0)
    return forall_vars

  def gen_parameter_forall_gates(self, forall_vars, parameter_vars):
    step_output_gates = []
    for i in range(len(parameter_vars)):
      self.eq_forall_vars_gate(forall_vars[i], parameter_vars[i])
      step_output_gates.append(self.output_gate)
    self.and_gate(step_output_gates)


  def temp_add_action_gates(self, tfun, splitvars_flag):
    aux_action_gates = []
    for ref_action in tfun.action_vars:
      self.transition_gates.append(['# Gate for action ' + ref_action[0] + str(ref_action[1]) + ':'])
      # if gate variable:
      main_action_if_var = tfun.av_inv_map[ref_action[0]]
      split_condition_output_gates = []
      for i in range(tfun.max_predicate_args+1):
        self.transition_gates.append(['# Split action with ' + str(i) + ' parameters:'])
        # split forall predicate if gate:
        if (splitvars_flag == 1):
          self.gen_split_predicate_if_gate(i, tfun.split_predicates_forall_vars)
          split_predicate_if_gate = self.output_gate
        step_output_gates = []
        all_untouched_predicates_pairs = []
        for base_parameter_type in tfun.predicate_types:
          step_type_output_gates = []
          step_type_parameter_output_gates = []
          untouched_predicate_pairs = []
          #print(base_parameter_type)
          # Finding split actions and generating if then gates,
          # along if conditions on parameters:
          for action in tfun.integer_tfun:
            if (tfun.av_inv_map[ref_action[0]] == action[0][0] and i == action[0][1]):
              #print(action)
              parameter_vars = action[0][2]
              temp_parameter_type_list = []
              for parameter_var in parameter_vars:
                temp_parameter_type_list.append(tfun.parameter_map[tuple(parameter_var)])
              if (base_parameter_type == tuple(temp_parameter_type_list)):
                self.transition_gates.append(['# Split action with parameters of ' + str(base_parameter_type) + ' type:'])
                # Generating all untouched propagation pairs:
                for cur_untouched_pair in action[3]:
                  if cur_untouched_pair not in all_untouched_predicates_pairs:
                    all_untouched_predicates_pairs.append(cur_untouched_pair)
                #print(base_parameter_type, tuple(temp_parameter_type_list))
                then_list = action[1]
                then_all_prop_list = []
                #print(untouched_predicate_pairs, action[3])
                untouched_predicate_pairs = list(action[3])
                for untouched_prop in action[2]:
                  then_list.append(self.untouched_prop_map[untouched_prop])
                if (parameter_vars):
                  forall_vars = self.get_forall_vars_for_parameters(action[0], tfun.parameter_map, tfun.obj_forall_vars)
                  self.gen_parameter_forall_gates(forall_vars, parameter_vars)
                  step_type_parameter_output_gates.append(self.output_gate)
                  if_parameter_output_gate = self.output_gate
                  self.and_gate(then_list)
                  then_output_gate = self.output_gate
                  self.if_then_gate(if_parameter_output_gate, then_output_gate)
                  step_type_output_gates.append(self.output_gate)
                else:
                  self.and_gate(then_list)
                  step_type_output_gates.append(self.output_gate)
          if (i != 0 and untouched_predicate_pairs):
            self.or_gate(step_type_parameter_output_gates)
            if_output_gate = self.output_gate
            out_then_list = []
            for predicate_pair in untouched_predicate_pairs:
              # Fetching untoched propagation gate:
              out_then_list.append(self.untouched_prop_map[predicate_pair])
            # We propagate only when no parameter is satisfied, hence, negative:
            self.if_then_gate(-if_output_gate, out_then_list)
            step_type_output_gates.append(self.output_gate)
          self.and_gate(step_type_output_gates)
          step_output_gates.append(self.output_gate)
        # If none of the parameters satisfy, we propogate the predicates:
        if (i != 0):
          then_list = []
          for predicate in tfun.predicate_dict[i]:
            base_predicate_pair = (tfun.sv_pre_inv_map[predicate], tfun.sv_post_inv_map[predicate])
            if base_predicate_pair not in all_untouched_predicates_pairs:
              #print(ref_action, base_predicate_pair)
              # Fetching untoched propagation gate:
              then_list.append(self.untouched_prop_map[base_predicate_pair])
          # We propagate only when no parameter is satisfied, hence, negative:
          self.and_gate(then_list)
          step_output_gates.append(self.output_gate)
        # Second main if block for each split branch :
        if(step_output_gates):
          if (splitvars_flag == 1):
            self.if_then_gate(split_predicate_if_gate, step_output_gates)
          else:
            self.and_gate(step_output_gates)
          split_condition_output_gates.append(self.output_gate)
      # Main if block for each action variable:
      self.if_then_gate(main_action_if_var, split_condition_output_gates)
      aux_action_gates.append(self.output_gate)
    self.transition_gates.append(['# final output action gate:'])
    self.and_gate(aux_action_gates)
    self.final_action_gate = self.output_gate



  # XXX there is a problem with propagation when some parameter is true and the action does not touch all the predicates
  # We need to make sure all the predicates propagate for every instantiation of forall variables.
  def add_action_gates(self, tfun, splitvars_flag):
    aux_action_gates = []
    for ref_action in tfun.action_vars:
      # if gate variable:
      main_action_if_var = tfun.av_inv_map[ref_action[0]]
      split_condition_output_gates = []
      for i in range(tfun.max_predicate_args+1):
        # split forall predicate if gate:
        if (splitvars_flag == 1):
          self.gen_split_predicate_if_gate(i, tfun.split_predicates_forall_vars)
          split_predicate_if_gate = self.output_gate
        step_parameter_output_gates = []
        step_output_gates = []
        # Finding split actions and generating if then gates,
        # along if conditions on parameters:
        for action in tfun.integer_tfun:
          if (tfun.av_inv_map[ref_action[0]] == action[0][0] and i == action[0][1]):
            parameter_vars = action[0][2]
            then_list = action[1]
            for untouched_prop in action[2]:
              then_list.append(self.untouched_prop_map[untouched_prop])
            if (parameter_vars):
              forall_vars = self.get_forall_vars_for_parameters(action[0], tfun.parameter_map, tfun.obj_forall_vars)
              self.gen_parameter_forall_gates(forall_vars, parameter_vars)
              step_parameter_output_gates.append(self.output_gate)
              if_parameter_output_gate = self.output_gate
              self.if_then_gate(if_parameter_output_gate, then_list)
              step_output_gates.append(self.output_gate)
            else:
              self.and_gate(then_list)
              step_output_gates.append(self.output_gate)

        # If none of the parameters satisfy, we propogate the predicates:
        if (i != 0):
          self.or_gate(step_parameter_output_gates)
          if_output_gate = self.output_gate
          then_list = []
          for predicate in tfun.predicate_dict[i]:
            # Fetching untoched propagation gate:
            then_list.append(self.untouched_prop_map[(tfun.sv_pre_inv_map[predicate], tfun.sv_post_inv_map[predicate])])
          # We propagate only when no parameter is satisfied, hence, negative:
          self.if_then_gate(-if_output_gate, then_list)
          step_output_gates.append(self.output_gate)
        # Second main if block for each split branch :
        if(step_output_gates):
          if (splitvars_flag == 1):
            self.if_then_gate(split_predicate_if_gate, step_output_gates)
          else:
            self.and_gate(step_output_gates)
          split_condition_output_gates.append(self.output_gate)
      # Main if block for each action variable:
      self.if_then_gate(main_action_if_var, split_condition_output_gates)
      aux_action_gates.append(self.output_gate)
    self.transition_gates.append(['# final output action gate:'])
    self.and_gate(aux_action_gates)
    self.final_action_gate = self.output_gate

  def add_amo_alo_gates(self, tfun):
    av_list = []
    for ref_action in tfun.action_vars:
      # if gate variable:
      av_list.append(tfun.av_inv_map[ref_action[0]])
    aux_amo_gates = []
    for i in range(len(av_list)):
      temp_av_list = list(av_list)
      if_gate = temp_av_list.pop(i)
      self.if_then_not_gate(if_gate, temp_av_list)
      aux_amo_gates.append(self.output_gate)
    self.transition_gates.append(['# final output AMO gate:'])
    self.and_gate(aux_amo_gates)
    amo_output_gate = self.output_gate

    self.transition_gates.append(['# ALO gate:'])
    self.or_gate(av_list)
    alo_output_gate = self.output_gate

    self.transition_gates.append(['# final output AMO ALO gate:'])
    self.and_gate([amo_output_gate, alo_output_gate])
    self.final_amoalo_gate = self.output_gate

    #for gate in self.transition_gates:
    #  print(gate)

  def add_final_gate(self):
    self.and_gate([self.final_action_gate, self.final_amoalo_gate])
    self.final_transition_gate = self.output_gate

  def __init__(self, tfun, splitvars_flag):
    self.transition_gates = []
    self.output_gate = 0 # output gate will never be zero
    self.next_gate = tfun.next_gate_var
    self.untouched_prop_map = {}
    self.final_action_gate = 0 # final action gate will never be zero
    self.final_amoalo_gate = 0 # final amo alo gate will never be zero
    self.final_transition_gate = 0 # final transition gate will never be zero

    self.transition_gates.append(['# Untouched Propagation gates:'])
    # Adding untouched propagation gates:
    self.add_untouched_prop_gates(tfun)

    self.transition_gates.append(['# Action gates:'])
    # Adding action gates:
    self.temp_add_action_gates(tfun, splitvars_flag)

    self.transition_gates.append(['# AMO ALO gates:'])
    # Adding AtMostOne and AtLeastOne gates:
    self.add_amo_alo_gates(tfun)

    self.transition_gates.append(['# Final transition gate:'])
    # Adding final transition gate:
    self.add_final_gate()
    self.total_gates = self.output_gate

  # XXX to be tested:
  def new_gate_gen(self, encoding, first_name, second_name, first_predicates, second_predicates, action_vars_list, forall_vars, split_forall_vars, aux_vars):

    # Appending variables for the new transition function:
    var_list = []

    var_list.extend(first_predicates)
    var_list.extend(second_predicates)

    for action_vars in action_vars_list:
      # main action variable:
      var_list.append(action_vars[0])
      # parameters of the action
      for parameter in action_vars[1]:
        var_list.extend(parameter)

    for obj_type_vars in forall_vars:
      for obj_vars in obj_type_vars:
        var_list.extend(obj_vars)
    var_list.extend(split_forall_vars)
    var_list.extend(aux_vars)


    encoding.append(['# Transition function from ' + first_name + ' to ' + second_name + ':'])
    encoding.append(['# ' + first_name + ' vars : (' + ', '.join(str(x) for x in first_predicates) + ')'])
    encoding.append(['# ' + second_name + ' vars : (' + ', '.join(str(x) for x in second_predicates) + ')'])
    encoding.append(['# Action vars with parameters:'])
    for action_vars in action_vars_list:
      main_action_var = action_vars[0]
      action_parameters = action_vars[1]
      encoding.append(['# Action variable:' + str(main_action_var)])
      encoding.append(['# Parameters:'])
      for parameter in action_parameters:
        parameter_string = ','.join(str(x) for x in parameter)
        encoding.append(['# ' + parameter_string])
    encoding.append(['# Forall variables:'])
    for obj_vars in forall_vars:
        obj_vars_string = ','.join(str(x) for x in obj_vars)
        encoding.append(['# ' + obj_vars_string])
    split_forall_vars_string = 'Split forall variables : ' + ','.join(str(x) for x in split_forall_vars)
    encoding.append(['# ' + split_forall_vars_string])

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
