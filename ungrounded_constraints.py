# Irfansha Shaik, 16.11.2020, Aarhus

from pddl import PDDL_Parser
from action import ActionWithUntouchedPredicates as ap
import math
from collections import Counter

class UngroundedConstraints():

  #-------------------------------------------------------------------------------------------
  # extraction from pddl domain and problem:
  #-------------------------------------------------------------------------------------------
  '''
  Takes domain and problem as input and extracts
  - initial state
  - goal state
  - types
  - predicates
  - objects
  - actions
  '''
  def extract(self, domain, problem):
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

    # XXX handle if there are no objects:
    if (len(parser.types) == 0):
      # Adding default object type:
      parser.types.append("object")

    #Adding No-op to the actions:
    parser.actions.append(ap('noop', [], [], [], [], [], []))

    self.types = parser.types
    self.actions = parser.actions
    self.predicates = parser.predicates
    self.objects = parser.objects

  def gen_predicate_list(self):
    for predicate, parameters in self.predicates.items():
      args_num = len(parameters)
      if (args_num > self.max_predicate_args):
        self.max_predicate_args = args_num
      if args_num in self.predicate_dict:
        self.predicate_dict[args_num].append(predicate)
      else:
        self.predicate_dict[args_num] = [predicate]

  def get_unique_parameters(self,action):
    temp_parameter_dict = {}
    max_parameter_length = 0
    # Extracting unique parameters for predicates:
    # positive preconditions:
    for pos_pre in action.positive_preconditions:
      parameters = list(pos_pre[1:])
      if len(parameters) in temp_parameter_dict:
        if parameters not in temp_parameter_dict[len(parameters)]:
          temp_parameter_dict[len(parameters)].append(parameters)
      else:
        if len(parameters) > max_parameter_length:
          max_parameter_length = len(parameters)
        temp_parameter_dict[len(parameters)] = [parameters]
    # negative preconditions:
    for neg_pre in action.negative_preconditions:
      parameters = list(neg_pre[1:])
      if len(parameters) in temp_parameter_dict:
        if parameters not in temp_parameter_dict[len(parameters)]:
          temp_parameter_dict[len(parameters)].append(parameters)
      else:
        if len(parameters) > max_parameter_length:
          max_parameter_length = len(parameters)
        temp_parameter_dict[len(parameters)] = [parameters]
    # add effects:
    for add_eff in action.add_effects:
      parameters = list(add_eff[1:])
      if len(parameters) in temp_parameter_dict:
        if parameters not in temp_parameter_dict[len(parameters)]:
          temp_parameter_dict[len(parameters)].append(parameters)
      else:
        if len(parameters) > max_parameter_length:
          max_parameter_length = len(parameters)
        temp_parameter_dict[len(parameters)] = [parameters]
    # delete effects:
    for del_eff in action.del_effects:
      parameters = list(del_eff[1:])
      if len(parameters) in temp_parameter_dict:
        if parameters not in temp_parameter_dict[len(parameters)]:
          temp_parameter_dict[len(parameters)].append(parameters)
      else:
        if len(parameters) > max_parameter_length:
          max_parameter_length = len(parameters)
        temp_parameter_dict[len(parameters)] = [parameters]
    return temp_parameter_dict, max_parameter_length


  def gen_predicate_split_action_list(self):
    for action in self.actions:
      temp_parameter_dict, max_parameter_length =  self.get_unique_parameters(action)
      for i in range(max_parameter_length+1):
        if i in temp_parameter_dict.keys():
          for temp_parameter in temp_parameter_dict[i]:
            # Generating new positive preconditions after splitting:
            new_positive_preconditions = []
            for pos_pre in action.positive_preconditions:
              pos_pre_param = list(pos_pre[1:])
              if (temp_parameter == pos_pre_param):
                new_positive_preconditions.append(pos_pre[0])
            # Generating new negative preconditions after splitting:
            new_negative_preconditions = []
            for neg_pre in action.negative_preconditions:
              neg_pre_param = list(neg_pre[1:])
              if (temp_parameter == neg_pre_param):
                new_negative_preconditions.append(neg_pre[0])
            # Generating new add effects after splitting:
            new_add_effects = []
            for add_eff in action.add_effects:
              add_eff_param = list(add_eff[1:])
              if (temp_parameter == add_eff_param):
                new_add_effects.append(add_eff[0])
            # Generating new del effects after splitting:
            new_del_effects = []
            for del_eff in action.del_effects:
              del_eff_param = list(del_eff[1:])
              if (temp_parameter == del_eff_param):
                new_del_effects.append(del_eff[0])
            untouched_predicates = []
            # Generating untouched clauses after splitting:
            for predicate in self.predicate_dict[i]:
              if predicate not in new_add_effects and predicate not in new_del_effects:
                untouched_predicates.append(predicate)
            self.predicate_split_action_list.append(ap(action.name, [i, temp_parameter], new_positive_preconditions, new_negative_preconditions, new_add_effects, new_del_effects, untouched_predicates))
    # Handling noop operation:
    self.predicate_split_action_list.append(ap(self.actions[-1].name, [0, []], [], [], [], [], list(self.predicates)))

  def extract_action_vars(self):
    for action in self.actions:
      self.action_vars.append((action.name, tuple(action.parameters)))

  def gen_bin_var_object_types(self):
    for obj_type in self.types:
      obj_length = len(self.objects[obj_type])
      num_binary_vars = math.ceil(math.log2(obj_length))
      # handling log(1) = 0:
      if (num_binary_vars == 0):
        num_binary_vars = 1
      self.bin_object_type_vars_dict[obj_type] = num_binary_vars

  # XXX check if any difference in hierarchial types:
  def gen_forall_variables_types(self):
    # Initializing forall_variables_type_dict with -1 for all types:
    for obj_type in self.types:
      self.forall_variables_type_dict[obj_type] = 0

    for predicate, predicate_type in self.predicates.items():
      values = list(predicate_type.values())
      for obj_type, count in Counter(values).items():
        if (self.forall_variables_type_dict[obj_type] < count):
          self.forall_variables_type_dict[obj_type] = count

  def __init__(self, domain, problem):
    self.predicate_dict = {}
    self.max_predicate_args = -1 # max predicate arguments can never be -1

    self.predicate_split_action_list = []

    # generating constraint for the pddl problem:
    self.extract(domain, problem)

    # separating predicates based on number of arguments:
    self.gen_predicate_list()

    # splitting actions based on predicates:
    self.gen_predicate_split_action_list()

    self.action_vars = []
    # Extracting action variables:
    self.extract_action_vars()

    # Extracting required binary variables for objects with types:
    self.bin_object_type_vars_dict = {}
    self.gen_bin_var_object_types()

    self.forall_variables_type_dict = {}
    self.gen_forall_variables_types()
