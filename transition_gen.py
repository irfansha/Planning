# Irfansha Shaik, 23.09.2020, Aarhus.

'''
Todos:
  1. XXX
'''

class TransitionFunction():

  # Mapping state variables to 1,...,n where n is the number of state variables:
  def pre_map_gen(self, state_vars):
    pre_map = {}
    for i in range(len(state_vars)):
      pre_map[i+1] = state_vars[i]
    return pre_map

  # Mapping state variables to n+1,...,n+n where n is the number of state variables:
  def post_map_gen(self, state_vars):
    n = len(state_vars)
    post_map = {}
    for i in range(len(state_vars)):
      post_map[n+i+1] = state_vars[i]
    return post_map

  def action_map_gen(self, n, action_vars):
    action_map = {}
    for i in range(len(action_vars)):
      action_map[(2*n)+i+1] = action_vars[i]
    return action_map

  def __init__(self, state_vars, action_vars, action_list):
    self.state_vars_pre_map = self.pre_map_gen(state_vars)
    self.state_vars_post_map = self.post_map_gen(state_vars)
    self.action_vars_map = self.action_map_gen(len(state_vars), action_vars)
