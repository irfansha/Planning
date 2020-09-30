# Irfansha Shaik, 21.09.2020, Aarhus.

'''
Todos:
  1. Add unit testcases for transition gates generator functions.
'''

import sys
from constraints import Constraints as cs
from transition_gen import TransitionFunction as tf

# Main:
if __name__ == '__main__':
  #start_time = time.time()
  domain = sys.argv[1]
  problem = sys.argv[2]
  k = int(sys.argv[3])
  constraints_extract = cs(domain, problem)

  transition_fun = tf(constraints_extract)
