# Irfansha Shaik, 21.09.2020, Aarhus

from pddl import PDDL_Parser
from action import Action


#-------------------------------------------------------------------------------------------

# state extraction from pddl domain and problem:
#-------------------------------------------------------------------------------------------
'''
Takes domain and problem as input and generates lists
- initial state
- goal state
- grounded actions
'''
def constraints(domain, problem):
  gate_list = []
  # Parser
  parser = PDDL_Parser()
  parser.parse_domain(domain)
  parser.parse_problem(problem)

  state = parser.state
  # Initial state gate:
  initial_gate = list(state)

  goal_pos = parser.positive_goals
  goal_not = parser.negative_goals
  goal_gate = [goal_pos, goal_not]

  action_list = []
  # Grounding process
  ground_actions = []
  for action in parser.actions:
    for act in action.groundify(parser.objects):
      ground_actions.append(act)
  # Appending grounded actions:
  for act in ground_actions:
    action_list.append(act)
  # Adding No-op to the actions:
  action_list.append(Action('noop', (), [], [], [], []))

  return (initial_gate, goal_gate, action_list)
#-------------------------------------------------------------------------------------------


# State variables extractor:
#-------------------------------------------------------------------------------------------
'''
Extracts all possible states from constraints available:
'''
def extract_state_vars(initial_state, goal_state, action_list):
  state_vars = []
  for var in initial_state:
    if var not in state_vars:
      state_vars.append(var)

  for var_list in goal_state:
    for var in var_list:
      if var not in state_vars:
        state_vars.append(var)

  for constraint in action_list:
    for cond in constraint.positive_preconditions:
      if cond not in state_vars:
        state_vars.append(cond)
    for cond in constraint.negative_preconditions:
      if cond not in state_vars:
        state_vars.append(cond)
    for cond in constraint.add_effects:
      if cond not in state_vars:
        state_vars.append(cond)
    for cond in constraint.del_effects:
      if cond not in state_vars:
        state_vars.append(cond)
  return state_vars


def extract_action_vars(action_list):
  action_vars = []
  for action in action_list:
    action_vars.append((action.name, action.parameters))
  return action_vars

