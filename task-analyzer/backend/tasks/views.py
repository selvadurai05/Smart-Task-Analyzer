from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .scoring import (
    build_dependency_graph,
    find_circular_dependencies,
    compute_task_with_explanation,
)


class AnalyzeTasksView(APIView):
    """
    POST /api/tasks/analyze/
    Body:
      Either:
        [ {task1}, {task2}, ... ]
      or:
        { "tasks": [ {task1}, {task2}, ... ] }

    Optional query param:
      ?strategy=fastest_wins|high_impact|deadline_driven|smart_balance
    """

    def post(self, request):
        data = request.data
        if isinstance(data, dict) and "tasks" in data:
            tasks = data["tasks"]
        else:
            tasks = data

        if not isinstance(tasks, list):
            return Response(
                {"error": "Expected a list of tasks or {'tasks': [...]}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure each task has an id
        normalized_tasks = []
        for idx, t in enumerate(tasks):
            t = dict(t)
            t.setdefault("id", idx + 1)
            t.setdefault("title", f"Task {idx + 1}")
            t.setdefault("estimated_hours", 1)
            t.setdefault("importance", 5)
            t.setdefault("dependencies", t.get("dependencies") or [])
            normalized_tasks.append(t)

        # Build graph & detect cycles
        dependency_graph = build_dependency_graph(normalized_tasks)
        circular_ids = find_circular_dependencies(dependency_graph)

        strategy = request.query_params.get("strategy", "smart_balance")

        scored_tasks = []
        for t in normalized_tasks:
            score, explanation = compute_task_with_explanation(
                t,
                strategy=strategy,
                dependency_graph=dependency_graph,
                circular_ids=circular_ids,
            )
            t_with_score = dict(t)
            t_with_score["score"] = score
            t_with_score["explanation"] = explanation
            scored_tasks.append(t_with_score)

        scored_tasks.sort(key=lambda x: x["score"], reverse=True)

        response_payload = {
            "strategy": strategy,
            "has_circular_dependencies": bool(circular_ids),
            "circular_task_ids": list(circular_ids),
            "tasks": scored_tasks,
        }

        return Response(response_payload, status=status.HTTP_200_OK)


class SuggestTasksView(APIView):
    """
    GET /api/tasks/suggest/
    Behaviour:

    - If the client sends tasks in the request body (even though it's a GET),
      we'll use those tasks and return the top 3 for today.
    - If no tasks are provided, we return a small sample suggestion list,
      with a note explaining this assumption.
    """

    def get(self, request):
        data = request.data

        if isinstance(data, dict) and "tasks" in data:
            tasks = data["tasks"]
        else:
            tasks = data

        used_sample = False

        # If no tasks provided, use a simple sample list so endpoint always works
        if not isinstance(tasks, list) or len(tasks) == 0:
            used_sample = True
            from datetime import date, timedelta

            today = date.today()
            tasks = [
                {
                    "id": 1,
                    "title": "Reply to important emails",
                    "due_date": today.isoformat(),
                    "estimated_hours": 1,
                    "importance": 8,
                    "dependencies": [],
                },
                {
                    "id": 2,
                    "title": "Finish project report",
                    "due_date": (today + timedelta(days=1)).isoformat(),
                    "estimated_hours": 4,
                    "importance": 9,
                    "dependencies": [],
                },
                {
                    "id": 3,
                    "title": "Refactor legacy code",
                    "due_date": (today + timedelta(days=3)).isoformat(),
                    "estimated_hours": 3,
                    "importance": 7,
                    "dependencies": [],
                },
                {
                    "id": 4,
                    "title": "Quick UI bug fix",
                    "due_date": today.isoformat(),
                    "estimated_hours": 0.5,
                    "importance": 6,
                    "dependencies": [],
                },
            ]

        # normalize tasks
        normalized_tasks = []
        for idx, t in enumerate(tasks):
            t = dict(t)
            t.setdefault("id", idx + 1)
            t.setdefault("title", f"Task {idx + 1}")
            t.setdefault("estimated_hours", 1)
            t.setdefault("importance", 5)
            t.setdefault("dependencies", t.get("dependencies") or [])
            normalized_tasks.append(t)

        dependency_graph = build_dependency_graph(normalized_tasks)
        circular_ids = find_circular_dependencies(dependency_graph)

        # For suggest, "smart_balance" is default
        strategy = request.query_params.get("strategy", "smart_balance")

        scored_tasks = []
        for t in normalized_tasks:
            score, explanation = compute_task_with_explanation(
                t,
                strategy=strategy,
                dependency_graph=dependency_graph,
                circular_ids=circular_ids,
            )
            t_with_score = dict(t)
            t_with_score["score"] = score
            t_with_score["explanation"] = explanation
            scored_tasks.append(t_with_score)

        scored_tasks.sort(key=lambda x: x["score"], reverse=True)

        top_3 = scored_tasks[:3]

        response_payload = {
            "strategy": strategy,
            "used_sample_data": used_sample,
            "has_circular_dependencies": bool(circular_ids),
            "circular_task_ids": list(circular_ids),
            "suggested_tasks": top_3,
        }

        return Response(response_payload, status=status.HTTP_200_OK)
