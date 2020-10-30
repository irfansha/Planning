# Irfansha Shaik, 21.09.2020, Aarhus.

'''
Todos:
  1. Extraction in FE and CTE seems slow down the execution, perhaps
     it is possible to actually make it faster (by allowing to solve from both directions)
'''

import argparse, textwrap
from constraints import Constraints as cs
from generate_encoding import EncodingGen as eg
from run_solver import RunSolver as qs
from plan_extraction import ExtractPlan as pe
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
                                  QI  = QBF Intermediate
                                  QR  = QBF Reachability
                                  FE  = Flat Encoding
                                  CTE = Compact Tree Encoding'''),default = 'QI')
  parser.add_argument("-t", help="transition function with binary or linear action variables: [b l]",default = 'b')
  parser.add_argument("--run", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                               0 = only generate encoding
                               1 = test plan existence
                               2 = extract the plan in found'''),default = 2)
  parser.add_argument("--encoding_out", help="output encoding file",default = 'encoding.qcir')
  parser.add_argument("--encoding_type", type=int, help="Encoding type: [1 = QCIR14 2 = QDIMACS]",default = 1)
  parser.add_argument("--solver_out", help="solver output file",default = 'solver_output.txt')
  parser.add_argument("--solver_type", type=int, help=textwrap.dedent('''
                                       Solver type:
                                       0 = custom
                                       1 = quabs
                                       2 = caqe'''),default = 1)
  parser.add_argument("--custom_solver_path", help="custom solver path",default = './solvers/qbf/quabs')
  args = parser.parse_args()


  if args.version:
    print("Version 0.8.5")

  # Extracting constraints from problem:
  constraints_extract = cs(args.d, args.p)

  encoding_gen = eg(constraints_extract, args)

  if (int(args.run) >= 1):
    run_qs = qs(args.encoding_out, args.solver_out, args.solver_type, args.custom_solver_path)
    run_qs.run()
    if run_qs.sat:
      print("Plan found")
      if (args.run == 2):
        plan_extract = pe(run_qs.sol_map)
        if (args.e == 'CTE' or args.e == 'FE'):
          plan_extract.extract_action_based_plan(encoding_gen.encoding.extraction_action_vars_gen.states, constraints_extract, args.k)
        else:
          plan_extract.extract_qr_plan(encoding_gen.encoding.states_gen.states, constraints_extract, args.k)
        plan_extract.print_plan()
        pt.test_plan(plan_extract.plan, constraints_extract)
    else:
      print('plan not found')
