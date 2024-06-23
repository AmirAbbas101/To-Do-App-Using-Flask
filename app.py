import os
from flask import Flask, request, render_template
from datetime import date
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Load secret key from environment variable
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'defaultsecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Task('{self.content}')"

# Get today's date in two different formats
datetoday = date.today().strftime("%m_%d_%y")
datetoday2 = date.today().strftime("%d-%B-%Y")

# Function to create database and tables
def create_tables():
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Error creating tables: {e}")

# Function to get the task list from the database
def get_task_list():
    try:
        tasks = Task.query.all()
        tasklist = [task.content for task in tasks]
        return tasklist
    except Exception as e:
        app.logger.error(f"Error retrieving tasks: {e}")
        return []

# Route for the home page
@app.route('/')
def home():
    try:
        tasklist = get_task_list()
        return render_template('home.html', datetoday2=datetoday2, tasklist=tasklist, l=len(tasklist))
    except Exception as e:
        app.logger.error(f"Error rendering home page: {e}")
        return render_template('500.html'), 500

# Route to clear the to-do list
@app.route('/clear')
def clear_list():
    try:
        db.session.query(Task).delete()
        db.session.commit()
        tasklist = get_task_list()
        return render_template('home.html', datetoday2=datetoday2, tasklist=tasklist, l=len(tasklist))
    except Exception as e:
        app.logger.error(f"Error clearing task list: {e}")
        db.session.rollback()
        return render_template('500.html'), 500

# Route to add a task to the to-do list
@app.route('/addtask', methods=['POST'])
def add_task():
    try:
        task_content = request.form.get('newtask')
        if task_content:
            new_task = Task(content=task_content)
            db.session.add(new_task)
            db.session.commit()
        tasklist = get_task_list()
        return render_template('home.html', datetoday2=datetoday2, tasklist=tasklist, l=len(tasklist))
    except Exception as e:
        app.logger.error(f"Error adding task: {e}")
        db.session.rollback()
        return render_template('500.html'), 500

# Route to remove a task from the to-do list
@app.route('/deltask', methods=['GET'])
def remove_task():
    try:
        task_index = int(request.args.get('deltaskid'))
        tasks = Task.query.all()

        if task_index < 0 or task_index >= len(tasks):
            return render_template('home.html', datetoday2=datetoday2, tasklist=get_task_list(), l=len(tasks), mess='Invalid Index...')
        else:
            task_to_delete = tasks[task_index]
            db.session.delete(task_to_delete)
            db.session.commit()
        
        tasklist = get_task_list()
        return render_template('home.html', datetoday2=datetoday2, tasklist=tasklist, l=len(tasklist))
    except ValueError:
        app.logger.error("Invalid task index provided.")
        return render_template('home.html', datetoday2=datetoday2, tasklist=get_task_list(), l=len(tasklist), mess='Invalid Index...')
    except Exception as e:
        app.logger.error(f"Error removing task: {e}")
        db.session.rollback()
        return render_template('500.html'), 500

# Error handling for 404 - Page Not Found
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Error handling for 500 - Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Server Error: {e}")
    return render_template('500.html'), 500

# Main function to run the Flask app
if __name__ == '__main__':
    create_tables()  # Ensure database and tables are created before running the app
    app.run()
