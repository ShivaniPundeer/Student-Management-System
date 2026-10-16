
const form = document.getElementById("studentForm");
const list = document.getElementById("studentList");
const search = document.getElementById("search");
const message = document.getElementById("message");

let students = [];

async function loadStudents() {
    try {
        const response = await fetch("/api/students");

        if (!response.ok) {
            throw new Error("Could not load students");
        }

        students = await response.json();
        displayStudents();
    } catch (error) {
        message.textContent =
            "Python server start karo, phir try karo.";
    }
}

function displayStudents() {
    const query = search.value.toLowerCase().trim();

    list.replaceChildren();

    students
        .filter(student =>
            student.name.toLowerCase().includes(query) ||
            student.roll.toLowerCase().includes(query)
        )
        .forEach(student => {
            const row = document.createElement("tr");

            [
                student.name,
                student.roll,
                student.course,
                student.marks
            ].forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            const action = document.createElement("td");
            const button = document.createElement("button");

            button.textContent = "Delete";
            button.className = "delete-btn";

            button.onclick = () => deleteStudent(student.id);

            action.appendChild(button);
            row.appendChild(action);
            list.appendChild(row);
        });
}

form.addEventListener("submit", async event => {
    event.preventDefault();

    const student = {
        name: document.getElementById("name").value.trim(),
        roll: document.getElementById("roll").value.trim(),
        course: document.getElementById("course").value.trim(),
        marks: Number(document.getElementById("marks").value)
    };

    try {
        const response = await fetch("/api/students", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(student)
        });

        const result = await response.json();

        if (!response.ok) throw new Error(result.error);

        message.textContent = result.message;
        form.reset();
        await loadStudents();

    } catch (error) {
        message.textContent =
            error.message || "Python server start karo.";
    }
});

async function deleteStudent(id) {
    if (!confirm("Delete this student?")) return;

    try {
        const response = await fetch(`/api/students/${id}`, {
            method: "DELETE"
        });

        const result = await response.json();

        if (!response.ok) throw new Error(result.error);

        message.textContent = result.message;
        await loadStudents();

    } catch (error) {
        message.textContent = error.message;
    }
}

search.addEventListener("input", displayStudents);

loadStudents();
