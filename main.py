# Irfansha Shaik, 21.09.2020, Aarhus.

'''
Todos:
  1. XXX
'''

import argparse, textwrap
from constraints import Constraints as cs
from transition_gen import TransitionFunction as tfl
from transition_gen_withoutamoalo import TransitionFunction as tfb
from sat_encoding_gen import SatEncoding as se
from qr_encoding_gen import QREncoding as qr
from qbf_intermediate_encoding import QIEncoding as qi
from ctencoding import CTEncoding as cte
from run_quabs import Quabs as qb
import plan_tester as pt

# Main:
if __name__ == '__main__':
  text = "A tool to encode PDDL (strips) problems to SAT/QBF encodings and compute a plan if exists"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("-V", "--version", help="show program version", action="store_true")
  parser.add_argument("-d", help="domain file path", default = 'testcases/dinner/dinner.pddl')
  parser.add_argument("-p", help="problem file path", default = 'testcases/dinner/pb1.pddl')
  parser.add_argument("-k", type=int, help="path length",default = 4)
  parser.add_argument("-e", help=textwrap.dedent('''
                                  encoding types:
                                  SAT = Satisfiability
                                  QI  = QBF intermediate
                                  QR  = QBF reachbility
                                  CTE = Compact Tree Encoding'''),default = 'QI')
  parser.add_argument("-t", help="transition function with binary or linear action variables: [b l]",default = 'b')
  parser.add_argument("--run", help=textwrap.dedent('''
                               Three levels of execution:
                               0 = only generate encoding
                               1 = test plan existence
                               2 = extract the plan in found'''),default = 2)
  parser.add_argument("--encoding_out", help="output encoding file",default = 'encoding.qcir')
  parser.add_argument("--solver_out", help="solver output file",default = 'solver_output.txt')
  parser.add_argument("--solver", help="solver path",default = './quabs')
  args = parser.parse_args()


  if args.version:
    print("Version 0.7.0")

  # Extracting constraints from problem:
  constraints_extract = cs(args.d, args.p)
  # Generating transition function:
  if (args.t == 'l'):
    tfun = tfl(constraints_extract)
  elif (args.t == 'b'):
    tfun = tfb(constraints_extract)

  if (args.e == 'SAT'):
    encoding = se(constraints_extract, tfun, args.k)
  elif (args.e == 'QR'):
    encoding = qr(constraints_extract, tfun, args.k)
  elif (args.e == 'QI'):
    encoding = qi(constraints_extract, tfun, args.k)
  elif (args.e == 'CTE'):
    if (args.run == '2'):
      encoding = cte(constraints_extract, tfun, args.k, 1)
    else:
      encoding = cte(constraints_extract, tfun, args.k, 0)
  else:
    print('no encoding generated')
    exit()

  encoding.print_encoding_tofile(args.encoding_out)
  print("Encoding generated")

  if (int(args.run) >= 1):
    run_qb = qb(args.encoding_out, args.solver_out, args.solver)
    run_qb.run()
    run_qb.parse_quabs_output()
    if run_qb.sat:
      print("Plan found")
      if (args.run == '2'):
        if (args.e == 'CTE'):
          run_qb.extract_action_based_plan(encoding.extraction_action_vars_gen.states, constraints_extract, args.k)
        else:
          run_qb.extract_qr_plan(encoding.states_gen.states, constraints_extract, tfun.num_state_vars, args.k)
        run_qb.print_plan()
        pt.test_plan(run_qb.plan, constraints_extract)
    else:
      print('plan not found')
