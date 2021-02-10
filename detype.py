# Irfansha Shaik, 09.02.2021, Aarhus

'''
Takes a domain and problem file in pddl specification, and removed the types
by using static predicates.
'''


from pddl import PDDL_Parser
#from action import Action

# Goes depth first to find the subtype objects
# and generates flattened types:
def find_objects(parser, obj_type, type_hierarchy_dict):
    if obj_type in parser.objects:
      return parser.objects[obj_type]
    else:
      if (obj_type in type_hierarchy_dict):
        next_obj_types = type_hierarchy_dict[obj_type]
      else:
        next_obj_types = []
      object_list = []
      for next_obj_type in next_obj_types:
        objects = find_objects(parser, next_obj_type, type_hierarchy_dict)
        object_list.extend(objects)
      return object_list

# Flattens the type hierarchy:
def update_types_and_objects(parser, type_hierarchy_dict, types):

  temp_list = []
  copy_types = list(parser.types)
  while(copy_types):
    temp_type = copy_types.pop(0)
    if (temp_type == '-'):
      # types list is not empty, so the super type is specified:
      if(copy_types):
        temp_super_type = copy_types.pop(0)
      else:
        temp_super_type = 'object'
      if temp_super_type in type_hierarchy_dict:
        type_hierarchy_dict[temp_super_type].extend(temp_list)
      else:
        type_hierarchy_dict[temp_super_type] = temp_list
      temp_list = []
    else:
      temp_list.append(temp_type)
  if (temp_list):
    type_hierarchy_dict['object'] = temp_list

  #print(type_hierarchy_dict)

  # Generating new type list from hierarchy:
  for super_type, sub_types in type_hierarchy_dict.items():
    if super_type not in types:
      types.append(super_type)
    for sub_type in sub_types:
      if sub_type not in types:
        types.append(sub_type)
  # object is the default type:
  if "object" not in types:
    types.append("object")

  updated_objects = {}

  # Now generating new object list:
  for obj_type in types:
    objects = find_objects(parser, obj_type, type_hierarchy_dict)
    updated_objects[obj_type] = objects
    #print(obj_type)
    #print(objects)
  return updated_objects

# Changing actions, adding types to preconditions:
def detype_domain(parser):
  used_types = []
  for action in parser.actions:
    new_parameters = []
    new_positive_preconditions = []
    for parameter in action.parameters:
      # No need of types, only names are enough:
      new_parameters.append(parameter[0])
      # Adding static type predicate in precondition
      # Need [type, ?argument] format:
      new_positive_preconditions.append([parameter[1], parameter[0]])
      # Collecting used types from parameters:
      if parameter[1] not in used_types:
        used_types.append(parameter[1])
    action.parameters = new_parameters
    action.positive_preconditions.extend(new_positive_preconditions)
  return used_types

def detype(domain, problem, domain_out, problem_out):
  # Parser
  parser = PDDL_Parser()
  parser.parse_domain(domain)
  parser.parse_problem(problem)

  f_domain = open(domain_out, "w")
  f_problem = open(problem_out, "w")

  types = []
  type_hierarchy_dict = {}

  # returns updated objects with all type dictionary:
  updated_objects = update_types_and_objects(parser, type_hierarchy_dict, types)

  #print(updated_objects)

  # returns used types, we only add typed predicates
  # if they are used in the domain:
  used_types = detype_domain(parser)

  # Testing if the actions are changed accordingly:
  #for action in parser.actions:
  #  print(action)


  print_detyped_domain_file(parser, f_domain)

  f_domain.close()

  # Printing detyped problem to stdout (for now):
  print_detyped_problem_file(parser, updated_objects, used_types, f_problem)

  f_problem.close()

  # replacing '_' with '-' for consistency:
  #replace_chars(domain_out, problem_out)

  if (":equality" in parser.requirements):
    replace_chars(domain_out)



def replace_chars(domain_out):
  # reading the lines in domain file:
  f = open(domain_out, "r")
  domain_lines = f.readlines()
  f.close()

  # writing back by replacing:
  f = open(domain_out, "w")
  for line in domain_lines:
    line = line.replace("=", "eq")
    f.write(line)
  f.close()


def print_detyped_domain_file(parser, f_domain):
  # domain name is unchanged:
  f_domain.write("(define (domain " + parser.domain_name + ")\n")

  # Since we extract predicates from actions, we do not need
  # to specify explicitly:
  f_domain.write("(:predicates )\n")

  for action in parser.actions:
    f_domain.write("(:action " + action.name + "\n")
    f_domain.write("  :parameters (" + " ".join(action.parameters) + ")\n")
    f_domain.write("  :precondition\n")
    precondition_string = ''
    # joining positive preconditions:
    for pre_cond in action.positive_preconditions:
      precondition_string = precondition_string + ' (' + ' '.join(pre_cond) + ")"
    # joining positive preconditions:
    for pre_cond in action.negative_preconditions:
      precondition_string = precondition_string + ' (not(' + ' '.join(pre_cond) + "))"
    f_domain.write("  (and" + precondition_string + ")\n")

    # Printing effects:
    f_domain.write("  :effect\n")
    effect_string = ''
    # joining positive preconditions:
    for eff_cond in action.add_effects:
      effect_string = effect_string + ' (' + ' '.join(eff_cond) + ")"
    # joining positive preconditions:
    for eff_cond in action.del_effects:
      effect_string = effect_string + ' (not(' + ' '.join(eff_cond) + "))"
    f_domain.write("  (and" + effect_string + ")\n")
    # action end paranthesis:
    f_domain.write(")\n")

  # Closing parantheses for domain:
  f_domain.write(")\n")

def print_detyped_problem_file(parser, updated_objects, used_types, f_problem):

  # problem name and domain name is unchanged:
  f_problem.write("(define (problem " + parser.problem_name + ")\n")
  f_problem.write("  (:domain " + parser.domain_name + ")\n")

  # Printing objects without types:
  f_problem.write("  (:objects\n")
  # objects are dictionary, only values are needs:
  for objs  in parser.objects.values():
    for obj in objs:
      f_problem.write("    " + obj+ "\n")
  # Objects closing parantheses:
  f_problem.write("  )\n")

  # Initial state is printed as usual, but with additional
  # static predicates for types:
  f_problem.write("  (:init \n")
  for prop in parser.state:
    f_problem.write("    (" + " ".join(prop) + ")\n")
  f_problem.write("    ;; static predicates for types:\n")

  # Adding static type predicates for each object:
  #for obj_type, objs  in parser.objects.items():
  # Instead using updated types to handle super types:
  for obj_type, objs  in updated_objects.items():
    if (obj_type in used_types):
      for obj in objs:
        f_problem.write("    (" + str(obj_type) + " "  + str(obj) + ")\n")

  # Printing equality propositions for objects
  # if equality is a requirement:
  if (":equality" in parser.requirements):
    f_problem.write("    ;; equality propositions for objects:\n")
    for obj_type, objs  in parser.objects.items():
        for obj in objs:
          f_problem.write("    (eq "  + str(obj) + " " + str(obj) + ")\n")

  # closing parantheses for initial state definition:
  f_problem.write("  )\n")



  # Goal state does not change so writting as before:
  f_problem.write("  (:goal (and\n")
  for goal in parser.positive_goals:
    f_problem.write("    (" + " ".join(goal) + ")\n")
  for goal in parser.negative_goals:
    f_problem.write("    (not (" + ' '.join(goal) + ") )\n")
  f_problem.write("  ))\n")

  # closing parantheses for problem file:
  f_problem.write(")\n")
