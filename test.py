import pddlpy

domprob = pddlpy.DomainProblem('./examples-pddl/domain-03.pddl', './examples-pddl/problem-03.pddl')

print(domprob.initialstate())
