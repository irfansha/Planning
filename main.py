# Irfansha Shaik, 21.09.2020, Aarhus.

'''
Todos:
  1. Add unit testcases for transition gates generator functions.
'''

import sys
from constraints import Constraints as cs
from transition_gen import TransitionFunction as tf
from sat_encoding_gen import SatEncoding as se
from run_quabs import Quabs as qb

# Main:
if __name__ == '__main__':
  #start_time = time.time()
  domain = sys.argv[1]
  problem = sys.argv[2]
  k = int(sys.argv[3])
  encoding = sys.argv[4]
  encoding_file_path = sys.argv[5]
  output_file_path = sys.argv[6]
  solver_path = sys.argv[7]

  # Extracting constraints from problem:
  constraints_extract = cs(domain, problem)
  # Generating transition function:
  tfun = tf(constraints_extract)

  if (encoding == 'SAT'):
    sat_encoding = se(constraints_extract, tfun, k)
    sat_encoding.print_encoding_tofile(encoding_file_path)
    run_qb = qb(encoding_file_path, output_file_path, solver_path)
    run_qb.run()
    run_qb.parse_quabs_output()
    if run_qb.sat:
      run_qb.extract_plan(sat_encoding.action_vars, constraints_extract.action_vars)
      run_qb.print_plan()
    else:
      print('plan not found')
