from flask import Flask, request, redirect, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = "university_management_secret_2026"

# ================= DATABASE =================

def db():
    con = sqlite3.connect("university.db")
    con.row_factory = sqlite3.Row
    return con

MODULES = {
    "students": {
        "title": "Students",
        "fields": [
            ("name", "Student Name", "text"),
            ("email", "Email", "email"),
            ("department", "Department", "text"),
            ("semester", "Semester", "text"),
            ("phone", "Phone", "text")
        ]
    },
    "teachers": {
        "title": "Teachers",
        "fields": [
            ("name", "Teacher Name", "text"),
            ("email", "Email", "email"),
            ("department", "Department", "text"),
            ("phone", "Phone", "text")
        ]
    },
    "courses": {
        "title": "Courses",
        "fields": [
            ("name", "Course Name", "text"),
            ("code", "Course Code", "text"),
            ("department", "Department", "text"),
            ("credit_hours", "Credit Hours", "number")
        ]
    },
    "attendance": {
        "title": "Attendance",
        "fields": [
            ("student", "Student Name", "text"),
            ("course", "Course Code", "text"),
            ("date", "Date", "date"),
            ("status", "Status", "select:Present,Absent,Late")
        ]
    },
    "results": {
        "title": "Results",
        "fields": [
            ("student", "Student Name", "text"),
            ("course", "Course Code", "text"),
            ("exam", "Exam Name", "text"),
            ("marks", "Obtained Marks", "number"),
            ("total", "Total Marks", "number")
        ]
    },
    "fees": {
        "title": "Fees",
        "fields": [
            ("student", "Student Name", "text"),
            ("amount", "Fee Amount", "number"),
            ("status", "Payment Status", "select:Paid,Unpaid")
        ]
    },
    "timetable": {
        "title": "Timetable",
        "fields": [
            ("course", "Course Name", "text"),
            ("day", "Day", "select:Monday,Tuesday,Wednesday,Thursday,Friday,Saturday"),
            ("time", "Time", "text"),
            ("room", "Room Number", "text")
        ]
    }
}

def initialize():
    con = db()

    con.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    for module, config in MODULES.items():
        columns = []
        for field, label, kind in config["fields"]:
            if kind == "number":
                columns.append(f"{field} REAL")
            else:
                columns.append(f"{field} TEXT")

        sql = f"""
            CREATE TABLE IF NOT EXISTS {module}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {",".join(columns)}
            )
        """
        con.execute(sql)

    user = con.execute(
        "SELECT * FROM users WHERE username=?",
        ("admin",)
    ).fetchone()

    if not user:
        con.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            ("admin", generate_password_hash("admin123"))
        )

    con.commit()
    con.close()

initialize()

# ================= LOGIN SECURITY =================

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper

# ================= WEBSITE DESIGN =================

STYLE = """
<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0b1120;
    color: #e5e7eb;
}

.sidebar {
    width: 240px;
    height: 100vh;
    position: fixed;
    background: #111c30;
    padding: 20px;
    overflow-y: auto;
}

.sidebar h2 {
    color: #38bdf8;
    margin-bottom: 30px;
}

.sidebar a {
    display: block;
    color: #cbd5e1;
    text-decoration: none;
    padding: 13px;
    margin: 5px 0;
    border-radius: 7px;
}

.sidebar a:hover {
    background: #263750;
    color: white;
}

.main {
    margin-left: 260px;
    padding: 25px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
}

.card {
    background: #17243a;
    padding: 22px;
    border-radius: 12px;
    margin: 15px 0;
    overflow-x: auto;
}

.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 15px;
}

.number {
    font-size: 30px;
    color: #38bdf8;
    font-weight: bold;
}

input, select {
    display: block;
    width: 100%;
    padding: 12px;
    margin: 10px 0;
    background: #0b1120;
    color: white;
    border: 1px solid #334155;
    border-radius: 6px;
}

button, .btn {
    display: inline-block;
    background: #0284c7;
    color: white;
    padding: 10px 16px;
    border: 0;
    border-radius: 6px;
    cursor: pointer;
    text-decoration: none;
    margin: 3px;
}

button:hover, .btn:hover {
    background: #0369a1;
}

.delete {
    background: #dc2626;
}

.delete:hover {
    background: #991b1b;
}

.edit {
    background: #d97706;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
    min-width: 600px;
}

th, td {
    padding: 12px;
    border-bottom: 1px solid #334155;
    text-align: left;
}

th {
    color: #38bdf8;
}

.message {
    background: #164e63;
    padding: 12px;
    border-radius: 7px;
    margin: 10px 0;
}

.login {
    max-width: 400px;
    margin: 100px auto;
}

.small {
    color: #94a3b8;
    font-size: 13px;
}

@media(max-width: 750px) {
    .sidebar {
        width: 100%;
        height: auto;
        position: relative;
    }

    .main {
        margin: 0;
        padding: 12px;
    }

    .header {
        display: block;
    }
}
</style>
"""

# ================= COMMON PAGE =================

BASE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    """ + STYLE + """
</head>
<body>

{% if session.get('user') %}
<div class="sidebar">
    <h2>🎓 University</h2>
    <a href="/">Dashboard</a>
    <a href="/students">Students</a>
    <a href="/teachers">Teachers</a>
    <a href="/courses">Courses</a>
    <a href="/attendance">Attendance</a>
    <a href="/results">Results</a>
    <a href="/fees">Fees</a>
    <a href="/timetable">Timetable</a>
    <a href="/logout">Logout</a>
</div>
{% endif %}

<div class="{{ 'main' if session.get('user') else 'login' }}">

{% for message in get_flashed_messages() %}
<div class="message">{{ message }}</div>
{% endfor %}

{{ content | safe }}

</div>
</body>
</html>
"""

def page(content, title="University Management System", **data):
    return render_template_string(
        BASE,
        content=content,
        title=title,
        **data
    )

# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        con = db()

        user = con.execute(
            "SELECT * FROM users WHERE username=?",
            (request.form.get("username"),)
        ).fetchone()

        con.close()

        if user and check_password_hash(
            user["password"],
            request.form.get("password", "")
        ):
            session["user"] = user["username"]
            return redirect("/")

        return page("""
        <div class="card">
            <h2>Incorrect Login Details</h2>
            <a href="/login">Try Again</a>
        </div>
        """, "Login")

    return page("""
    <div class="card">
        <h1>🎓 University Login</h1>
        <form method="POST">
            <input name="username" placeholder="Username" required>
            <input name="password" type="password"
                   placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p class="small">Username: admin</p>
        <p class="small">Password: admin123</p>
    </div>
    """, "Login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= DASHBOARD =================

@app.route("/")
@login_required
def dashboard():

    con = db()
    counts = {}

    for module in MODULES:
        counts[module] = con.execute(
            f"SELECT COUNT(*) FROM {module}"
        ).fetchone()[0]

    con.close()

    content = """
    <div class="header">
        <h1>University Dashboard</h1>
        <p>Welcome, {{ session.get('user') }}</p>
    </div>

    <div class="cards">
    """

    for module, config in MODULES.items():
        content += f"""
        <div class="card">
            <h3>{config['title']}</h3>
            <div class="number">{counts[module]}</div>
            <a href="/{module}">View Records →</a>
        </div>
        """

    content += """
    </div>
    <div class="card">
        <h2>University Management System</h2>
        <p>Manage university records from one dashboard.</p>
        <p>Use the sidebar to manage students, teachers,
        courses, attendance, results, fees and timetable.</p>
    </div>
    """

    return page(content, counts=counts)

# ================= ADD / VIEW / EDIT / DELETE =================

@app.route("/<module>")
@login_required
def list_records(module):

    if module not in MODULES:
        return "Page not found", 404

    config = MODULES[module]
    fields = config["fields"]

    con = db()
    records = con.execute(
        f"SELECT * FROM {module} ORDER BY id DESC"
    ).fetchall()
    con.close()

    content = f"""
    <div class="header">
        <h1>{config['title']} Management</h1>
        <a class="btn" href="/{module}/add">+ Add New</a>
    </div>

    <div class="card">
        <h2>All {config['title']}</h2>
        <table>
            <tr>
                <th>ID</th>
    """

    for field, label, kind in fields:
        content += f"<th>{label}</th>"

    content += "<th>Actions</th></tr>"

    for record in records:
        content += f"<tr><td>{record['id']}</td>"

        for field, label, kind in fields:
            value = record[field]
            content += f"<td>{value if value is not None else ''}</td>"

        content += f"""
        <td>
            <a class="btn edit"
               href="/{module}/edit/{record['id']}">Edit</a>

            <form method="POST"
                  action="/{module}/delete/{record['id']}"
                  style="display:inline"
                  onsubmit="return confirm('Are you sure you want to delete this record?')">
                <button class="delete" type="submit">Delete</button>
            </form>
        </td>
        </tr>
        """

    content += """
        </table>
    </div>
    """

    return page(content, config["title"])

# ================= ADD RECORD =================

@app.route("/<module>/add", methods=["GET", "POST"])
@login_required
def add_record(module):

    if module not in MODULES:
        return "Page not found", 404

    config = MODULES[module]
    fields = config["fields"]

    if request.method == "POST":

        values = [request.form.get(field, "").strip()
                  for field, label, kind in fields]

        if not all(values):
            return "Please fill all fields", 400

        if module == "results":
            marks = float(values[3])
            total = float(values[4])
            if marks < 0 or total <= 0 or marks > total:
                return "Invalid marks. Obtained marks must not exceed total marks.", 400

        if module == "fees" and float(values[1]) < 0:
            return "Fee amount cannot be negative.", 400

        columns = ",".join(field for field, label, kind in fields)
        placeholders = ",".join(["?"] * len(fields))

        con = db()
        con.execute(
            f"INSERT INTO {module} ({columns}) VALUES ({placeholders})",
            values
        )
        con.commit()
        con.close()

        return redirect(f"/{module}")

    return form_page(module, config, fields, "Add")

# ================= EDIT RECORD =================

@app.route("/<module>/edit/<int:record_id>", methods=["GET", "POST"])
@login_required
def edit_record(module, record_id):

    if module not in MODULES:
        return "Page not found", 404

    config = MODULES[module]
    fields = config["fields"]

    con = db()
    record = con.execute(
        f"SELECT * FROM {module} WHERE id=?",
        (record_id,)
    ).fetchone()

    if not record:
        con.close()
        return "Record not found", 404

    if request.method == "POST":

        values = [request.form.get(field, "").strip()
                  for field, label, kind in fields]

        if not all(values):
            con.close()
            return "Please fill all fields", 400

        if module == "results":
            marks = float(values[3])
            total = float(values[4])
            if marks < 0 or total <= 0 or marks > total:
                con.close()
                return "Invalid marks. Obtained marks must not exceed total marks.", 400

        if module == "fees" and float(values[1]) < 0:
            con.close()
            return "Fee amount cannot be negative.", 400

        assignments = ",".join(
            f"{field}=?" for field, label, kind in fields
        )

        con.execute(
            f"UPDATE {module} SET {assignments} WHERE id=?",
            values + [record_id]
        )

        con.commit()
        con.close()

        return redirect(f"/{module}")

    con.close()
    return form_page(module, config, fields, "Edit", record)

# ================= FORM DESIGN =================

def form_page(module, config, fields, action, record=None):

    content = f"""
    <div class="card">
        <h1>{action} {config['title']}</h1>

        <form method="POST">
    """

    for field, label, kind in fields:

        value = record[field] if record else ""

        if kind.startswith("select:"):
            options = kind.replace("select:", "").split(",")
            content += f"<label>{label}</label><select name='{field}' required>"

            for option in options:
                selected = "selected" if str(value) == option else ""
                content += f"<option value='{option}' {selected}>{option}</option>"

            content += "</select>"

        else:
            content += f"""
            <label>{label}</label>
            <input
                type="{kind}"
                name="{field}"
                value="{value if value is not None else ''}"
                placeholder="{label}"
                required
            >
            """

    content += f"""
            <button type="submit">{action} Record</button>
            <a class="btn" href="/{module}">Cancel</a>
        </form>
    </div>
    """

    return page(content, action + " " + config["title"])

# ================= DELETE RECORD =================

@app.route("/<module>/delete/<int:record_id>", methods=["POST"])
@login_required
def delete_record(module, record_id):

    if module not in MODULES:
        return "Page not found", 404

    con = db()

    con.execute(
        f"DELETE FROM {module} WHERE id=?",
        (record_id,)
    )

    con.commit()
    con.close()

    return redirect(f"/{module}")

# ================= RUN APPLICATION =================

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)