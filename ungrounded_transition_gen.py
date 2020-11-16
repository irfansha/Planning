# Irfansha Shaik, 16.11.2020, Aarhus.

'''
Todos:
  1. XXX
'''

from variable_dispatcher import VarDispatcher as vd
#from gates_gen import TransitionGatesGen as gg

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
    return action_map, action_inv_map

  def __init__(self, constraints_extract):
    self.var_dis = vd()
    self.sv_pre_map, self.sv_pre_inv_map = self.pre_map_gen(constraints_extract.predicates)
    self.sv_post_map, self.sv_post_inv_map = self.post_map_gen(constraints_extract.predicates)
    
    self.av_map, self.av_inv_map = self.action_map_gen(len(constraints_extract.predicates), constraints_extract.action_vars, constraints_extract.bin_object_type_vars_dict)
    self.integer_tfun = self.integer_tfun_gen(constraints_extract.predicate_split_action_list, constraints_extract.predicates)
    #self.gates_gen = gg(self)
    #self.num_aux_vars = self.gates_gen.total_gates - (2*self.num_predicates + self.num_action_vars)

  # XXX
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

      int_tfun.append([self.av_inv_map[action_list[i].name], cur_parameters, current_predicates, untouched_propagate_pairs])

    for i in range(len(int_tfun)):
      print(int_tfun[i])
    return int_tfun
