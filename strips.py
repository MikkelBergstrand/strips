from dataclasses import dataclass
from copy import deepcopy

type Constant = str
type Variable = str



class Predicate:
    def __init__(self, _type: str, variables: list[Variable]) -> None:
        self.variables = variables
        self.type = _type

    def __str__(self) -> str:
        return f"{self.type}({",".join([str(x) for x in self.variables])})"

    def __hash__(self) -> int:
        return hash(self.__str__())
    
class UnboundPredicate:
    def __init__(self, _type: str, *args: list[Variable]) -> None:
        self.type = _type
        self.variables = args

    def __call__(self, *args: list[Constant]) -> Predicate:
        if len(*args) != len(self.variables):
            raise AssertionError("Invalid number of arguments passed to predicate.")
        return Predicate(self.type, *args)
        
    
@dataclass
class Action:
    params: list[Variable]
    neg_preconditions: list[UnboundPredicate]
    pos_preconditions: list[UnboundPredicate]
    neg_effects: list[UnboundPredicate]
    pos_effects: list[UnboundPredicate] 

class GroundedAction:
    def __init__(self, action: Action) -> None:
        self.action = action
        self.bindings: dict[str, str]

    def is_valid(self) -> bool:
        return len(self.bindings) ==len(self.action.params)

    def export_bindings(self, to_modify: list[UnboundPredicate]) -> list[Predicate]:
        if not self.is_valid():
            raise AssertionError("Cannot export bindings: current variable binding is incomplete!")

        ret: list[Predicate] = []
        for pred in to_modify:
            new_pred = Predicate(pred.type, *pred.variables)
            for i, var in enumerate(new_pred.variables):
                new_pred.variables[i] = self.bindings[var]
            ret.append(new_pred)
        return ret 
                

    def add_binding(self, truth_predicate: Predicate, matching_predicate: UnboundPredicate) -> 'GroundedAction|None':
        """Attempt to bind a predicate that is true (all literals have constant assignments) 
        to an unset predicate (all literals are variables). 
        It will then check if there is a conflict between these assignments and previous assignments."""
        g = GroundedAction(action=self.action)
        new_bindings = deepcopy(self.bindings)

        for truth_var, matching_var in zip(truth_predicate.variables, matching_predicate.variables):
            # Binding does not work, already bound to something.
            if matching_var in new_bindings and new_bindings[matching_var] != truth_var:
                return None
            else:
                new_bindings[str(matching_var)] = truth_var
        g.bindings = new_bindings
        return g



            
class State:
    def __init__(self, predicates: set[Predicate]) -> None:
        self.predicates = predicates

    def satisfies(self, other_predicates: set[Predicate]) -> bool:
        """Check if all input predicates hold in the current state."""
        return other_predicates.issubset(self.predicates)

    def contains(self, other_predicate: Predicate) -> bool:
        return other_predicate in self.predicates


@dataclass
class PlannerProblem:
    init: State
    goal: State
    actions: list[Action]


class STRIPSPlanner:
    def __init__(self, planner_problem: PlannerProblem) -> None:
        self.planner_problem = planner_problem
        self.state = self.planner_problem.init

    def get_applicable_actions(self) -> list[GroundedAction]:
        ret: list[GroundedAction] = []
        for action in self.planner_problem.actions:
            self.__get_applicable_actions_submethod(ret, GroundedAction(action), set(action.pos_preconditions))
        return ret

    
    def __get_applicable_actions_submethod(self, ret: list[GroundedAction], binding: GroundedAction, pos_preconditions: set[UnboundPredicate]):
        # Now, all preconditions have been picked.
        if not binding.action.pos_effects:
            bound_neg_preconditions = binding.export_bindings(binding.action.neg_preconditions)
            for neg_precond in bound_neg_preconditions:
                if self.state.contains(neg_precond):
                    return
                ret.append(binding)
        else:
            pp = pos_preconditions.pop()
            for sp in self.state.predicates:
                # Different types of predicates can never be in conflict.
                if pp.type != sp.type:
                    continue

                # Compare predicate matching
                if new_binding := binding.add_binding(sp, pp):
                    self.__get_applicable_actions_submethod(ret, new_binding, deepcopy(pos_preconditions))
                else:
                    break

        


