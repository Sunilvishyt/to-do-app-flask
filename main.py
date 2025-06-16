import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, StringField
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import DataRequired
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_title = db.Column(db.String(200))
    task_desc = db.Column(db.String(400))


class CompletedTasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_title = db.Column(db.String(200))
    task_desc = db.Column(db.String(400))


class TaskForm(FlaskForm):
    checkbox = BooleanField("checkbox", default=False)
    submit = SubmitField()


class NewTask(FlaskForm):
    task_title = StringField(
        "task title",
        validators=[DataRequired()],
        render_kw={"autocomplete": "off", "placeholder": "task title"},
    )
    task_description = StringField(
        "task Description (if any)",
        render_kw={"autocomplete": "off", "placeholder": "task description"},
    )
    submit = SubmitField()


with app.app_context():
    if not os.path.exists("data.db"):
        db.create_all()


@app.route("/", methods=["get", "post"])
def home():
    form = TaskForm()
    all_tasks = Tasks.query.all()
    if request.method == "POST":
        completed_tasks = request.form.getlist(
            "completed_tasks"
        )  # only the clicked checkboxes are submitted in the html the not clicked are not send by the html so you wont see them.
        for task_id in completed_tasks:
            task = db.session.get(
                Tasks, task_id
            )  # get method is used for the primary key if its not a primary key we will use the filter by.
            if task:
                completed_task = task.task_title
                completed_task_desc = task.task_desc
                entry = CompletedTasks(
                    task_title=completed_task, task_desc=completed_task_desc
                )
                db.session.add(entry)
                db.session.commit()
                db.session.delete(task)
            db.session.commit()
        return redirect(url_for("home"))
    print(all_tasks)
    return render_template(
        "index.html", all_tasks=all_tasks, form=form, empty=len(all_tasks)
    )


@app.route("/add-task", methods=["get", "post"])
def add_task():
    form = NewTask()
    if form.validate_on_submit():
        task = form.task_title.data
        description = form.task_description.data
        entry = Tasks(task_title=task, task_desc=description)
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_task.html", form=form)


@app.route("/completed-tasks", methods=["get", "post"])
def completed():
    form = NewTask()
    all_tasks = CompletedTasks.query.all()
    if request.method == "POST":
        completed_task = request.form.getlist("completed_tasks")
        for task_id in completed_task:
            task = db.session.get(CompletedTasks, task_id)
            if task:
                db.session.delete(task)
            db.session.commit()
        return redirect(url_for("completed"))
    return render_template(
        "completed_tasks.html", all_tasks=all_tasks, form=form, empty=len(all_tasks)
    )


if __name__ == "__main__":
    app.run(debug=False)
