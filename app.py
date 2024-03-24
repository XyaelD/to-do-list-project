import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tasks.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Renders the task list for a given date"""

    # By default, will render the current date's task list
    date = datetime.date.today()
    # Yesterday and tomorrow are always fetched as well for quick-nav buttons next to the current date;
    # The data type needs to be a datetime.date to successfully utilize the timedelta function
    yesterday = date - datetime.timedelta(days=1)
    tomorrow = date + datetime.timedelta(days=1)

    # Search the database for the relevant data for the user
    rows = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND date = ?", session["user_id"], date
    )

    # Render the main page with the data
    return render_template(
        "index.html", rows=rows, date=date, yesterday=yesterday, tomorrow=tomorrow
    )


@app.route("/add", methods=["POST"])
@login_required
def add():
    """Adds a task based on the date on the page"""

    # Server side catching of errors
    if not request.form.get("hidden-date"):
        return apology("There was a problem getting the date!")
    if not request.form.get("task"):
        return apology("You need to input a task!")
    # This will always be fed from the request the render the template successfully using the correct date
    date_from_page = request.form.get("hidden-date")
    # The date needs to be converted from a str to a datetime.date object
    date = datetime.datetime.strptime(date_from_page, "%Y-%m-%d").date()
    task = request.form.get("task")
    yesterday = date - datetime.timedelta(days=1)
    tomorrow = date + datetime.timedelta(days=1)

    # Add the task into the correct location in the database
    db.execute(
        "INSERT INTO tasks (user_id, date, task) VALUES (?,?,?)",
        session["user_id"],
        date,
        task,
    )

    # Every time the database gets updated, the rows need to be fetched again with the updated data
    updated_rows = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND date = ?", session["user_id"], date
    )

    # Uses the flash feature to give user feedback
    flash("Added a new task!", "success")
    return render_template(
        "index.html",
        rows=updated_rows,
        date=date,
        yesterday=yesterday,
        tomorrow=tomorrow,
    )


@app.route("/update", methods=["POST"])
@login_required
def update():
    """Updates tasks for a date or deletes a single task"""

    # If the update route was sent an item to be deleted:
    if "delete-task" in request.form:
        if not request.form.get("hidden-date"):
            return apology("There was a problem getting the date!")
        if not request.form.get("delete-task"):
            return apology("You need to select a valid task to delete!")
        to_delete = request.form.get("delete-task")
        date_from_page = request.form.get("hidden-date")
        date = datetime.datetime.strptime(date_from_page, "%Y-%m-%d").date()
        yesterday = date - datetime.timedelta(days=1)
        tomorrow = date + datetime.timedelta(days=1)

        # Delete the appropriate task from the database
        db.execute(
            "DELETE FROM TASKS WHERE user_id = ? AND DATE = ? AND id = ?",
            session["user_id"],
            date,
            to_delete,
        )

        updated_rows = db.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND date = ?",
            session["user_id"],
            date,
        )

        flash("Task successfully deleted!", "success")

        return render_template(
            "index.html",
            rows=updated_rows,
            date=date,
            yesterday=yesterday,
            tomorrow=tomorrow,
        )

    # If the update request was a normal update request:
    if not request.form.get("hidden-date"):
        return apology("There was a problem getting the date!")

    # The 'checked-tasks' is not validated because it can be nothing since all checkboxes could be set to nothing and the unchecked tasks depends on this
    to_update = request.form.getlist("checked-tasks")
    date_from_page = request.form.get("hidden-date")
    date = datetime.datetime.strptime(date_from_page, "%Y-%m-%d").date()
    yesterday = date - datetime.timedelta(days=1)
    tomorrow = date + datetime.timedelta(days=1)

    rows = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND date = ?", session["user_id"], date
    )
    # This is why nothing for checked-tasks is okay:
    unchecked_tasks = [row["id"] for row in rows if row["id"] not in to_update]

    # Update all tasks based on whether they were checked off or not (every task is now in one of the two lists)
    # The completed variable gets changed to TRUE or FALSE, but SQLITE stores this as 1 or 0
    if to_update is None:
        for task in unchecked_tasks:
            db.execute(
                "UPDATE tasks SET completed = FALSE WHERE user_id = ? AND ID = ?",
                session["user_id"],
                task,
            )

    for task in unchecked_tasks:
        db.execute(
            "UPDATE tasks SET completed = FALSE WHERE user_id = ? AND ID = ?",
            session["user_id"],
            task,
        )

    for task in to_update:
        db.execute(
            "UPDATE tasks SET completed = TRUE WHERE user_id = ? AND ID = ?",
            session["user_id"],
            task,
        )

    updated_rows = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND date = ?", session["user_id"], date
    )

    flash("All tasks successfully updated!", "success")
    return render_template(
        "index.html",
        rows=updated_rows,
        date=date,
        yesterday=yesterday,
        tomorrow=tomorrow,
    )


@app.route("/getdate", methods=["POST"])
@login_required
def getdate():
    """Renders the task list for a specified date"""

    date_to_get = request.form.get("task-day")
    date = datetime.datetime.strptime(date_to_get, "%Y-%m-%d").date()
    yesterday = date - datetime.timedelta(days=1)
    tomorrow = date + datetime.timedelta(days=1)

    rows = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND date = ?",
        session["user_id"],
        date_to_get,
    )

    return render_template(
        "index.html",
        rows=rows,
        date=date_to_get,
        yesterday=yesterday,
        tomorrow=tomorrow,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Server side catching of errors
        if not request.form.get("username"):
            return apology("Please provide a username", 403)
        elif not request.form.get("password"):
            return apology("Please provide a password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Logged in successfully!", "success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    flash("Logged out successfully!", "success")
    # Redirect user to login form
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Check if the username is filled out
        if not request.form.get("username"):
            return apology("The username field is empty!", 400)

        # Check if the username is already in the database
        username = request.form.get("username")
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) == 1:
            return apology("That username already exists!", 400)

        # Check that the password fields are filled out
        if not request.form.get("password") or not request.form.get("confirmation"):
            return apology("The password or confirmation fields are empty!", 400)

        # Check that the password fields match
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            return apology("The password and confirmation fields must match!", 400)

        # Register the new user in the database
        hash = generate_password_hash(password, method="pbkdf2", salt_length=16)
        db.execute("INSERT INTO users (username, hash) VALUES (?,?)", username, hash)

        flash("Registration successful! Please log in!", "success")
        # Go to login screen
        return render_template("login.html")
    else:
        return render_template("register.html")
