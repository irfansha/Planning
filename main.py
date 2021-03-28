# Irfansha Shaik, 21.09.2020, Aarhus.

'''
Todos:
  1. Rearrange arguments.
  2. Extraction in FE and CTE seems slow down the execution, perhaps
     it is possible to actually make it faster (by allowing to solve from both directions)
  3. Use operator splitting for SAT encoding (and other grounded encodings)
  4. Implement extraction for CTE, as it seems standard for QBF planning encodings.
  5. No need to wait until, intermediate unsat problems are solved better to move on before (and come back if needed).
  6. No need for external preprocessing with caqe as 2 preprocessors are internally available (thus removes extra steps in pipeline).
  7. Experiment with different options for each solver to optimise the solving.
  8. Handle equality requirement in the planning problems.
  9. Collect statistics for each encoding and solver (when plan is being computed).
  10. Implement explanatory frame axioms (including operator splitting) instead of classical frame axioms and add as an option.
  11. Extraction based on multiple calls to solver to be added (as the other extraction is slowing down the computation).
'''

import argparse, textwrap
from constraints import Constraints as cs
from ungrounded_constraints import UngroundedConstraints as ucs
from ungrounded_constraints_plus import UngroundedConstraintsPlus as ucsp
from generate_encoding import EncodingGen as eg
from run_solver import RunSolver as qs
from plan_extraction import ExtractPlan as pe
import plan_tester as pt
import run_tests as rt
import run_benchmarks as rb
import preprocess  as pre
import detype as dt
import time
import os

# Main:
if __name__ == '__main__':
  text = "A tool to encode PDDL (strips) problems to SAT/QBF encodings and compute a plan if exists"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("-V", "--version", help="show program version", action="store_true")
  parser.add_argument("-d", help="domain file path", default = 'testcases/competition/IPC2/Blocks/domain.pddl')
  parser.add_argument("--dd_out", help="detyped domain output file path", default = './detyped_domain')
  parser.add_argument("-p", help="problem file path", default = 'testcases/competition/IPC2/Blocks/prob01.pddl')
  parser.add_argument("--dp_out", help="detyped problem output file path", default = './detyped_problem')
  parser.add_argument("--dir", help="Benchmarks directory path", default = 'competition_benchmarks/IPC2/Elevator/')
  parser.add_argument("--de_type", type=int, help="detype domain and problem file [0/1], default 0",default = 0)
  parser.add_argument("--plan_out", help="plan output file path", default = 'cur_plan.txt')
  parser.add_argument("-k", type=int, help="path length",default = 4)
  parser.add_argument("--step", type=int, help="step value for k, in benchmarks, default 5",default = 5)
  parser.add_argument("-e", help=textwrap.dedent('''
                                  encoding types:
                                  SAT = Satisfiability
                                  M-seq = Madagascar SAT sequential encoding
                                  RE1  = Reachability Encoding 1
                                  RE2  = Reachability Encoding 2
                                  FE  = Flat Encoding
                                  CTE = Compact Tree Encoding
                                  UE = Ungrounded Encoding
                                  UE+ = Ungrounded encoding, also handling hierarchial types'''),default = 'UE+')
  parser.add_argument("-t", help="transition function with binary or linear action variables: [b l]",default = 'b')
  parser.add_argument("--run", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                               0 = only generate encoding
                               1 = test plan existence
                               2 = extract the plan in found
                               3 = extract the plan from preprocessed solution itself'''),default = 2)
  parser.add_argument("--testing", type=int, help=textwrap.dedent('''
                                          0 = no testing
                                          1 = internal testing with direct grounding, more memory required
                                          2 = external testing with VAL'''),default = 2)
  parser.add_argument("--splitvars", type=int, help="Turn split forall vars on: [0 = No 1 = Yes]",default = 0)
  parser.add_argument("--parameters_overlap", type=int, help="Turn reusing parameter vars for actions on: [0 = No 1 = Yes]",default = 0)
  parser.add_argument("--parameters_fold", type=int, help=textwrap.dedent('''
                                           "Turn reusing parameter vars with in each time step on: [0 = No 1 = Yes], default 0
                                            Experimental'''),default = 0)
  parser.add_argument("--fold_num", type=int, help="Number of max different variables to use, when parameters fold is on, default 10",default = 10)
  parser.add_argument("--encoding_out", help="output encoding file",default = 'encoding')
  parser.add_argument("--encoding_intermediate_out", help="output encoding file",default = 'intermediate_encoding')
  parser.add_argument("--encoding_type", type=int, help="Encoding type: [1 = QCIR14 2 = QDIMACS]",default = 2)
  parser.add_argument("--solver_out", help="solver output file",default = 'solver_output.txt')
  parser.add_argument("--solver_type", type=int, help=textwrap.dedent('''
                                       Solver type:
                                       0 = custom
                                       1 = quabs
                                       2 = caqe
                                       3 = dep-qbf
                                       4 = minisat
                                       5 = cryptominisat
                                       6 = pcaqe'''),default = 2)
  parser.add_argument("--verbosity_level", type=int, help=textwrap.dedent('''
                               Levels of verbosity:
                               0 = For testing, states if plan is correct.
                               1 = verbose'''),default = 1)
  parser.add_argument("--run_tests", type=int, help=textwrap.dedent('''
                               Levels running tests:
                               0 = no tests
                               1 = essential tests
                               2 = complete tests (may take a while!)'''),default = 0)
  parser.add_argument("--run_benchmarks", type=int, help="Run benchmarks, specify benchmarks directory using --dir", default=0)
  parser.add_argument("--time_limit", type=float, help="Time limit (excluding encoding time) in seconds, default 1800 seconds",default = 1800)
  parser.add_argument("--forall_pruning",type =int, help="[0/1]Avoiding search in unnecessary forall branches", default=0)
  parser.add_argument("--preprocessing", type = int, help=textwrap.dedent('''
                                       Preprocessing:
                                       0 = off
                                       1 = bloqqer (version 37)
                                       2 = bloqqer-internal caqe (version 37)'''),default = 0)
  parser.add_argument("--dependency_schemes",type =int, help="[0/1]enables dependency schemes if avaliable in solver", default=0)
  parser.add_argument("--preprocessed_encoding_out", help="File path to preprocessed encoding file", default = "preprocessed_encoding")
  parser.add_argument("--preprocessing_time_limit", type=int, help="Time limit in seconds, default 900 seconds",default = 900)
  args = parser.parse_args()



  print(args)

  # Asserting if detype is turned on when parameter fold is turned on:
  if (args.parameters_fold == 1):
    assert(args.de_type == 1)

  if args.version:
    print("Version 0.9")

  # If run tests enabled:
  if (args.run_tests != 0):
    rt.run_tests(args)
  # If run benchmarks enabled:
  elif (args.run_benchmarks != 0):
    rb.run(args)
  else:

    # If detype is set to 1, then we detype:
    if (args.de_type == 1):
      dt.detype(args.d, args.p, args.dd_out, args.dp_out)
      # after generating detyped files, we use them are source:
      args.d = args.dd_out
      args.p = args.dp_out

    # If not extracting plan, we dont test by default:
    if (args.run < 2):
      args.testing = 0
    # --------------------------------------- Timing the encoding ----------------------------------------
    start_encoding_time = time.perf_counter()

    # Extracting constraints from problem (expect for madagascar encoding):
    if (args.e == 'M-seq'):
      constraints_extract = []
    elif (args.e == 'UE'):
      constraints_extract = ucs(args.d, args.p, args.testing, args.verbosity_level)
    elif (args.e == "UE+"):
      constraints_extract = ucsp(args.d, args.p, args.testing, args.verbosity_level)
    else:
      constraints_extract = cs(args.d, args.p)


    encoding_gen = eg(constraints_extract, args)

    encoding_time = time.perf_counter() - start_encoding_time

    print("Encoding time: " + str(encoding_time))

    # ----------------------------------------------------------------------------------------------------

    # Preprocessing:
    if (args.preprocessing == 1):
      # Hanlding, if preprocessor runs out of time:
      args.preprocessing = pre.preprocess(args)

    if (int(args.run) >= 1):
      run_qs = qs(args)
      # --------------------------------------- Timing the solver run ----------------------------------------
      start_run_time = time.perf_counter()
      run_qs.runsolver()
      solving_time = time.perf_counter() - start_run_time
      print("Solving time: " + str(solving_time) + "\n")
      # ------------------------------------------------------------------------------------------------------

      # ------------------------------------- Printing memory stats of encodings -----------------------------
      print("Encoding size (in KB): " + str(os.path.getsize(args.encoding_out)/1000))
      if (args.preprocessing == 1):
        print("Preprocessed encoding size (in KB): " + str(os.path.getsize(args.preprocessed_encoding_out)/1000))

      # ------------------------------------------------------------------------------------------------------
      if run_qs.timed_out:
        exit()
      if run_qs.sat == -1:
        print("Memory out occurred\n")
        exit()
      if run_qs.sat:
        print("Plan found")
        # We do not extract a plan from Madagascar:
        if (args.e == "M-seq"):
          exit()
        if (args.run >= 2):
          plan_extract = pe(run_qs.sol_map, args.plan_out)
          if (args.e == 'CTE' or args.e == 'FE'):
            plan_extract.extract_action_based_plan(encoding_gen.encoding.extraction_action_vars_gen.states, constraints_extract, args.k)
          elif(args.e == 'UE' or args.e == 'UE+'):
            if (args.parameters_overlap == 0 and args.parameters_fold == 0):
              plan_extract.extract_ungrounded_plan(encoding_gen.encoding.action_with_parameter_vars, constraints_extract, args.k)
            else:
              plan_extract.extract_ungrounded_plan(encoding_gen.encoding.action_with_parameter_vars_with_overlap, constraints_extract, args.k)
          else:
            plan_extract.extract_qr_plan(encoding_gen.encoding.states_gen.states, constraints_extract, args.k)
          plan_extract.update_format()
          #if (args.verbosity_level != 0):
          plan_extract.print_updated_plan()
          plan_extract.print_to_file()
          if (args.testing == 1):
            pt.test_plan(plan_extract.plan, constraints_extract, args.e,  args.verbosity_level)
            pt.test_plan_with_val(args.d, args.p, args.plan_out, args.verbosity_level)
          if (args.testing == 2):
            pt.test_plan_with_val(args.d, args.p, args.plan_out,  args.verbosity_level)
      else:
        print('Plan not found')
