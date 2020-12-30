import os


sat_list = [("./testcases/IPC1/gripper/domain.pddl", "./testcases/IPC1/gripper/prob01.pddl", 11),
            ("./testcases/IPC1/movie/domain.pddl", "./testcases/IPC1/movie/prob01.pddl", 7),
            ("./testcases/IPC1/movie/domain.pddl", "./testcases/IPC1/movie/prob02.pddl", 7),
            ("./testcases/IPC2/Blocks/domain.pddl", "./testcases/IPC2/Blocks/prob01.pddl", 6),
            ("./testcases/IPC2/Blocks/domain.pddl", "./testcases/IPC2/Blocks/prob02.pddl",12),
            ("./testcases/IPC2/Elevator/domain.pddl", "./testcases/IPC2/Elevator/prob01.pddl", 4),
            ("./testcases/IPC2/Elevator/domain.pddl", "./testcases/IPC2/Elevator/prob02.pddl", 10),
            ("./testcases/IPC3/DriverLog/domain.pddl", "./testcases/IPC3/DriverLog/prob01.pddl", 7),
            ("./testcases/IPC3/ZenoTravel/domain.pddl", "./testcases/IPC3/ZenoTravel/prob01.pddl", 1),
            ("./testcases/IPC3/ZenoTravel/domain.pddl", "./testcases/IPC3/ZenoTravel/prob02.pddl", 6),
            ("./testcases/IPC4/Satellite/domain.pddl", "./testcases/IPC4/Satellite/prob01.pddl", 9),
            ("./testcases/IPC4/Satellite/domain.pddl", "./testcases/IPC4/Satellite/prob02.pddl", 13),
            ("./testcases/IPC5/Rovers/domain.pddl", "./testcases/IPC5/Rovers/prob01.pddl", 10),
            ("./testcases/IPC5/Rovers/domain.pddl", "./testcases/IPC5/Rovers/prob02.pddl", 8)
            ]

unsat_list = [("./testcases/IPC1/gripper/domain.pddl", "./testcases/IPC1/gripper/prob01.pddl", 10),
            ("./testcases/IPC1/movie/domain.pddl", "./testcases/IPC1/movie/prob01.pddl", 6),
            ("./testcases/IPC1/movie/domain.pddl", "./testcases/IPC1/movie/prob02.pddl", 6),
            ("./testcases/IPC2/Blocks/domain.pddl", "./testcases/IPC2/Blocks/prob01.pddl", 5),
            ("./testcases/IPC2/Blocks/domain.pddl", "./testcases/IPC2/Blocks/prob02.pddl",11),
            ("./testcases/IPC2/Elevator/domain.pddl", "./testcases/IPC2/Elevator/prob01.pddl", 3),
            ("./testcases/IPC2/Elevator/domain.pddl", "./testcases/IPC2/Elevator/prob02.pddl", 9),
            ("./testcases/IPC3/DriverLog/domain.pddl", "./testcases/IPC3/DriverLog/prob01.pddl", 6),
            ("./testcases/IPC3/ZenoTravel/domain.pddl", "./testcases/IPC3/ZenoTravel/prob01.pddl", 0),
            ("./testcases/IPC3/ZenoTravel/domain.pddl", "./testcases/IPC3/ZenoTravel/prob02.pddl", 5),
            ("./testcases/IPC4/Satellite/domain.pddl", "./testcases/IPC4/Satellite/prob01.pddl", 8),
            ("./testcases/IPC4/Satellite/domain.pddl", "./testcases/IPC4/Satellite/prob02.pddl", 12),
            ("./testcases/IPC5/Rovers/domain.pddl", "./testcases/IPC5/Rovers/prob01.pddl", 9),
            ("./testcases/IPC5/Rovers/domain.pddl", "./testcases/IPC5/Rovers/prob02.pddl", 7)
            ]


def run_tests(args):
    count = 0
    all_success = 1
    # Running testcases that have a plan:
    for testcase in sat_list:
      count += 1
      print("\n--------------------------------------------------------------------------------")
      print("testcase" + str(count) + " :")
      print(testcase)
      # Running testcase and generating plan (if available):
      command = 'python3 main.py -d ' + testcase[0] + ' -p ' + testcase[1] + ' -e ' + args.e + ' --forall_pruning ' + str(args.forall_pruning) + ' --run 2 -k ' + str(testcase[2]) + ' --testing 0 --verbosity_level 0 --run ' + str(args.run) + ' --preprocessing ' + str(args.preprocessing) + ' --preprocessing_time_limit ' + str(args.preprocessing_time_limit) + ' --time_limit ' + str(args.time_limit) + ' --parameters_overlap ' + str(args.parameters_overlap) + ' --solver_type ' + str(args.solver_type)
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
        command = Val_path + ' ' + testcase[0] + ' ' + testcase[1] + ' ' + args.plan_out
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
    for testcase in unsat_list:
      count += 1
      print("\n--------------------------------------------------------------------------------")
      print("testcase" + str(count) + " :")
      print(testcase)
      # Running testcase and generating plan (if available):
      command = 'python3 main.py -d ' + testcase[0] + ' -p ' + testcase[1] + ' -e ' + args.e + ' --forall_pruning ' + str(args.forall_pruning) + ' --run 2 -k ' + str(testcase[2]) + ' --testing 0 --verbosity_level 0 --run ' + str(args.run) + ' --preprocessing ' + str(args.preprocessing) + ' --preprocessing_time_limit ' + str(args.preprocessing_time_limit) + ' --time_limit ' + str(args.time_limit) + ' --parameters_overlap ' + str(args.parameters_overlap) + ' --solver_type ' + str(args.solver_type)
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