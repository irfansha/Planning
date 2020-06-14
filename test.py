import pddlpy

domprob = pddlpy.DomainProblem('./examples-pddl/blocks/domain.pddl', './examples-pddl/blocks/probBLOCKS-4-0.pddl')


print("DOMAIN PROBLEM")
print("objects")
print("\t", domprob.worldobjects())
print("operators")
print("\t", list( domprob.operators() ))
print("init",)
print("\t", domprob.initialstate())
print("goal",)
print("\t", domprob.goals())

ops_to_test = { 1:"pick-up", 2:"put-down", 3:"stack", 4:"unstack", }
op = ops_to_test[4]
for o in domprob.ground_operator(op):
    print()
    print( "\tvars", o.variable_list )
    print( "\tpre+", o.precondition_pos )
    print( "\tpre-", o.precondition_neg )
    print( "\teff+", o.effect_pos )
    print( "\teff-", o.effect_neg )
