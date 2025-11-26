let tasks = [];

function addTask() {
    const title = document.getElementById("title").value;
    const due = document.getElementById("due_date").value;
    const hours = parseFloat(document.getElementById("estimated_hours").value);
    const imp = parseInt(document.getElementById("importance").value);
    const depsStr = document.getElementById("dependencies").value;

    const deps = depsStr ? depsStr.split(",").map(x => parseInt(x.trim())) : [];

    tasks.push({
        id: tasks.length + 1,
        title: title,
        due_date: due,
        estimated_hours: hours,
        importance: imp,
        dependencies: deps
    });

    alert("Task added!");
}

async function analyzeTasks() {
    let bodyTasks = tasks;

    // If JSON input provided
    const jsonText = document.getElementById("jsonInput").value;
    if (jsonText.trim() !== "") {
        try {
            bodyTasks = JSON.parse(jsonText);
        } catch {
            alert("Invalid JSON format!");
            return;
        }
    }

    const strategy = document.getElementById("strategy").value;

    const res = await fetch("http://127.0.0.1:8000/api/tasks/analyze/?strategy=" + strategy, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tasks: bodyTasks })
    });

    const data = await res.json();
    displayResult(data.tasks);
}

function displayResult(tasks) {
    const output = document.getElementById("output");
    output.innerHTML = "<h2>Results</h2>";

    tasks.forEach(t => {
        let cls = "low";
        if (t.score >= 12) cls = "high";
        else if (t.score >= 8) cls = "medium";

        output.innerHTML += `
            <div class="task ${cls}">
                <h3>${t.title}</h3>
                <p><b>Score:</b> ${t.score}</p>
                <p><b>Due:</b> ${t.due_date}</p>
                <p><b>Hours:</b> ${t.estimated_hours}</p>
                <p><b>Importance:</b> ${t.importance}</p>
                <p><b>Explanation:</b> ${t.explanation}</p>
            </div>
        `;
    });
}
