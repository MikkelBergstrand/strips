from strips import STRIPSPlanner, PlannerProblem, Action, Predicate, UnboundPredicate, State


def strips_planner():
    # Declare variables

    r, fr, to =  "r", "from", "to"
    move = Action(
            params=[r, fr, to], 
            neg_preconditions=[UnboundPredicate("occ", to)], 
            pos_preconditions=[UnboundPredicate("adj", fr, to), UnboundPredicate("at", r, fr)],
            pos_effects=[UnboundPredicate("at", r, to), UnboundPredicate("occ", to)],
            neg_effects=[UnboundPredicate("occ", fr), UnboundPredicate("at", r, fr)],
    )
    initial_state: set[Predicate] = {
            Predicate("adj", ["loc1", "loc2"]),
            Predicate("adj", ["loc2", "loc1"]),
            Predicate("adj", ["loc1", "loc3"]),
            Predicate("adj", ["loc3", "loc1"]),
            Predicate("at", ["r1", "loc1"]),
            Predicate("occ", ["loc2"])
    }

    problem = PlannerProblem(
            init=State(initial_state),
            actions=[move],
            goal=State(set([Predicate("at", ["r1", "loc3"])])),
    )
    planner = STRIPSPlanner(planner_problem=problem)
    print(problem.init)
    print(planner.fwdSearch())


if __name__ == "__main__":
    strips_planner()

