from strips import STRIPSPlanner, PlannerProblem, Action, Predicate, UnboundPredicate, Variable, State
import strips


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
            Predicate("at", ["r1", "loc1"]),
            Predicate("occ", ["loc2"])
    }

    problem = PlannerProblem(
            init=State(initial_state),
            actions=[move],
            goal=State(set([Predicate("at", ["r1", "loc1"])])),
    )
    planner = STRIPSPlanner(planner_problem=problem)
    print(planner.get_applicable_actions())



if __name__ == "__main__":
    strips_planner()

