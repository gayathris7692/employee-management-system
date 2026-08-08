from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("employees.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    search = request.args.get("search", "")

    conn = get_db_connection()

    if search:
        employees = conn.execute(
            """
            SELECT * FROM employees
            WHERE name LIKE ?
               OR email LIKE ?
               OR department LIKE ?
            """,
            (f"%{search}%", f"%{search}%", f"%{search}%")
        ).fetchall()
    else:
        employees = conn.execute(
            "SELECT * FROM employees"
        ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        employees=employees,
        search=search
    )


@app.route("/add", methods=["POST"])
def add_employee():
    name = request.form["name"]
    email = request.form["email"]
    department = request.form["department"]
    salary = request.form["salary"]

    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO employees (name, email, department, salary)
        VALUES (?, ?, ?, ?)
        """,
        (name, email, department, salary)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_employee(id):
    conn = get_db_connection()

    employee = conn.execute(
        "SELECT * FROM employees WHERE id = ?",
        (id,)
    ).fetchone()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]
        salary = request.form["salary"]

        conn.execute(
            """
            UPDATE employees
            SET name = ?, email = ?, department = ?, salary = ?
            WHERE id = ?
            """,
            (name, email, department, salary, id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    conn.close()

    return render_template("edit.html", employee=employee)
@app.route("/delete/<int:id>")
def delete_employee(id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM employees WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    conn = get_db_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            salary REAL NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()

    app.run(debug=True)