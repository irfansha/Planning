# Irfansha Shaik, 21.09.2020, Aarhus

from pddl import PDDL_Parser
from action import Action


class Constraints():

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

  def update_types_and_objects(self, types):

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
      #print(obj_type)
      #print(objects)



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

    self.objects = dict(parser.objects)

    # Updating incorrect parsed types:
    self.update_types_and_objects(parser.types)

    # Grounding process
    ground_actions = []
    for action in parser.actions:
      for act in action.groundify(self.updated_objects):
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

    self.type_hierarchy_dict = {}

    self.types = []

    self.updated_objects = {}

    # generating constraint for the pddl problem:
    self.constraints_extract(domain, problem)
    # Extracting and sorting state variables:
    self.extract_state_vars()
    self.state_vars.sort()
    self.num_state_vars = len(self.state_vars)
    # Extracting action variables:
    self.extract_action_vars()
