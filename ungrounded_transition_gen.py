# Irfansha Shaik, 16.11.2020, Aarhus.

'''
Todos:
  1. XXX
'''

from variable_dispatcher import VarDispatcher as vd
from gates_gen import UngroundedTransitionGatesGen as gg
import math

class UngroundedTransitionFunction():

  # Mapping state variables to 1,...,n where n is the number of predicates:
  def pre_map_gen(self, predicates):
    predicates_list = list(predicates)
    pre_map = {}
    pre_inv_map = {}
    for predicate in predicates_list:
      [int_var] = self.var_dis.get_vars(1)
      pre_map[int_var] = predicate
      pre_inv_map[predicate] = int_var
    return pre_map, pre_inv_map

  # Mapping state variables to n+1,...,n+n where n is the number of predicates:
  def post_map_gen(self, predicates):
    predicates_list = list(predicates)
    n = len(predicates)
    post_map = {}
    post_inv_map = {}
    for predicate in predicates_list:
      [int_var] = self.var_dis.get_vars(1)
      post_map[int_var] = predicate
      post_inv_map[predicate] = int_var
    return post_map, post_inv_map

  def action_map_gen(self, n, action_vars, bin_object_type_vars_dict):
    action_map = {}
    action_inv_map = {}
    parameter_map = {}
    for i in range(len(action_vars)):
      action_name_var = action_vars[i][0]
      [int_action_name_var] = self.var_dis.get_vars(1)
      action_map[int_action_name_var] = action_name_var
      action_inv_map[action_name_var] = int_action_name_var
      action_parameters = action_vars[i][1]
      for parameter in action_parameters:
        bin_action_var_list = self.var_dis.get_vars(bin_object_type_vars_dict[parameter[1]])
        action_map[tuple(bin_action_var_list)] = (action_name_var, parameter[0])
        action_inv_map[(action_name_var, parameter[0])] = bin_action_var_list
        parameter_map[tuple(bin_action_var_list)] = parameter[1]
    return action_map, action_inv_map, parameter_map

  def forall_vars_gen(self, forall_variables_type_dict, bin_object_type_vars_dict, max_predicate_args):
    for obj_type, count in forall_variables_type_dict.items():
      assert(count != -1)
      obj_bin_vars = []
      for i in range(count):
        temp_bin_vars = self.var_dis.get_vars(bin_object_type_vars_dict[obj_type])
        obj_bin_vars.append(temp_bin_vars)
      self.obj_forall_vars[obj_type] = obj_bin_vars
    # Forall variables for split predicates:
    num_binary_vars = math.ceil(math.log2(max_predicate_args+1))
    # handling log(1) = 0:
    if (num_binary_vars == 0):
      num_binary_vars = 1
    self.split_predicates_forall_vars = self.var_dis.get_vars(num_binary_vars)


  def __init__(self, constraints_extract, splitvars_flag):
    self.var_dis = vd()
    self.sv_pre_map, self.sv_pre_inv_map = self.pre_map_gen(constraints_extract.predicates)
    self.sv_post_map, self.sv_post_inv_map = self.post_map_gen(constraints_extract.predicates)
    self.num_predicates = len(constraints_extract.predicates)
    self.action_vars = constraints_extract.action_vars
    self.predicate_dict = constraints_extract.predicate_dict
    self.max_predicate_args = constraints_extract.max_predicate_args
    self.av_map, self.av_inv_map, self.parameter_map = self.action_map_gen(len(constraints_extract.predicates), constraints_extract.action_vars, constraints_extract.bin_object_type_vars_dict)
    self.obj_forall_vars = {}
    self.split_predicates_forall_vars = []
    self.forall_vars_gen(constraints_extract.forall_variables_type_dict, constraints_extract.bin_object_type_vars_dict, constraints_extract.max_predicate_args)
    [self.next_gate_var] = self.var_dis.get_vars(1)
    self.integer_tfun = self.integer_tfun_gen(constraints_extract.predicate_split_action_list, constraints_extract.predicates)
    self.gates_gen = gg(self, splitvars_flag)
    self.num_aux_vars = self.gates_gen.total_gates - self.next_gate_var + 1

  def integer_tfun_gen(self, action_list, predicates):
    int_tfun = []
    n = len(predicates)
    for i in range(len(action_list)):
      #print(action_list[i])
      # Generating pre and post literals in each action:
      current_predicates = []

      # Appending the positive preconditions as positive literals:
      for pos_pre in action_list[i].positive_preconditions:
        current_predicates.append(self.sv_pre_inv_map[pos_pre])

      # Appending the negative preconditions as negative literals:
      for neg_pre in action_list[i].negative_preconditions:
        current_predicates.append(-self.sv_pre_inv_map[neg_pre])

      # Appending the positive postconditions as positive literals:
      for pos_post in action_list[i].add_effects:
        current_predicates.append(self.sv_post_inv_map[pos_post])

      # Appending the negative postconditions as negative literals:
      for neg_post in action_list[i].del_effects:
        current_predicates.append(-self.sv_post_inv_map[neg_post])

      untouched_propagate_pairs = []
      for ut_pred in action_list[i].untouched_predicates:
        untouched_propagate_pairs.append((self.sv_pre_inv_map[ut_pred], self.sv_post_inv_map[ut_pred]))

      cur_parameters = []
      for parameter in action_list[i].parameters[1]:
        cur_parameters.append(self.av_inv_map[(action_list[i].name, parameter)])

      int_tfun.append([(self.av_inv_map[action_list[i].name], action_list[i].parameters[0] ,cur_parameters), current_predicates, untouched_propagate_pairs])
    return int_tfun
