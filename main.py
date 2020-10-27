# Irfansha Shaik, 21.09.2020, Aarhus.

'''
Todos:
  1. XXX
'''

import argparse
from constraints import Constraints as cs
from transition_gen import TransitionFunction as tf
#from transition_gen_withoutamoalo import TransitionFunction as tf
from sat_encoding_gen import SatEncoding as se
from qr_encoding_gen import QREncoding as qr
from qbf_intermediate_encoding import QIEncoding as qi
from ctencoding import CTEncoding as cte
from run_quabs import Quabs as qb
import plan_tester as pt

# Main:
if __name__ == '__main__':
  text = "A tool to encode PDDL (strips) problems to SAT/QBF encodings and compute a plan if exists"
  parser = argparse.ArgumentParser(description=text)
  parser.add_argument("-V", "--version", help="show program version", action="store_true")
  parser.add_argument("-d", help="domain file path")
  parser.add_argument("-p", help="problem file path")
  parser.add_argument("-k", help="path length",default = 4)
  parser.add_argument("-e", help="encoding",default = 'QI')
  parser.add_argument("--encoding_out", help="output encoding file",default = 'encoding.qcir')
  parser.add_argument("--solver_out", help="solver output file",default = 'solver_output.txt')
  parser.add_argument("--solver", help="solver path",default = './quabs')
  args = parser.parse_args()


  if args.version:
    print("Version 0.7.0")

  # Extracting constraints from problem:
  constraints_extract = cs(args.d, args.p)
  # Generating transition function:
  tfun = tf(constraints_extract)

  if (args.e == 'SAT'):
    sat_encoding = se(constraints_extract, tfun, args.k)
    sat_encoding.print_encoding_tofile(args.encoding_out)
    run_qb = qb(args.encoding_out, args.solver_out, args.solver)
    run_qb.run()
    run_qb.parse_quabs_output()
    if run_qb.sat:
      #run_qb.extract_plan(sat_encoding.action_vars, constraints_extract.action_vars)
      run_qb.extract_qr_plan(sat_encoding.states_gen.states, constraints_extract, tfun.num_state_vars, args.k)
      run_qb.print_plan()
      pt.test_plan(run_qb.plan, constraints_extract)
    else:
      print('plan not found')
  elif (args.e == 'QR'):
    qr_encoding = qr(constraints_extract, tfun, args.k)
    qr_encoding.print_encoding_tofile(args.encoding_out)

    #qr_encoding.print_encoding()
    run_qb = qb(args.encoding_out, args.solver_out, args.solver)
    run_qb.run()
    run_qb.parse_quabs_output()
    if run_qb.sat:
      run_qb.extract_qr_plan(qr_encoding.states_gen.states, constraints_extract, tfun.num_state_vars, args.k)
      run_qb.print_plan()
      pt.test_plan(run_qb.plan, constraints_extract)
    else:
      print('plan not found')
  elif (args.e == 'QI'):
    qi_encoding = qi(constraints_extract, tfun, args.k)
    qi_encoding.print_encoding_tofile(args.encoding_out)
    run_qb = qb(args.encoding_out, args.solver_out, args.solver)
    run_qb.run()
    run_qb.parse_quabs_output()
    if run_qb.sat:
      run_qb.extract_qr_plan(qi_encoding.states_gen.states, constraints_extract, tfun.num_state_vars, args.k)
      run_qb.print_plan()
      pt.test_plan(run_qb.plan, constraints_extract)
    else:
      print('plan not found')
  elif (args.e == 'CTE'):
    ct_encoding = cte(constraints_extract, tfun, args.k)
    ct_encoding.print_encoding_tofile(args.encoding_out)
    run_qb = qb(args.encoding_out, args.solver_out, args.solver)
    run_qb.run()
    run_qb.parse_quabs_output()
    if run_qb.sat:
      print("plan found")
      '''
      run_qb.extract_qr_plan(qi_encoding.states_gen.states, constraints_extract, tfun.num_state_vars, args.k)
      run_qb.print_plan()
      pt.test_plan(run_qb.plan, constraints_extract)
      '''
    else:
      print('plan not found')
