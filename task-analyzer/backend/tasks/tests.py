from django.test import SimpleTestCase

from .scoring import (
    compute_task_score,
    build_dependency_graph,
    find_circular_dependencies,
)


class ScoringAlgorithmTests(SimpleTestCase):
    """
    Unit tests for the Smart Task Analyzer scoring logic.
    """

    def test_overdue_task_gets_higher_score_than_future_task(self):
        """
        Overdue task should generally have higher score than a similar task
        with a future due date, when using the deadline-driven strategy.
        """
        overdue_task = {
            "id": 1,
            "title": "Overdue task",
            "due_date": "2024-01-01",  # long past
            "estimated_hours": 2,
            "importance": 7,
            "dependencies": [],
        }

        future_task = {
            "id": 2,
            "title": "Future task",
            "due_date": "2030-01-01",  # far in future
            "estimated_hours": 2,
            "importance": 7,
            "dependencies": [],
        }

        graph = build_dependency_graph([overdue_task, future_task])

        overdue_score = compute_task_score(
            overdue_task,
            strategy="deadline_driven",
            dependency_graph=graph,
        )
        future_score = compute_task_score(
            future_task,
            strategy="deadline_driven",
            dependency_graph=graph,
        )

        self.assertGreater(
            overdue_score,
            future_score,
            msg="Overdue task should have higher score than future task",
        )

    def test_low_effort_task_scored_higher_in_fastest_wins(self):
        """
        Under the 'fastest_wins' strategy, a low-effort task should get
        a higher score than a high-effort task with same importance/due date.
        """
        low_effort = {
            "id": 1,
            "title": "Quick task",
            "due_date": "2030-01-01",
            "estimated_hours": 0.5,
            "importance": 5,
            "dependencies": [],
        }

        high_effort = {
            "id": 2,
            "title": "Big task",
            "due_date": "2030-01-01",
            "estimated_hours": 8,
            "importance": 5,
            "dependencies": [],
        }

        graph = build_dependency_graph([low_effort, high_effort])

        low_effort_score = compute_task_score(
            low_effort,
            strategy="fastest_wins",
            dependency_graph=graph,
        )
        high_effort_score = compute_task_score(
            high_effort,
            strategy="fastest_wins",
            dependency_graph=graph,
        )

        self.assertGreater(
            low_effort_score,
            high_effort_score,
            msg="Low-effort task should have higher score under 'fastest_wins'",
        )

    def test_circular_dependencies_detected(self):
        """
        Circular dependencies between tasks should be detected by
        find_circular_dependencies.
        """
        tasks = [
            {
                "id": 1,
                "title": "Task A",
                "due_date": None,
                "estimated_hours": 1,
                "importance": 5,
                "dependencies": [2],  # depends on B
            },
            {
                "id": 2,
                "title": "Task B",
                "due_date": None,
                "estimated_hours": 1,
                "importance": 5,
                "dependencies": [1],  # depends on A -> cycle
            },
        ]

        graph = build_dependency_graph(tasks)
        circular_ids = find_circular_dependencies(graph)

        self.assertTrue(
            len(circular_ids) > 0,
            msg="Circular dependency set should not be empty",
        )
        self.assertTrue(
            1 in circular_ids or 2 in circular_ids,
            msg="At least one of the cyclic tasks should be reported as circular",
        )
