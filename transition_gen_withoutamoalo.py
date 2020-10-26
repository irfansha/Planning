# Irfansha Shaik, 23.09.2020, Aarhus.

'''
Todos:
  1. Update the transition function such that, it does not need additional action variables
     instead it uses numbering of action variables and avoid amo alo clauses.
     Perhaps, it is better to add a different transition function class.
'''

from gates_gen import TransitionGatesGenWithoutAmoAlo as gg

class TransitionFunction():

  # Mapping state variables to 1,...,n where n is the number of state variables:
  def pre_map_gen(self, state_vars):
    pre_map = {}
    pre_inv_map = {}
    for i in range(len(state_vars)):
      pre_map[i+1] = state_vars[i]
      pre_inv_map[tuple(state_vars[i])] = i+1
    return pre_map, pre_inv_map

  # Mapping state variables to n+1,...,n+n where n is the number of state variables:
  def post_map_gen(self, state_vars):
    n = len(state_vars)
    post_map = {}
    post_inv_map = {}
    for i in range(len(state_vars)):
      post_map[n+i+1] = state_vars[i]
      post_inv_map[tuple(state_vars[i])] = n+i+1
    return post_map, post_inv_map

  def action_map_gen(self, n, action_vars):
    action_map = {}
    action_inv_map = {}
    for i in range(len(action_vars)):
      action_map[(2*n)+i+1] = action_vars[i]
      action_inv_map[tuple(action_vars[i])] = (2*n)+i+1
    return action_map, action_inv_map

  def __init__(self, constraints_extract):
    self.sv_pre_map, self.sv_pre_inv_map = self.pre_map_gen(constraints_extract.state_vars)
    self.sv_post_map, self.sv_post_inv_map = self.post_map_gen(constraints_extract.state_vars)
    self.av_map, self.av_inv_map = self.action_map_gen(len(constraints_extract.state_vars), constraints_extract.action_vars)
    self.num_state_vars = len(constraints_extract.state_vars)
    self.num_aux_action_vars = len(constraints_extract.action_vars)
    self.aux_action_vars = list(self.av_map.keys())
    self.integer_tfun = self.integer_tfun_gen(constraints_extract.action_list, constraints_extract.state_vars)
    self.gates_gen = gg(self)
    self.action_vars = self.gates_gen.binary_action_vars
    self.num_action_vars = self.gates_gen.num_binary_action_vars
    self.num_aux_vars = self.gates_gen.total_gates - (2*self.num_state_vars + self.num_action_vars)

  def integer_tfun_gen(self, action_list, state_vars):
    int_tfun = []
    n = len(state_vars)
    for i in range(len(action_list)):
      touched_vars = []
      #print(action_list[i])
      # Generating pre and post literals in each action:
      current_state_literals = []
      #print(action_list[i].positive_preconditions)

      # Appending the positive preconditions as positive literals:
      for pos_pre in action_list[i].positive_preconditions:
        current_state_literals.append(self.sv_pre_inv_map[tuple(pos_pre)])

      # Appending the negative preconditions as negative literals:
      for neg_pre in action_list[i].negative_preconditions:
        current_state_literals.append(-self.sv_pre_inv_map[tuple(neg_pre)])

      # Appending the positive postconditions as positive literals:
      for pos_post in action_list[i].add_effects:
        if pos_post not in touched_vars:
          touched_vars.append(pos_post)
        current_state_literals.append(self.sv_post_inv_map[tuple(pos_post)])

      # Appending the negative postconditions as negative literals:
      for neg_post in action_list[i].del_effects:
        if neg_post not in touched_vars:
          touched_vars.append(neg_post)
        current_state_literals.append(-self.sv_post_inv_map[tuple(neg_post)])

      untouched_propagate_pairs = []
      for j in range(len(state_vars)):
        if state_vars[j] not in touched_vars:
          untouched_propagate_pairs.append((j+1, j+1+n))
          assert(self.sv_pre_map[j+1] == self.sv_post_map[j+1+n])

      int_tfun.append([self.av_inv_map[action_list[i].name,tuple(action_list[i].parameters)], current_state_literals, untouched_propagate_pairs])

    return int_tfun
