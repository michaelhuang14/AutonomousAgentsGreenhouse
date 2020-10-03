import sys

if len(sys.argv) == 1 or "1" in sys.argv[1]:
    from coffee_maker import *
    from autograder_files import autograder_coffee_maker
    print("Part 1: Coffee Maker")
    if len(sys.argv) == 3 and "-t" in sys.argv[2]:
        autograder_coffee_maker.parse_coffee_test(int(sys.argv[2][2:]))
    else:
        autograder_coffee_maker.parse_coffee_test(-1)
    print()

if len(sys.argv) == 1 or "2" in sys.argv[1]:
    from autograder_files import autograder_greenhouse
    fsms = ["Light","RaiseTemp","LowerTemp","LowerHumid","RaiseSMoist","LowerSMoist","Ping"]
    if len(sys.argv) == 3 and sys.argv[2] in fsms:
        autograder_greenhouse.checkOneBehavior(sys.argv[2])
    elif len(sys.argv) == 3:
        print("Unknown behavior: select from ", fsms)
    elif len(sys.argv) == 1 or len(sys.argv) == 2:
        print("Part 2: Individual FSMs")
        for fsm in fsms:
            print("FSM: ", fsm)
            autograder_greenhouse.checkOneBehavior(fsm)
    print()


if len(sys.argv) == 1 or "3" in sys.argv[1]:
    from autograder_files import autograder_greenhouse
    print("Part 3: Full Agent")
    autograder_greenhouse.checkLayeredBehavior()
    print()