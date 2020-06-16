import pddlpy

'''
Takes initial_state, a list of atoms, and casts it to list of tuples:
'''
def initial_state_cast(temp_initial_state):
  initial_state = []
  for cond in temp_initial_state:
    temp_cond = str(cond)
    temp_cond = temp_cond[1:-1]
    temp_cond = temp_cond.split("'")
    new_cond = []
    for term in temp_cond:
      if term != '' and ',' not in term :
        new_cond.append(term)
    initial_state.append(tuple(new_cond))
  assert(str(temp_initial_state) == str(initial_state))
  return initial_state

'''
Takes, operation and preconditons, and generates next level valid conditions:
'''
def gen_nl_valid_conditions(op, pos_cond, neg_cond):
  valid_actions = []
  for o in domprob.ground_operator(op):
    #print( "\tvars", o.variable_list )
    pre_pos = list(o.precondition_pos)
    pre_neg = list(o.precondition_neg)
    # Listing valid states from each operator:
    invalid_flag = 0
    # Looking at positive preconditions and their presence in initial state:
    for cond in pre_pos:
      if cond not in pos_cond:
        #print("No", cond, "\n", initial_state)
        invalid_flag = 1
        break
    # Looking at negative preconditions and their presence in initial state:
    if invalid_flag == 0:
      for cond in neg_cond:
        if cond in initial_state:
          #print("No", cond, "\n", initial_state)
          invalid_flag = 1
          break
    post_pos = list(o.effect_pos)
    post_neg = list(o.effect_neg)
    if invalid_flag == 0:
      temp_tup = [op, pre_pos, pre_neg, post_pos, post_neg]
      valid_actions.append(temp_tup)
  return valid_actions


domprob = pddlpy.DomainProblem('./examples-pddl/blocks/domain.pddl', './examples-pddl/blocks/probBLOCKS-4-0.pddl')

#Contains objects with thier types:
#print(domprob.worldobjects())


print("operators")
operators = list(domprob.operators())
print(operators)


temp_initial_state = list(domprob.initialstate())

#print(temp_initial_state)

initial_state = initial_state_cast(temp_initial_state)
#print(initial_state)



print("goal",)
print("\t", domprob.goals())

valid_list = []

# XXX To be updated to allow negative conditions in initial state if valid:
pos_cond = list(initial_state)
neg_cond = []

for op in operators:
  temp_valid_actions = gen_nl_valid_conditions(op, pos_cond, neg_cond)
  valid_list.extend(temp_valid_actions)

for valid_map in valid_list:
  print(valid_map)
