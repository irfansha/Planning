# Planning
A framework for developing/using/experimenting planning problems, with special focus on QBF solving.

Ungrounded encoding available:
A QBF encoding is generated for given domain and problem file in PDDL specification with out grounding.

## Dependencies:

Note: Paths assume linux operating system, can be changed if needed.

For generating plans:
Install CAQE solver and place the executable in solvers path: ./solvers/qbf/caqe

For preprocessing:
Install Bloqqer and place the executable in tools path: ./tools/bloqqer/bloqqer

For preprocessing with plan extraction with CAQE:
Install Bloqqer-qdo, a modified preprocessor by Leander Tentrup and place in the main directory path: ./bloqqer-qdo

## Usage

For running tests:
python3 main.py --run_tests 1

For only encoding generation (k is plan length):
python3 main.py -d testcases/competition/IPC2/Blocks/domain.pddl -p testcases/competition/IPC2/Blocks/prob01.pddl -k 6 --run 0

For plan existence/extraction:
python3 main.py -d [] -p [] -k [] --run 1/--run 2

For plan existence with preprocessing (standard bloqqer works fine):
python3 main.py -d [] -p [] -k [] --run 1 --preprocessing 1

For plan extraction with preprocessing (use bloqqer-qdo):
python3 main.py -d [] -p [] -k [] --run 2 --preprocessing 2
