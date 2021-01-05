import os


competition_testcase_path = "./testcases/competition/"

competition_sat_list = [("IPC1/gripper/", "prob01.pddl", 11), ("IPC1/movie/", "prob01.pddl", 7),
                        ("IPC1/movie/", "prob02.pddl", 7),
                        ("IPC2/Blocks/", "prob01.pddl", 6), ("IPC2/Blocks/", "prob02.pddl",12),
                        ("IPC2/Elevator/", "prob01.pddl", 4), ("IPC2/Elevator/", "prob02.pddl", 10),
                        ("IPC3/DriverLog/", "prob01.pddl", 7), ("IPC3/ZenoTravel/", "prob01.pddl", 1),
                        ("IPC3/ZenoTravel/", "prob02.pddl", 6),
                        ("IPC4/Satellite/", "prob01.pddl", 9), ("IPC4/Satellite/", "prob02.pddl", 13),
                        ("IPC5/Rovers/", "prob01.pddl", 10), ("IPC5/Rovers/", "prob02.pddl", 8)]

competition_unsat_list = [("IPC1/gripper/", "prob01.pddl", 10), ("IPC1/movie/", "prob01.pddl", 6),
                          ("IPC1/movie/", "prob02.pddl", 6),
                          ("IPC2/Blocks/", "prob01.pddl", 5), ("IPC2/Blocks/", "prob02.pddl",11),
                          ("IPC2/Elevator/", "prob01.pddl", 3), ("IPC2/Elevator/", "prob02.pddl", 9),
                          ("IPC3/DriverLog/", "prob01.pddl", 6), ("IPC3/ZenoTravel/", "prob01.pddl", 0), ("IPC3/ZenoTravel/", "prob02.pddl", 5),
                          ("IPC4/Satellite/", "prob01.pddl", 8), ("IPC4/Satellite/", "prob02.pddl", 12),
                          ("IPC5/Rovers/", "prob01.pddl", 9), ("IPC5/Rovers/", "prob02.pddl", 7)]

classical_testcase_path = "./testcases/classical/"

classical_sat_list = [("ipc1998/untyped/gripper/", "prob01.pddl",11), ("ipc1998/untyped/movie/", "prob01.pddl",7),
                      #("ipc1998/untyped/mystery/", "prob01.pddl", 5),
                      ("ipc2000/typed/elevators-00-strips/", "prob01.pddl", 4), ("ipc2000/typed/elevators-00-strips/", "prob02.pddl", 7),
                      ("ipc2000/untyped/blocks/", "prob01.pddl", 6),
                      ("ipc2000/untyped/blocks-3op/", "prob01.pddl", 0),
                      #("ipc2000/untyped/logistics00/", "prob01.pddl", 20)
                      ("ipc2002/untyped/depot/", "prob01.pddl", 10),
                      ("ipc2002/untyped/driverlog/", "prob01.pddl", 7),
                      #("ipc2002/untyped/rovers-02/", "prob01.pddl", 11),
                      ("ipc2002/untyped/zenotravel/", "prob01.pddl", 1)]



def gen_new_arguments(domain, problem, k, args):
  new_command = ''
  for arg in vars(args):
    # We set these separately:
    if (arg == 'version'):
      continue
    elif (arg == 'd'):
      new_command += ' -d ' + domain
    elif(arg == 'p'):
      new_command += ' -p ' + problem
    elif(arg == 'k'):
      new_command += ' -k ' + str(k)
    elif(arg == "testing"):
      new_command += ' --testing 0'
    elif(arg == "verbosity_level"):
      new_command += ' --verbosity_level 0'
    elif( arg == "run_tests"):
      new_command += ' --run_tests 0'
    elif (len(arg) == 1):
      new_command += ' -' + str(arg) + ' ' + str(getattr(args, arg))
    else:
      new_command += ' --' + str(arg) + ' ' + str(getattr(args, arg))
  return(new_command)


def run_tests(args):
    count = 0
    all_success = 1
    # Running testcases that have a plan:
    for testcase in competition_sat_list:
      count += 1
      print("\n--------------------------------------------------------------------------------")
      print("testcase" + str(count) + " :")
      domain = competition_testcase_path + testcase[0] + 'domain.pddl'
      problem = competition_testcase_path + testcase[0] + testcase[1]
      print(domain, problem, testcase[2])
      # domain and problem files (and k) are new:
      command_arguments = gen_new_arguments(domain, problem, testcase[2], args)
      # Running testcase and generating plan (if available):
      command = 'python3 main.py ' + command_arguments
      plan_status = os.popen(command).read()
      print(plan_status)
      if (args.run == 1):
        print("Testing only existence")
        if ('Plan found' in plan_status):
          print("success")
        else:
          # plan failed:
          all_success = 0
          print("failed! plan must exist")
      elif ('Plan found' in plan_status):
        # Validating the plan generated:
        Val_path = './tools/Validate'
        command = Val_path + ' ' + domain + ' ' + problem + ' ' + args.plan_out
        testing_status = os.popen(command).read()
        if ("Plan valid" not in testing_status):
          print("failed")
          # plan failed:
          all_success = 0
          exit()
        else:
          print("success")
      else:
          print("failed! plan must exist")
          # plan failed:
          all_success = 0
      print("--------------------------------------------------------------------------------\n")
    # Running testcases that have a plan:
    for testcase in classical_sat_list:
      count += 1
      print("\n--------------------------------------------------------------------------------")
      print("testcase" + str(count) + " :")
      domain = classical_testcase_path + testcase[0] + 'domain.pddl'
      problem = classical_testcase_path + testcase[0] + testcase[1]
      print(domain, problem, testcase[2])
      # domain and problem files (and k) are new:
      command_arguments = gen_new_arguments(domain, problem, testcase[2], args)
      # Running testcase and generating plan (if available):
      command = 'python3 main.py ' + command_arguments
      plan_status = os.popen(command).read()
      print(plan_status)
      if (args.run == 1):
        print("Testing only existence")
        if ('Plan found' in plan_status):
          print("success")
        else:
          # plan failed:
          all_success = 0
          print("failed! plan must exist")
      elif ('Plan found' in plan_status):
        # Validating the plan generated:
        Val_path = './tools/Validate'
        command = Val_path + ' ' + domain + ' ' + problem + ' ' + args.plan_out
        testing_status = os.popen(command).read()
        if ("Plan valid" not in testing_status):
          print("failed")
          # plan failed:
          all_success = 0
          exit()
        else:
          print("success")
      else:
          print("failed! plan must exist")
          # plan failed:
          all_success = 0
      print("--------------------------------------------------------------------------------\n")

    # Running unsat testcases:
    for testcase in competition_unsat_list:
      count += 1
      print("\n--------------------------------------------------------------------------------")
      print("testcase" + str(count) + " :")
      domain = competition_testcase_path + testcase[0] + 'domain.pddl'
      problem = competition_testcase_path + testcase[0] + testcase[1]
      print(domain, problem, testcase[2])
      # domain and problem files (and k) are new:
      command_arguments = gen_new_arguments(domain, problem, testcase[2], args)
      # Running testcase and generating plan (if available):
      command = 'python3 main.py ' + command_arguments
      plan_status = os.popen(command).read()
      print(plan_status)
      if ('Plan not found' in plan_status):
        print("success")
      else:
        # plan failed:
        all_success = 0
        print("failed! plan must not exist")
      print("--------------------------------------------------------------------------------\n")

    if (all_success):
      print("All tests successful")
    else:
      print("Test failed")