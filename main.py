# Irfansha Shaik, 21.09.2020, Aarhus.

'''
Todos:
  1. Refine actions list into intergers
'''

import sys
import constraints as cs
from transition_gen import TransitionFunction as tf

# Main:
if __name__ == '__main__':
  #start_time = time.time()
  domain = sys.argv[1]
  problem = sys.argv[2]
  k = int(sys.argv[3])
  initial_state, goal_state, action_list = cs.constraints(domain, problem)

  state_vars = cs.extract_state_vars(initial_state, goal_state, action_list)
  state_vars.sort()

  action_vars = cs.extract_action_vars(action_list)
  #print(action_vars)
  #print(state_vars)

  transition_gen = tf(state_vars, action_vars, action_list)

  #print(transition_gen.state_vars_pre_map)
  #print(transition_gen.state_vars_post_map)
  #print(transition_gen.action_vars_map)
