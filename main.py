from pddl import parse_domain, parse_problem
import sys


def main():
    domain = parse_domain(sys.argv[1])
    problem = parse_problem(sys.argv[2])

    for action in domain.actions:
        print(action.precondition)
        print(action.effect)

if __name__ == "__main__":
    main()
