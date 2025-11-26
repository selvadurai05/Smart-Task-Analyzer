Sooper da, UI settled 😎🔥
Ippa almost full assignment ready. Next step: **README.md** + **GitHub** → submit panradhu.

Na unakku **ready-made README** kudukuren. Nee `task-analyzer/README.md` la **copy–paste** panna pothum. (konjam time breakdown numbers la nee unmai-ku adjust panniko).

---

## 1️⃣ README.md – full content (paste as is)

`task-analyzer/README.md` create pannitu idha paste pannu 👇

````markdown
# Smart Task Analyzer – Internship Assignment

A mini web application that scores and prioritizes tasks using multiple strategies.  
Backend is built with **Django + Django REST Framework**, and frontend is a simple **HTML/CSS/JavaScript** interface.

---

## 🔧 Tech Stack

- **Backend:** Python 3.10+, Django 5.x, Django REST Framework
- **Frontend:** HTML, CSS, Vanilla JavaScript (fetch API)
- **Database:** SQLite (default Django)
- **Testing:** Django `SimpleTestCase`

---

## 🚀 Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd task-analyzer
````

### 2. Backend setup

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

By default, the API will run at:

```text
http://127.0.0.1:8000/
```

### 3. Frontend setup

No build tools are required.

* Open `frontend/index.html` directly in your browser (double-click or "Open With > Browser").
* Make sure the backend server is running before clicking **Analyze Tasks**.

---

## 🧠 API Endpoints

### `POST /api/tasks/analyze/?strategy=...`

Analyzes and scores a list of tasks and returns them sorted by priority.

* **Body (JSON)**

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Fix login bug",
      "due_date": "2025-11-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": []
    }
  ]
}
```

* **Query param**

`strategy` can be one of:

* `smart_balance` (default)

* `fastest_wins`

* `high_impact`

* `deadline_driven`

* **Response (shape)**

```json
{
  "strategy": "smart_balance",
  "has_circular_dependencies": false,
  "circular_task_ids": [],
  "tasks": [
    {
      "id": 1,
      "title": "Fix login bug",
      "due_date": "2025-11-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": [],
      "score": 12.34,
      "explanation": "Human-readable explanation..."
    }
  ]
}
```

---

### `GET /api/tasks/suggest/`

Returns the **top 3 suggested tasks** for today, with explanations.

* If the client sends tasks in the request body (as JSON), those tasks are used.

* If no tasks are provided, the endpoint uses a small built-in sample list and sets `used_sample_data: true` in the response, so the behavior is explicit.

* **Response (shape)**

```json
{
  "strategy": "smart_balance",
  "used_sample_data": true,
  "has_circular_dependencies": false,
  "circular_task_ids": [],
  "suggested_tasks": [
    {
      "id": 1,
      "title": "Reply to important emails",
      "score": 13.21,
      "explanation": "..."
    }
  ]
}
```

---

## 🧪 Running Tests

The project includes unit tests for the scoring algorithm.

```bash
cd backend
.venv\Scripts\activate
python manage.py test tasks
```

---

## 🧮 Algorithm Explanation (Smart Task Scoring)

The core of this assignment is the priority scoring logic implemented in `tasks/scoring.py`. Each task is treated as a dictionary with fields like `title`, `due_date`, `estimated_hours`, `importance`, and `dependencies`. The algorithm first normalizes the input (fills missing values with sensible defaults) and then computes four component scores: **importance**, **urgency**, **effort**, and **dependency impact**.

Importance is a direct mapping of the user-provided value on a 1–10 scale, clamped to remain within that range. Effort is modeled so that low-effort tasks receive higher scores: tasks under one hour are treated as “quick wins” and get a high effort score, while long tasks get progressively lower scores. This allows the application to prioritize small wins in strategies like “Fastest Wins”.

Urgency is derived from the due date relative to today. Tasks with no due date receive zero urgency. Tasks due in the future get an urgency value that decreases as the due date moves further away, while tasks that are due today or already overdue receive a strong boost. Overdue tasks in particular get their urgency capped at a maximum, reflecting that they are already late and should be pulled to the top.

Dependency impact measures how many other tasks depend on a given task. A directed graph is built from the dependencies, and for each task, the algorithm counts how many other tasks list it in their dependency list. This count is scaled and capped to avoid extremes. There is also a lightweight circular dependency check using depth-first search; tasks that participate in a cycle are flagged so the explanation can warn that their dependency impact may be unreliable.

On top of these components, different strategies apply different weightings. **Fastest Wins** emphasizes effort, **High Impact** emphasizes importance, **Deadline Driven** emphasizes urgency, and **Smart Balance** combines all four signals with more even weights. Scores are rounded for readability, and every task receives a human-readable explanation string that describes why it received that score, referencing urgency, effort, impact, and dependencies in plain language.

---

## 🧠 Design Decisions

* **Django REST Framework** was chosen for clean API views and easy JSON handling.
* A dedicated `scoring.py` module keeps the scoring logic isolated and testable.
* Strategy is passed as a query parameter so the same API can support multiple views (Fastest Wins, High Impact, etc.).
* Circular dependencies are detected and surfaced in the response instead of silently ignored.
* The `SuggestTasks` endpoint can work with client-provided tasks or a simple built-in sample, ensuring it always demonstrates behavior even without persistence.

---

## 🎨 Frontend Overview

* Simple, responsive layout with two main panels:

  * **Task Input**: form fields to add individual tasks + a textarea to paste raw JSON.
  * **Analyze**: strategy selector and “Analyze Tasks” button.
* Results are rendered as cards with **color-coded priority**:

  * Red bar = High priority
  * Yellow bar = Medium
  * Green bar = Low
* The frontend communicates with the backend using `fetch` and displays the score and explanation for each task.

---

## ⏱ Time Breakdown (approximate)

> You can adjust these numbers to match your actual time.

* Backend design & implementation: ~1.5 hours
* Scoring algorithm & strategies: ~1 hour
* Circular dependency handling & tests: ~45 minutes
* Frontend (HTML/CSS/JS): ~45 minutes
* Debugging, polishing & documentation: ~30 minutes

---

## 🎯 Bonus Challenges

* **Circular dependencies** are detected and reported at the API level.
* No separate graph visualization / ML-based learning system is implemented due to time, but the scoring logic is structured so it can be extended.

---

## 🔭 Future Improvements

* Persist tasks in the database and let `/api/tasks/suggest/` query real user data.
* Add a visual dependency graph to highlight blocking tasks and cycles.
* Add an Eisenhower Matrix view (Urgent vs Important) on the frontend.
* Allow users to customize weights for urgency/importance/effort/dependencies.
* Add pagination and filtering for large task lists.
* Improve mobile UX and add light/dark mode toggle.

<img width="1920" height="1080" alt="Screenshot (107)" src="https://github.com/user-attachments/assets/67e44255-4faf-4188-b191-1493e55a87de" />

````

---

## 2️⃣ Quick GitHub push steps (in case you need)

Repo create pannirundha illatti:

```bash
cd task-analyzer
git init
git add .
git commit -m "Smart Task Analyzer - assignment"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
