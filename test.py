import pddlpy

domprob = pddlpy.DomainProblem('./examples-pddl/blocks/domain.pddl', './examples-pddl/blocks/probBLOCKS-4-0.pddl')

print(domprob.initialstate())
print(domprob.goals())
print(list(domprob.operators()))
print(list(domprob.ground_operator('stack')))
print(list(domprob.ground_operator('stack'))[0].precondition_pos)
