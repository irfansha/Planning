# Irfansha Shaik, 21.09.2020, Aarhus

from pddl import PDDL_Parser
from action import Action


class Constraints():

  #-------------------------------------------------------------------------------------------
  # state extraction from pddl domain and problem:
  #-------------------------------------------------------------------------------------------
  '''
  Takes domain and problem as input and generates lists
  - initial state
  - goal state
  - grounded actions
  '''
  def constraints_extract(self, domain, problem):
    gate_list = []
    # Parser
    parser = PDDL_Parser()
    parser.parse_domain(domain)
    parser.parse_problem(problem)

    state = parser.state
    # Initial state gate, ASSUMING no negative initial conditions:
    self.initial_state = list(state)

    goal_pos = parser.positive_goals
    goal_not = parser.negative_goals
    self.goal_state = [goal_pos, goal_not]

    # Grounding process
    ground_actions = []
    for action in parser.actions:
      for act in action.groundify(parser.objects):
        ground_actions.append(act)
    # Appending grounded actions:
    for act in ground_actions:
      self.action_list.append(act)
    # Adding No-op to the actions:
    self.action_list.append(Action('noop', (), [], [], [], []))

  #-------------------------------------------------------------------------------------------


  # State variables extractor:
  #-------------------------------------------------------------------------------------------
  '''
  Extracts all possible states from constraints available:
  '''
  def extract_state_vars(self):

    for var in self.initial_state:
      if var not in self.state_vars:
        self.state_vars.append(var)

    for var_list in self.goal_state:
      for var in var_list:
        if var not in self.state_vars:
          self.state_vars.append(var)

    for constraint in self.action_list:
      for cond in constraint.positive_preconditions:
        if cond not in self.state_vars:
          self.state_vars.append(cond)
      for cond in constraint.negative_preconditions:
        if cond not in self.state_vars:
          self.state_vars.append(cond)
      for cond in constraint.add_effects:
        if cond not in self.state_vars:
          self.state_vars.append(cond)
      for cond in constraint.del_effects:
        if cond not in self.state_vars:
          self.state_vars.append(cond)


  def extract_action_vars(self):
    for action in self.action_list:
      self.action_vars.append((action.name, tuple(action.parameters)))


  def __init__(self, domain, problem):
    self.initial_state = []
    self.goal_state = []
    self.action_list = []
    self.state_vars = []
    self.action_vars = []
    # generating constraint for the pddl problem:
    self.constraints_extract(domain, problem)
    # Extracting and sorting state variables:
    self.extract_state_vars()
    self.state_vars.sort()
    self.num_state_vars = len(self.state_vars)
    # Extracting action variables:
    self.extract_action_vars()
