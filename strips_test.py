from strips import STRIPSPlanner, PlannerProblem, Action, Predicate, UnboundPredicate, Variable
import pytest


def strips_planner():
    # Declare variables

    r, fr, to =  "r", "from", "to"
    move = Action(
            params=[r, fr, to], 
            neg_preconditions=[UnboundPredicate("occ", [to])], 
            pos_preconditions=[UnboundPredicate("adj", [fr, to]), UnboundPredicate("at", [r, fr])],
            pos_effects=[UnboundPredicate("at", [r, to]), UnboundPredicate("occ", [to])],
            neg_effects=[UnboundPredicate("occ", [fr]), UnboundPredicate("at", [r, fr])],

    )
    initial_state: list[Predicate] = Predicate(""])




