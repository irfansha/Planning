# Irfansha Shaik, 15.11.2020, Aarhus

from variable_dispatcher import VarDispatcher as vd
from pddl import PDDL_Parser
from action import Action

class UngroundedEncoding():

  #-------------------------------------------------------------------------------------------
  # state extraction from pddl domain and problem:
  #-------------------------------------------------------------------------------------------
  '''
  Takes domain and problem as input and generates lists
  - initial state
  - goal state
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

    if (len(parser.types) == 0):
      # Adding default object type:
      parser.types.append("object")

    #Adding No-op to the actions:
    parser.actions.append(Action('noop', [], [], [], [], []))

    self.types = parser.types
    self.actions = parser.actions
    self.predicates = parser.predicates
    self.objects = parser.objects

    #for action in parser.actions:
    #  print(action)
    #print(self.types)
    #print(self.predicates)
    #print(self.objects)

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
      print(action)
      temp_parameter_dict, max_parameter_length =  self.get_unique_parameters(action)
      print(temp_parameter_dict)
      for i in range(max_parameter_length+1):
        if (temp_parameter_dict != {}):
          for temp_parameter in temp_parameter_dict[i]:
            print("temp_par", temp_parameter)
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
            self.predicate_split_action_list.append(Action(action.name, [i, temp_parameter], new_positive_preconditions, new_negative_preconditions, new_add_effects, new_del_effects))
    for action in self.predicate_split_action_list:
      print(action)

#-------------------------------------------------------------------------------------------

  def print_gate(self, gate):
    if len(gate) == 1:
      print(gate[0])
    else:
      print(str(gate[1]) + ' = ' + gate[0] + '(' + ', '.join(str(x) for x in gate[2]) + ')')

  def print_gate_tofile(self, gate, f):
    if len(gate) == 1:
      f.write(gate[0] + '\n')
    else:
      f.write(str(gate[1]) + ' = ' + gate[0] + '(' + ', '.join(str(x) for x in gate[2]) + ') \n')

  def print_encoding_tofile(self, file_path):
    f = open(file_path, 'w')
    for gate in self.quantifier_block:
      self.print_gate_tofile(gate, f)
    f.write('output(' + str(self.final_output_gate) + ') \n')
    for gate in self.encoding:
      self.print_gate_tofile(gate, f)

  def print_encoding(self):
    for gate in self.quantifier_block:
      self.print_gate(gate)
    print('output(' + str(self.final_output_gate) + ')')
    for gate in self.encoding:
      self.print_gate(gate)


  def __init__(self, args):
    self.var_dis = vd()
    self.quantifier_block = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.transition_step_output_gates = []
    self.final_output_gate = 0 # final output gate can never be 0


    self.predicate_dict = {}
    self.max_predicate_args = -1 # max predicate arguments can never be -1

    self.predicate_split_action_list = []

    # generating constraint for the pddl problem:
    self.extract(args.d, args.p)

    # separating predicates based on number of arguments:
    self.gen_predicate_list()

    # splitting actions based on predicates:
    self.gen_predicate_split_action_list()
