from dataclasses import dataclass
from copy import deepcopy
from typing import Iterable
import heapq
from itertools import count

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

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Predicate):
            return False
        return self.variables == value.variables and self.type == value.type

    
class UnboundPredicate:
    def __init__(self, _type: str, *args: Variable) -> None:
        self.type = _type
        self.variables = list(args)

    def __call__(self, *args: list[Constant]) -> Predicate:
        if len(*args) != len(self.variables):
            raise AssertionError("Invalid number of arguments passed to predicate.")
        return Predicate(self.type, *args)
        

    def __str__(self) -> str:
        return f"{self.type}({",".join([str(x) for x in self.variables])})"
    
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
        self.bindings: dict[str, str] = {}

    def is_valid(self) -> bool:
        return len(self.bindings) == len(self.action.params)

    def export_bindings(self, to_modify: Iterable[UnboundPredicate]) -> set[Predicate]:
        if not self.is_valid():
            raise AssertionError("Cannot export bindings: current variable binding is incomplete!")

        ret: set[Predicate] = set()
        for pred in to_modify:
            new_pred = Predicate(pred.type, deepcopy(pred.variables))
            for i, var in enumerate(new_pred.variables):
                new_pred.variables[i] = self.bindings[var]
            ret.add(new_pred)
        return ret 
                

    def add_binding(self, truth_predicate: Predicate, matching_predicate: UnboundPredicate) -> 'GroundedAction|None':
        """Attempt to bind a predicate that is true (all literals have constant assignments) 
        to an unset predicate (all literals are variables). 
        It will then check if there is a conflict between these assignments and previous assignments.
        It will return None if there is a conflict, or a new binding if it is OK."""
        g = GroundedAction(action=self.action)
        new_bindings: dict[str, str] = deepcopy(self.bindings)

        for truth_var, matching_var in zip(truth_predicate.variables, matching_predicate.variables):
            # Binding does not work, already bound to something.
            if matching_var in new_bindings and new_bindings[matching_var] != truth_var:
                return None
            else:
                new_bindings[str(matching_var)] = truth_var
        g.bindings = new_bindings
        return g
            
    def __str__(self) -> str:
        params=", ".join([f"{x}={y}" for x, y in self.bindings.items()])
        return f"name({params})"
    
    def __repr__(self) -> str:
        return self.__str__()

class State:
    def __init__(self, predicates: set[Predicate]) -> None:
        self.predicates = predicates

    def satisfies(self, other_predicates: 'State') -> bool:
        """Check if all input predicates hold in the current state.""" 
        return other_predicates.predicates.issubset(self.predicates)

    def contains(self, other_predicate: Predicate) -> bool:
        return other_predicate in self.predicates
    
    def apply_action(self, action: GroundedAction) -> 'State':
        neg_effects = action.export_bindings(action.action.neg_effects)
        pos_effects = action.export_bindings(action.action.pos_effects)
        return State((self.predicates - neg_effects).union(pos_effects))

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, State):
            return False
        return self.predicates == value.predicates

    def __str__(self) -> str:
       return ",".join([str(x) for x in self.predicates]) 

    def __repr__(self) -> str:
       return self.__str__()

    def __hash__(self) -> int:
       return hash(self.__str__())

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
        if not pos_preconditions:
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


    def fwdSearch(self) -> list[GroundedAction]|None:
        @dataclass
        class SearchNode:
            state: State
            action: GroundedAction|None
            prev_node: 'SearchNode|None'
            

        def solution(node: SearchNode|None) -> list[GroundedAction]:
            ret = []
            while node and node.action:
                ret.append(node.action)
                node = node.prev_node
            return ret
            
        counter = count()
        frontier = []
        heapq.heappush(frontier, (0, next(counter), SearchNode(self.state, None, None)))
        visited: set[State] = set()
        while frontier:
            print(visited)
            priority, _, node = heapq.heappop(frontier)
            visited.add(node.state)
            if node.state.satisfies(self.planner_problem.goal):
                print(node.state)
                return solution(node)
                
            applicables = self.get_applicable_actions()
            for action in applicables:
                new_state = node.state.apply_action(action)
                if new_state not in visited:
                    heapq.heappush(frontier, (priority + 1, next(counter), SearchNode(state=new_state, action=action, prev_node=node)))

        return None

        
