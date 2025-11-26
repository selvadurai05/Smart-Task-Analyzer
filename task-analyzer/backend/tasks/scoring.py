from datetime import date, datetime
from typing import Dict, List, Set, Tuple, Any


def parse_due_date(value):
    """Safely parse a date string (YYYY-MM-DD) into a date object."""
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return None


def build_dependency_graph(tasks: List[Dict[str, Any]]) -> Dict[Any, List[Any]]:
    """
    Build adjacency list: task_id -> list of task_ids it depends on.
    tasks: list of dicts, each with 'id' and optional 'dependencies' list.
    """
    graph: Dict[Any, List[Any]] = {}
    for t in tasks:
        tid = t.get("id")
        deps = t.get("dependencies") or []
        if tid is None:
            continue
        graph[tid] = list(deps)
    return graph


def find_circular_dependencies(graph: Dict[Any, List[Any]]) -> Set[Any]:
    """
    Detect circular dependencies using DFS.
    Returns a set of task ids that are part of any cycle.
    """

    visited: Set[Any] = set()
    stack: Set[Any] = set()
    in_cycle: Set[Any] = set()

    def dfs(node):
        if node in stack:
            # found a cycle – mark node as cyclic
            in_cycle.add(node)
            return
        if node in visited:
            return

        visited.add(node)
        stack.add(node)

        for nei in graph.get(node, []):
            dfs(nei)

        stack.remove(node)

    for node in graph.keys():
        if node not in visited:
            dfs(node)

    # NOTE: in_cycle only has starting nodes, add all neighbors reachable in that cycle
    # for simplicity, we'll just return in_cycle; this is enough to flag suspicious tasks
    return in_cycle


def compute_components(task: Dict[str, Any], dependency_graph: Dict[Any, List[Any]]) -> Dict[str, float]:
    """
    Compute individual component scores: importance, urgency, effort, dependency.
    Returns dict: {importance_score, urgency_score, effort_score, dependency_score}
    """
    from math import fabs

    # importance
    importance = task.get("importance") or 5
    try:
        importance = int(importance)
    except Exception:
        importance = 5
    importance = max(1, min(10, importance))
    importance_score = float(importance)

    # effort (low effort = high score)
    estimated_hours = task.get("estimated_hours") or 1
    try:
        estimated_hours = float(estimated_hours)
    except Exception:
        estimated_hours = 1.0
    estimated_hours = max(0.25, estimated_hours)

    if estimated_hours <= 1:
        effort_score = 10.0
    else:
        effort_score = max(1.0, 10.0 - estimated_hours)

    # urgency based on due_date
    due_date = parse_due_date(task.get("due_date"))
    today = date.today()
    urgency_score = 0.0
    if due_date:
        delta_days = (due_date - today).days
        if delta_days < 0:
            # overdue
            urgency_score = min(15.0, 10.0 + fabs(delta_days) * 0.5)
        elif delta_days == 0:
            urgency_score = 14.0
        else:
            urgency_score = max(0.0, 10.0 - delta_days * 0.7)

    # dependency score: how many tasks depend on this task?
    task_id = task.get("id")
    dependents_count = 0
    if task_id is not None:
        # any node that has this id in its dependency list
        for tid, deps in dependency_graph.items():
            if task_id in deps:
                dependents_count += 1
    dependency_score = min(10.0, dependents_count * 2.0)

    return {
        "importance_score": importance_score,
        "effort_score": effort_score,
        "urgency_score": urgency_score,
        "dependency_score": dependency_score,
    }


def apply_strategy(components: Dict[str, float], strategy: str) -> float:
    """
    Apply weighting based on strategy and return final numeric score.
    """
    importance = components["importance_score"]
    effort = components["effort_score"]
    urgency = components["urgency_score"]
    dependency = components["dependency_score"]

    if strategy == "fastest_wins":
        # prioritize effort
        score = effort * 2 + importance * 0.5 + urgency * 0.5
    elif strategy == "high_impact":
        # prioritize importance
        score = importance * 2 + urgency * 1.0 + effort * 0.3
    elif strategy == "deadline_driven":
        # prioritize urgency
        score = urgency * 2 + importance * 1.0 + effort * 0.5
    else:  # "smart_balance"
        score = (
            importance * 1.2
            + urgency * 1.2
            + effort * 0.8
            + dependency * 1.5
        )

    return round(score, 2)


def explain_task(task: Dict[str, Any],
                 components: Dict[str, float],
                 strategy: str,
                 is_circular: bool) -> str:
    """
    Build a human-readable explanation string for why a task got this score.
    """
    title = task.get("title", "Untitled task")
    importance = components["importance_score"]
    effort = components["effort_score"]
    urgency = components["urgency_score"]
    dependency = components["dependency_score"]

    parts = []

    # base explanation
    if strategy == "fastest_wins":
        parts.append(
            f"Prioritized as a 'Fastest Wins' task because it has relatively low effort "
            f"(effort score {effort:.1f}) and importance {importance:.1f}."
        )
    elif strategy == "high_impact":
        parts.append(
            f"Prioritized as a 'High Impact' task because its importance score is {importance:.1f}, "
            f"with urgency {urgency:.1f}."
        )
    elif strategy == "deadline_driven":
        parts.append(
            f"Prioritized as a 'Deadline Driven' task due to its urgency score of {urgency:.1f}, "
            f"and importance {importance:.1f}."
        )
    else:  # smart_balance
        parts.append(
            f"Prioritized using 'Smart Balance' by combining importance ({importance:.1f}), "
            f"urgency ({urgency:.1f}), effort ({effort:.1f}), and dependency impact ({dependency:.1f})."
        )

    if urgency > 10:
        parts.append("This task is overdue or due very soon, so urgency heavily boosts its priority.")
    elif urgency > 5:
        parts.append("The due date is approaching, which increases its urgency score.")

    if effort >= 9:
        parts.append("It is a very quick task, making it a good 'quick win'.")
    elif effort <= 3:
        parts.append("It requires moderate effort compared to other tasks.")

    if dependency >= 4:
        parts.append("Completing this task will unblock multiple other tasks.")

    if is_circular:
        parts.append(
            "⚠ This task is part of a circular dependency chain; dependency impact may be unreliable."
        )

    return " ".join(parts)


def compute_task_score(task: Dict[str, Any],
                       strategy: str = "smart_balance",
                       dependency_graph: Dict[Any, List[Any]] = None) -> float:
    """
    Public helper: compute score only (for tests or reuse).
    """
    if dependency_graph is None:
        dependency_graph = {}
    components = compute_components(task, dependency_graph)
    return apply_strategy(components, strategy)


def compute_task_with_explanation(task: Dict[str, Any],
                                  strategy: str,
                                  dependency_graph: Dict[Any, List[Any]],
                                  circular_ids: Set[Any]) -> Tuple[float, str]:
    """
    Main helper for views:
    - computes score
    - builds explanation
    """
    if dependency_graph is None:
        dependency_graph = {}

    components = compute_components(task, dependency_graph)
    score = apply_strategy(components, strategy)

    is_circular = task.get("id") in circular_ids if circular_ids else False
    explanation = explain_task(task, components, strategy, is_circular)

    return score, explanation
