import os
from flask import Flask, request, render_template
from datetime import date

app = Flask(__name__)

# Load secret key from environment variable
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'defaultsecretkey')

# Get today's date in two different formats
datetoday = date.today().strftime("%m_%d_%y")
datetoday2 = date.today().strftime("%d-%B-%Y")

# Ensure 'tasks.txt' file exists; create if it doesn't
if 'tasks.txt' not in os.listdir('.'):
    with open('tasks.txt', 'w') as f:
        f.write('')

# Function to read task list from 'tasks.txt'
def get_task_list():
    with open('tasks.txt', 'r') as f:
        tasklist = f.readlines()
    return tasklist

# Function to create a new (empty) task list
def create_new_task_list():
    os.remove('tasks.txt')
    with open('tasks.txt', 'w') as f:
        f.write('')

# Function to update task list in 'tasks.txt'
def update_task_list(tasklist):
    os.remove('tasks.txt')
    with open('tasks.txt', 'w') as f:
        f.writelines(tasklist)

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html', datetoday2=datetoday2, tasklist=get_task_list(), l=len(get_task_list()))

# Route to clear the to-do list
@app.route('/clear')
def clear_list():
    create_new_task_list()
    return render_template('home.html', datetoday2=datetoday2, tasklist=get_task_list(), l=len(get_task_list()))

# Route to add a task to the to-do list
@app.route('/addtask', methods=['POST'])
def add_task():
    task = request.form.get('newtask')
    with open('tasks.txt', 'a') as f:
        f.writelines(task + '\n')
    return render_template('home.html', datetoday2=datetoday2, tasklist=get_task_list(), l=len(get_task_list()))

# Route to remove a task from the to-do list
@app.route('/deltask', methods=['GET'])
def remove_task():
    task_index = int(request.args.get('deltaskid'))
    tasklist = get_task_list()

    if task_index < 0 or task_index >= len(tasklist):
        return render_template('home.html', datetoday2=datetoday2, tasklist=tasklist, l=len(tasklist), mess='Invalid Index...')
    else:
        removed_task = tasklist.pop(task_index)

    update_task_list(tasklist)
    return render_template('home.html', datetoday2=datetoday2, tasklist=tasklist, l=len(tasklist))

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Main function to run the Flask app
if __name__ == '__main__':
    app.run()
