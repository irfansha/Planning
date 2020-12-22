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
            ("./testcases/IPC4/Satellite/domain.pddl", "./testcases/IPC4/Satellite/prob02.pddl", 13)
            ]

def run_tests(plan_out):
    count = 0
    all_success = 1
    # Running testcases that have a plan:
    for testcase in sat_list:
      count += 1
      # Running testcase and generating plan (if available):
      command = 'python3 main.py -d ' + testcase[0] + ' -p ' + testcase[1] + ' -e UE --run 2 -k ' + str(testcase[2]) + ' --testing 0 --verbosity_level 0'
      plan_status = os.popen(command).read()
      print("\n--------------------------------------------------------------------------------")
      print("testcase" + str(count) + " :")
      print(testcase)
      if ('Plan found' in plan_status):
        # Validating the plan generated:
        Val_path = './tools/Validate'
        command = Val_path + ' ' + testcase[0] + ' ' + testcase[1] + ' ' + plan_out
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
    if (all_success):
      print("All tests successful")
    else:
      print("Test failed")