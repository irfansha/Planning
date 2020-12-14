# Irfansha Shaik, 05.10.2020, Aarhus

'''
Todos:
  1. For Ungrounded planning, it is possible to test without grounding
'''
import os

def test_plan(plan, constraints, encoding):
  if (encoding == 'UE'):
    initial_state = constraints.test_initial_state
    goal_state = constraints.test_goal_state
    action_list = constraints.test_action_list
  else:
    initial_state = constraints.initial_state
    goal_state = constraints.goal_state
    action_list = constraints.action_list
  print("\nTesting plan: ")
  current_state = []
  temp_pos_var = []
  temp_neg_var = []
  for state_var in constraints.state_vars:
    if state_var in initial_state:
      temp_pos_var.append(state_var)
    else:
      temp_neg_var.append(state_var)
  current_state.append(temp_pos_var)
  current_state.append(temp_neg_var)

  for cur_action in plan:
    for action in action_list:
      if (action.name == cur_action[0] and tuple(action.parameters) == cur_action[1]):
        # precondition must satisfy:
        for pos_pre_cond in action.positive_preconditions:
          if pos_pre_cond not in current_state[0]:
            print("Error! precondition not satisfied for action: ", cur_action)
            exit()
        for neg_pre_cond in action.negative_preconditions:
          if neg_pre_cond not in current_state[1]:
            print("Error! precondition not satisfied for action: ", cur_action)
            exit()
        # applying action current state:
        for add_state in action.add_effects:
          if add_state not in current_state[0]:
            current_state[0].append(add_state)
          if add_state in current_state[1]:
            current_state[1].remove(add_state)
        for del_state in action.del_effects:
          if del_state not in current_state[1]:
            current_state[1].append(del_state)
          if del_state in current_state[0]:
            current_state[0].remove(del_state)
  # Testing if current state is goal state:
  for pos_state in goal_state[0]:
    if pos_state not in current_state[0]:
      print("Error! goal state not reached, positive conditions not present \n")
      exit()
  for neg_state in goal_state[1]:
    if neg_state not in current_state[1]:
      print("Error! goal state not reached \n")
      exit()

  print("Test successful! plan is accurate \n")


def test_plan_with_val(domain, problem, plan):
  print("Testing with VAL: \n")
  Val_path = './tools/Validate'
  command = Val_path + ' ' + domain + ' ' + problem + ' ' + plan
  os.system(command)