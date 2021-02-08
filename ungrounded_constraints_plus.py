# Irfansha Shaik, 16.11.2020, Aarhus

from pddl import PDDL_Parser
from action import ActionWithUntouchedPredicates as ap
from action import Action as ga
import math
from collections import Counter

class UngroundedConstraintsPlus():

  def find_objects(self, obj_type):
    if obj_type in self.objects:
      return self.objects[obj_type]
    else:
      next_obj_types = self.type_hierarchy_dict[obj_type]
      object_list = []
      for next_obj_type in next_obj_types:
        objects = self.find_objects(next_obj_type)
        object_list.extend(objects)
      return object_list

  def update_types_objects(self, types):

    temp_list = []
    copy_types = list(types)
    while(copy_types):
      temp_type = copy_types.pop(0)
      if (temp_type == '-'):
        # types list is not empty, so the super type is specified:
        if(copy_types):
          temp_super_type = copy_types.pop(0)
        else:
          temp_super_type = 'object'
        if temp_super_type in self.type_hierarchy_dict:
          self.type_hierarchy_dict[temp_super_type].extend(temp_list)
        else:
          self.type_hierarchy_dict[temp_super_type] = temp_list
        temp_list = []
      else:
        temp_list.append(temp_type)
    if (temp_list):
      self.type_hierarchy_dict['object'] = temp_list

    # Generating new type list from hierarchy:
    for super_type, sub_types in self.type_hierarchy_dict.items():
      if super_type not in self.types:
        self.types.append(super_type)
      for sub_type in sub_types:
        if sub_type not in self.types:
          self.types.append(sub_type)
    # object is the default type:
    if "object" not in self.types:
      self.types.append("object")

    # Now generating new object list:
    for obj_type in self.types:
      objects = self.find_objects(obj_type)
      self.updated_objects[obj_type] = objects

  def gen_predicate_name(self, cond, action_parameters):
        cond_name = cond[0]
        cond_parameters = cond[1:]
        temp_parameter_type_map = {}
        count = 0
        temp_parameter_type_string = ''
        for cond_parameter in cond_parameters:
          for action_parameter in action_parameters:
            if (cond_parameter == action_parameter[0]):
              new_key = '?' + str(count)
              count += 1
              temp_parameter_type_map[new_key]= action_parameter[1]
              temp_parameter_type_string += '_' + action_parameter[1]
        return cond_name + temp_parameter_type_string, temp_parameter_type_map

  def gen_new_predicates(self, actions):
    for action in actions:
      for cond in action.positive_preconditions:
        predicate_new_name, parameter_map = self.gen_predicate_name(cond, action.parameters)
        if predicate_new_name not in self.predicates:
          self.predicates[predicate_new_name] = parameter_map
        cond[0] = predicate_new_name
      for cond in action.negative_preconditions:
        predicate_new_name, parameter_map = self.gen_predicate_name(cond, action.parameters)
        if predicate_new_name not in self.predicates:
          self.predicates[predicate_new_name] = parameter_map
        cond[0] = predicate_new_name
      for cond in action.add_effects:
        predicate_new_name, parameter_map = self.gen_predicate_name(cond, action.parameters)
        if predicate_new_name not in self.predicates:
          self.predicates[predicate_new_name] = parameter_map
        cond[0] = predicate_new_name
      for cond in action.del_effects:
        predicate_new_name, parameter_map = self.gen_predicate_name(cond, action.parameters)
        if predicate_new_name not in self.predicates:
          self.predicates[predicate_new_name] = parameter_map
        cond[0] = predicate_new_name

  def gen_initial_state(self, state):
    for prop in state:
      prop_name = prop[0]
      prop_parameters = prop[1:]
      for prop_parameter in prop_parameters:
        for obj_type, objects in self.objects.items():
          if (prop_parameter) in objects:
            prop_name += '_' + obj_type
      old_name_list = []
      old_name_list.append(prop[0])
      old_name_list.extend(list(prop_parameters))
      prop[0] = prop_name
      self.initial_state.append(prop)
      self.base_initial_state.append(old_name_list)

  def gen_goal_state(self, positive_goals, negative_goals):
    old_positive_goals = []
    for prop in positive_goals:
      prop_name = prop[0]
      prop_parameters = prop[1:]
      for prop_parameter in prop_parameters:
        for obj_type, objects in self.objects.items():
          if (prop_parameter) in objects:
            prop_name += '_' + obj_type
      old_name_list = []
      old_name_list.append(prop[0])
      old_name_list.extend(list(prop_parameters))
      old_positive_goals.append(old_name_list)
      prop[0] = prop_name


    old_negative_goals = []
    for prop in negative_goals:
      prop_name = prop[0]
      prop_parameters = prop[1:]
      for prop_parameter in prop_parameters:
        for obj_type, objects in self.objects.items():
          if (prop_parameter) in objects:
            prop_name += '_' + obj_type
      old_name_list = []
      old_name_list.append(prop[0])
      old_name_list.extend(list(prop_parameters))
      old_negative_goals.append(old_name_list)
      prop[0] = prop_name
    self.goal_state = [positive_goals, negative_goals]
    self.base_goal_state = [old_positive_goals, old_negative_goals]

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

    for constant_list in parser.constants:
      temp_constants = []
      while(constant_list):
        cur_constant = constant_list.pop(0)
        if (cur_constant == '-'):
          constant_type = constant_list.pop(0)
          if constant_type not in parser.objects:
            parser.objects[constant_type] = temp_constants
          else:
            parser.objects[constant_type].extend(temp_constants)
        else:
          temp_constants.append(cur_constant)


    state = list(parser.state)


    self.objects = dict(parser.objects)

    # Updating incorrect parsed types:
    self.update_types_objects(parser.types)

    self.gen_new_predicates(parser.actions)

    #self.predicates = parser.predicates

    #Adding No-op to the actions:
    parser.actions.append(ap('noop', [], [], [], [], [], [], []))

    self.actions = parser.actions

    #for action in self.actions:
    #  print(action)
    # Initial state gate, ASSUMING no negative initial conditions:
    self.gen_initial_state(state)


    #print(goal_pos, goal_not)
    self.gen_goal_state(parser.positive_goals, parser.negative_goals)
    #print(self.goal_state)



  # Only for testing purposes, grounded action lists required:
  def extract_state_vars(self, domain, problem, verbosity):
    if (verbosity != 0):
      print("Caution! grounding (use only for testing purposes)")
    parser = PDDL_Parser()
    parser.parse_domain(domain)
    parser.parse_problem(problem)
    # Grounding process
    ground_actions = []
    self.test_action_list = []


    state = parser.state
    # Initial state gate, ASSUMING no negative initial conditions:
    self.test_initial_state = list(state)

    goal_pos = parser.positive_goals
    goal_not = parser.negative_goals
    self.test_goal_state = [goal_pos, goal_not]


    for action in parser.actions:
      for act in action.groundify(self.updated_objects):
        ground_actions.append(act)
    # Appending grounded actions:
    for act in ground_actions:
      self.test_action_list.append(act)

    for var in self.test_initial_state:
      if var not in self.state_vars:
        self.state_vars.append(var)

    for var_list in self.test_goal_state:
      for var in var_list:
        if var not in self.state_vars:
          self.state_vars.append(var)

    for constraint in self.test_action_list:
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


  def gen_predicate_list(self):
    for predicate, parameters in self.predicates.items():
      temp_parameter_type_list = []
      for parameter, parameter_type in parameters.items():
        temp_parameter_type_list.append(parameter_type)
      if tuple(temp_parameter_type_list) not in self.predicate_types:
        self.predicate_types.append(tuple(temp_parameter_type_list))
      # For noop:
      #print(predicate, parameters)
      args_num = len(parameters)
      if (args_num > self.max_predicate_args):
        self.max_predicate_args = args_num
      if args_num in self.predicate_dict:
        self.predicate_dict[args_num].append(predicate)
      else:
        self.predicate_dict[args_num] = [predicate]
    for i in range(self.max_predicate_args+1):
      if (i not in self.predicate_dict):
        self.predicate_dict[i] = []
    if (() not in self.predicate_types):
      self.predicate_types.append(())

  # Here max parameter length does not need to be computed, instead max predicate arguments is sufficient,
  # To be checked for predicates with 3 args:
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


  def gen_action_parameter_type_dict(self, action):
    temp_dict = {}
    for parameter in action.parameters:
      if parameter[0] not in temp_dict:
        temp_dict[parameter[0]] = parameter[1]
    return temp_dict

  def gen_predicate_split_action_list(self):
    for action in self.actions:
      # Noop handled separately:
      if (action.name == 'noop'):
        continue
      temp_parameter_dict, max_parameter_length =  self.get_unique_parameters(action)
      parameter_type_dict = self.gen_action_parameter_type_dict(action)
      #print("paramete_type_dict",parameter_type_dict)
      #print("paramete_dict",temp_parameter_dict)
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
            all_untouched_predicates = []
            # Generating parameter type:
            cur_parameter_type = []
            for cur_parameter in temp_parameter:
              cur_parameter_type.append(parameter_type_dict[cur_parameter])
            # Generating untouched clauses after splitting:
            for predicate in self.predicate_dict[i]:
              predicate_values = list(self.predicates[predicate].values())
              flag = 1
              for j in range(i):
                if (cur_parameter_type[j] != predicate_values[j]):
                  flag = 0
                  break
              if (flag):
                all_untouched_predicates.append(predicate)
                if predicate not in new_add_effects and predicate not in new_del_effects:
                  untouched_predicates.append(predicate)
            self.predicate_split_action_list.append(ap(action.name, [i, temp_parameter], new_positive_preconditions, new_negative_preconditions, new_add_effects, new_del_effects, untouched_predicates, all_untouched_predicates))
        else:
          untouched_predicates = []
          all_untouched_predicates = []
          # Generating untouched clauses after splitting:
          for predicate in self.predicate_dict[i]:
            predicate_values = list(self.predicates[predicate].values())
            all_untouched_predicates.append(predicate)
            untouched_predicates.append(predicate)
          # If parameter is non-empty, here might be the problem:
          self.predicate_split_action_list.append(ap(action.name, [i, []], [], [], [], [], untouched_predicates, all_untouched_predicates))

    # Handling noop operation:
    self.predicate_split_action_list.append(ap(self.actions[-1].name, [0, []], [], [], [], [], list(self.predicates), list(self.predicates)))

  def extract_action_vars(self):
    for action in self.actions:
      self.action_vars.append((action.name, tuple(action.parameters)))

  def gen_bin_var_object_types(self):
    for obj_type in self.types:
      obj_length = len(self.updated_objects[obj_type])
      num_binary_vars = math.ceil(math.log2(obj_length))
      # handling log(1) = 0:
      if (num_binary_vars == 0):
        num_binary_vars = 1
      self.bin_object_type_vars_dict[obj_type] = num_binary_vars

  # XXX check if any difference in hierarchial types:
  def gen_forall_variables_types(self):
    # Initializing forall_variables_type_dict with 0 for all types:
    for obj_type in self.types:
      self.forall_variables_type_dict[obj_type] = 0

    for predicate, predicate_type in self.predicates.items():
      #print(predicate, predicate_type)
      values = list(predicate_type.values())
      for obj_type, count in Counter(values).items():
        if (self.forall_variables_type_dict[obj_type] < count):
          self.forall_variables_type_dict[obj_type] = count

  # Generating minimum required type variables for action arguments:
  def gen_action_vars_overlap_dict(self):
    for obj_type in self.types:
      self.action_vars_overlap_dict[obj_type] = 0

    for action in self.actions:
      parameter_type_list = []
      for parameter in action.parameters:
        parameter_type_list.append(parameter[1])
      for obj_type, count in Counter(parameter_type_list).items():
        if (self.action_vars_overlap_dict[obj_type] < count):
          self.action_vars_overlap_dict[obj_type] = count



  def __init__(self, domain, problem, testing, verbosity):
    self.initial_state = []
    self.base_initial_state = []
    self.goal_state = []
    self.base_goal_state = []

    self.predicate_dict = {}
    self.max_predicate_args = -1 # max predicate arguments can never be -1

    self.predicates = {}

    self.predicate_split_action_list = []

    self.type_hierarchy_dict = {}

    self.types = []
    self.predicate_types = []

    self.updated_objects = {}


    # generating constraint for the pddl problem:
    self.extract(domain, problem)

    if (testing == 1):
      self.state_vars = []
      self.extract_state_vars(domain, problem, verbosity)

    # separating predicates based on number of arguments:
    self.gen_predicate_list()

    #print("predicates",self.predicates)

    #print("predicate types: ", self.predicate_types)

    # splitting actions based on predicates:
    self.gen_predicate_split_action_list()

    #for action in self.predicate_split_action_list:
    #  print(action)


    self.action_vars = []
    # Extracting action variables:
    self.extract_action_vars()

    # Extracting required binary variables for objects with types:
    self.bin_object_type_vars_dict = {}
    self.gen_bin_var_object_types()

    #print(self.bin_object_type_vars_dict)

    self.forall_variables_type_dict = {}
    self.gen_forall_variables_types()

    #print(self.forall_variables_type_dict)

    self.action_vars_overlap_dict = {}
    self.gen_action_vars_overlap_dict()

    #print("predicates",self.predicates)

    #for action in self.actions:
    #  print(action)
    #print(self.forall_variables_type_dict)

    #print(self.initial_state)
    #print(self.goal_state)
