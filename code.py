from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from functools import wraps
global current_user
current_user = None
from flask_mail import Mail,Message
from random import randint
app = Flask(__name__)
mail=Mail(app)


import secrets

# Generate a secure random key
app.secret_key = secrets.token_hex(16)

# MySQL Database Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mad!mysql2004",
    database="test1"
)

c = mydb.cursor()

def get_faculty_details(faculty_id, session=None, year=None):
    lst = [[None, 0, 0, 0]]

    # [name, theory_courses_n, practical_courses_n, projects_n]
    q1 = f"SELECT f_name FROM Users WHERE faculty_id = '{faculty_id}'"
    c.execute(q1)
    name = c.fetchone()

    if name is None:
        return None

    lst[0][0] = name[0]

    if session == "All sessions":
        # Query for theory courses
        q2 = f"SELECT t.course_code, tc.course_name, t.handled_duration, t.hours_per_week, u.Designation FROM theory t JOIN theorycourse tc ON t.course_code = tc.course_code JOIN users u ON u.faculty_id = t.faculty_id WHERE t.faculty_id = '{faculty_id}'"
        c.execute(q2)
        theory_courses = c.fetchall()
        lst[0][1] = sum([course[3] for course in theory_courses])
        lst.append(theory_courses)

        # Query for practical courses
        q3 = f"SELECT p.course_code, pc.course_name, p.handled_duration, pc.hours, u.Designation FROM practical p JOIN practicalcourse pc ON p.course_code = pc.course_code JOIN users u ON u.faculty_id = p.faculty_id WHERE p.faculty_id = '{faculty_id}'"
        c.execute(q3)
        practical_courses = c.fetchall()
        lst[0][2] = sum([course[3] for course in practical_courses])
        lst.append(practical_courses)

        # Query for projects
        q4 = f"SELECT * FROM project WHERE faculty_id = '{faculty_id}'"
        c.execute(q4)
        projects = c.fetchall()
        lst[0][3] = len(projects)*3
        lst.append(projects)

        return lst

    elif year is not None and session is None:
        years = year.split('-')
        # Query for theory courses
        q2 = f"SELECT u.f_name, t.course_code, tc.course_name, t.hours_per_week, u.Designation FROM theory t JOIN theorycourse tc ON t.course_code = tc.course_code JOIN users u ON u.faculty_id = t.faculty_id WHERE t.handled_duration = 'March-Apr {years[1]}' AND t.faculty_id = '{faculty_id}'"
        c.execute(q2)
        theory_courses = c.fetchall()
        q2 = f"SELECT u.f_name, t.course_code, tc.course_name, t.hours_per_week, u.Designation FROM theory t JOIN theorycourse tc ON t.course_code = tc.course_code JOIN users u ON u.faculty_id = t.faculty_id WHERE t.handled_duration = 'Nov-Dec {years[0]}' AND t.faculty_id = '{faculty_id}'"
        c.execute(q2)
        theory_courses.extend(c.fetchall())
        lst[0][1] = sum([course[3] for course in theory_courses if course is not None])
        lst.append(theory_courses)

        # Query for practical courses
        q3 = f"SELECT u.f_name, p.course_code, pc.course_name, pc.hours, u.Designation FROM practical p JOIN practicalcourse pc ON p.course_code = pc.course_code JOIN users u ON u.faculty_id = p.faculty_id WHERE p.handled_duration = 'March-Apr {years[1]}' AND p.faculty_id = '{faculty_id}'"
        c.execute(q3)
        practical_courses = c.fetchall()
        q3 = f"SELECT u.f_name, p.course_code, pc.course_name, pc.hours, u.Designation FROM practical p JOIN practicalcourse pc ON p.course_code = pc.course_code JOIN users u ON u.faculty_id = p.faculty_id WHERE p.handled_duration = 'Nov-Dec {years[0]}' AND p.faculty_id = '{faculty_id}'"
        c.execute(q3)
        practical_courses.extend(c.fetchall())
        lst[0][2] = sum([course[3] for course in practical_courses if course is not None])
        lst.append(practical_courses)

        # Query for projects
        q4 = f"SELECT u.f_name, p.course_code, p.project_name, u.Designation FROM project p JOIN users u ON u.faculty_id = p.faculty_id WHERE handled_duration = 'March-Apr {years[1]}' AND p.faculty_id = '{faculty_id}'"
        c.execute(q4)
        projects = c.fetchall()
        q4 = f"SELECT u.f_name, p.course_code, p.project_name, u.Designation FROM project p JOIN users u ON u.faculty_id = p.faculty_id WHERE handled_duration = 'Nov-Dec {years[0]}' AND p.faculty_id = '{faculty_id}'"
        c.execute(q4)
        projects.extend(c.fetchall())
        lst[0][3] = len(projects)*3
        lst.append(projects)

        return lst
    
    elif session is not None and year is not None:
        # Query for theory courses
        q2 = f"SELECT u.f_name, t.course_code, tc.course_name, t.hours_per_week, u.Designation FROM theory t JOIN theorycourse tc ON t.course_code = tc.course_code JOIN users u ON u.faculty_id = t.faculty_id WHERE t.handled_duration = '{str(session) + ' ' + str(year)}' AND t.faculty_id = '{faculty_id}'"
        c.execute(q2)
        theory_courses = c.fetchall()
        lst[0][1] = sum([course[3] for course in theory_courses])
        lst.append(theory_courses)

        # Query for practical courses
        q3 = f"SELECT u.f_name, p.course_code, pc.course_name, pc.hours, u.Designation FROM practical p JOIN practicalcourse pc ON p.course_code = pc.course_code JOIN users u ON u.faculty_id = p.faculty_id WHERE p.handled_duration = '{str(session) + ' ' + str(year)}' AND p.faculty_id = '{faculty_id}'"
        c.execute(q3)
        practical_courses = c.fetchall()
        lst[0][2] = sum([course[3] for course in practical_courses])
        lst.append(practical_courses)

        # Query for projects
        q4 = f"SELECT u.f_name, p.course_code, p.project_name, u.Designation FROM project p JOIN users u ON u.faculty_id = p.faculty_id WHERE handled_duration = '{str(session) + ' ' + str(year)}' AND p.faculty_id = '{faculty_id}'"
        c.execute(q4)
        projects = c.fetchall()
        lst[0][3] = len(projects)*3
        lst.append(projects)

        return lst

    else:
        return None 
    
# Uncomment the following lines if you want to run this part separately
#print(get_faculty_details(faculty_id='sivamuruganv@ssn.edu.in', year='2023'))

def get_student_to_faculty_ratio():
    import math 
    # Query to get the total number of students
    c.execute("SELECT SUM(strength) AS total_students FROM DepartmentClasses")
    total_students = c.fetchone()[0]

    # Query to get the total number of faculty
    c.execute("SELECT COUNT(*) AS total_faculty FROM Users WHERE role_in_dept = 'faculty' or role_in_dept = 'hod' and status = 'Active'")
    total_faculty = c.fetchone()[0]
    if total_students == None:
        return "N/A" 
    if total_faculty == None:
        return "N/A"  # To handle division by zero error

    # Calculate the student-to-faculty ratio
    ratio = math.ceil(total_students / total_faculty)
    return f'1 : {str(ratio)}'

def faculty_already_handles_course(faculty_id, course_code, session):
    
    c.execute("SELECT * FROM Theory WHERE faculty_id = %s AND course_code = %s AND handled_duration = %s", (faculty_id, course_code, session))
    theory_result = c.fetchone()


    c.execute("SELECT * FROM Practical WHERE faculty_id = %s AND course_code = %s AND handled_duration = %s", (faculty_id, course_code, session))
    practical_result = c.fetchone()


    c.execute("SELECT * FROM Project WHERE faculty_id = %s AND course_code = %s AND handled_duration = %s", (faculty_id, course_code, session))
    project_result = c.fetchone()

    if theory_result or practical_result or project_result:
        return True
    else:
        return False


def login(username, password):
    global current_user
    info = []
    c.execute("SELECT faculty_id, f_name, entity, role_in_dept FROM Users WHERE faculty_id = '{}' and password = '{}'".format(username, password))
    info.extend(c.fetchall())
    if info:
        current_user = [info[0][0], info[0][2], info[0][3]]
    return info

'''print(login('sivamuruganv@ssn.edu.in', 'Welcome123'))
print(current_user)'''

def get_theory_courses():
    c.execute("SELECT course_code, course_name FROM theorycourse")
    return c.fetchall()

def get_practical_courses():
    c.execute("SELECT course_code, course_name FROM practicalcourse")
    return c.fetchall()

def get_combined_courses():
    c.execute("SELECT course_code, course_name FROM theorycourse UNION SELECT course_code, course_name FROM practicalcourse")
    return c.fetchall()

def get_classes():
    classes = []
    c.execute("SELECT section,  batch, strength FROM departmentclasses order by batch,section asc")
    classes.extend(c.fetchall())
    return classes

def check_faculty(id, relation):
    temp = []
    if relation == 1:
        c.execute("SELECT Faculty_id from users")
    elif relation == 2:
        c.execute("SELECT Faculty_id from dept_duty")
    for i in c.fetchall():
        temp.append(i[0])
    if id in temp:
        return True
    return False

def course_exists(course_code, course_type):
    if course_type == 'theory':
        c.execute("SELECT course_code FROM theorycourse WHERE course_code = %s", (course_code,))
    elif course_type == 'practical':
        c.execute("SELECT course_code FROM practicalcourse WHERE course_code = %s", (course_code,))
    else:
        c.execute("SELECT course_code FROM theorycourse WHERE course_code = %s UNION SELECT course_code FROM practicalcourse WHERE course_code = %s" , (course_code, course_code))
    return c.fetchone() is not None

def add_theorycourse(faculty_id, course_code, session, hours_per_week):
    C = []
    c.execute("SELECT course_code from theorycourse")
    for i in c.fetchall():
        C.append(i[0])
    if course_code in C and check_faculty(faculty_id, 1):
        c.execute("INSERT INTO theory values ('{}','{}','{}', '{}')".format(faculty_id, course_code, session, hours_per_week))
        mydb.commit()

def add_practicalcourse(faculty_id, course_code, session):
    C = []
    c.execute("SELECT course_code from practicalcourse")
    for i in c.fetchall():
        C.append(i[0])
    if course_code in C and check_faculty(faculty_id, 1):
        c.execute("INSERT INTO Practical values ('{}','{}','{}')".format(faculty_id, course_code, session))
        mydb.commit()


def get_faculty_name(faculty_id):
    c.execute("SELECT f_name from users WHERE faculty_id = %s", (faculty_id,))
    return c.fetchall()[0][0]

def get_session_data(faculty_id):
    session_data = {}

    # Execute SQL query to fetch theory count for each session
    c.execute("SELECT handled_duration AS session, SUM(hours_per_week) AS theory_count FROM theory t WHERE t.faculty_id = '{}' GROUP BY session".format(faculty_id))
    theory_data = c.fetchall()

    # Populate session data dictionary with theory counts
    for session, theory_count in theory_data:
        session_data.setdefault(session, {'theory': 0, 'practical': 0, 'projects': 0})
        session_data[session]['theory'] = theory_count

    # Execute SQL query to fetch practical count for each session
    c.execute("SELECT handled_duration AS session, SUM(pc.hours) AS practical_count FROM practical p JOIN practicalcourse pc ON pc.course_code = p.course_code WHERE p.faculty_id = '{}' GROUP BY session".format(faculty_id))
    practical_data = c.fetchall()

    # Populate session data dictionary with practical counts
    for session, practical_count in practical_data:
        session_data.setdefault(session, {'theory': 0, 'practical': 0, 'projects': 0})
        session_data[session]['practical'] = practical_count

    # Execute SQL query to fetch project count for each session
    c.execute("SELECT handled_duration AS session, COUNT(*) AS project_count FROM project pr WHERE pr.faculty_id = '{}' GROUP BY session".format(faculty_id))
    project_data = c.fetchall()

    # Populate session data dictionary with project counts
    for session, project_count in project_data:
        session_data.setdefault(session, {'theory': 0, 'practical': 0, 'projects': 0})
        session_data[session]['projects'] = project_count*3

    # Sort session data by month and year
    def sort_key(session):
        months_order = {'Nov-Dec': 1, 'March-Apr': 2}
        month, year = session.split()  # Split session string into month and year
        return months_order[month], int(year)

    sorted_session_data = dict(sorted(session_data.items(), key=lambda x: sort_key(x[0])))

    return sorted_session_data

def get_all_duties():
    c.execute("SELECT * FROM duty")
    lst = c.fetchall()
    return lst

def sort_year(*args):
    l=[]
    result=[]
    dummy={}
    c=0
    d={0:"March-Apr",1:"Nov-Dec"}
    for i in args:
        l.append(i.split()[1])
        dummy[i.split()[1]]=i.split()[0]
    l.sort()
    l2=list(set(l))
    l2.sort()
    for j in l2:
        if l.count(j)==2:
            result.append(d[0]+" "+j)
            result.append(d[1]+" "+j)
        else:
            result.append(dummy[j]+" "+j)
    return result

def get_faculty_id(faculty_name):
    c.execute("SELECT faculty_id FROM users WHERE f_name = '{}'".format(faculty_name))
    id = c.fetchone()
    if id:
        print(id[0])
        return id[0]
    else:
        return None

def get_faculty_name(faculty_id):
    c.execute("SELECT f_name FROM users WHERE faculty_id = '{}'".format(faculty_id))
    name = c.fetchone()[0]
    if c:
        return name
    else:
        return None

def get_all_sessions():

    c.execute("SELECT DISTINCT handled_duration FROM (SELECT handled_duration FROM theory UNION SELECT handled_duration FROM practical UNION SELECT handled_duration FROM project) AS handled_duration;")
    lst = []
    for i in c.fetchall():
        lst.extend(i)
    return lst

def get_all_faculties():
    c.execute("SELECT DISTINCT f_name, f.faculty_id FROM (SELECT faculty_id FROM theory UNION SELECT faculty_id FROM practical UNION SELECT faculty_id FROM project) AS f JOIN users u ON f.faculty_id = u.faculty_id ORDER BY f_name ASC;")
    lst = []
    for i in c.fetchall():
        lst.append(i)
    return lst

def get_faculty_designation(faculty_id):
    designation = None
    c.execute(f"SELECT Designation FROM users WHERE faculty_id = '{faculty_id}'")
    designation = c.fetchone()
    if designation:
        return designation[0]
    return None

def get_all_academic_portfolios(faculty_id = None):
    sessions = get_all_sessions()
    sorted_sessions = sort_year(*sessions)


    faculties = get_all_faculties()

    portfolios = {}

    for faculty in faculties:
        designation = get_faculty_designation(faculty[1])
        portfolios[(faculty[0],designation)] = {}

    for session in sorted_sessions:
        for faculty in faculties:
            designation = get_faculty_designation(faculty[1])
            c.execute("SELECT SUM(hours_per_week) FROM theory WHERE faculty_id = '{}' AND handled_duration = '{}'".format(faculty[1], session))
            t_count = c.fetchall()[0]
            if t_count[0] == None:
                t_count = (0,)
            c.execute("SELECT SUM(hours) FROM practical p JOIN practicalcourse pc on pc.course_code = p.course_code WHERE faculty_id = '{}' AND handled_duration = '{}'".format(faculty[1], session))
            pr_count = c.fetchall()[0]
            if pr_count[0] == None:
                pr_count = (0,)
            c.execute("SELECT COUNT(course_code) FROM project WHERE faculty_id = '{}' AND handled_duration = '{}'".format(faculty[1], session))
            p_count = c.fetchall()[0]
            if p_count[0] == None:
                p_count = (0,)

            portfolios[(faculty[0], designation)][session] = [t_count[0], pr_count[0], p_count[0]*3, t_count[0] + pr_count[0] + p_count[0]*3]
            
    if faculty_id:
        name = get_faculty_name(faculty_id)
        designation = get_faculty_designation(faculty_id)

        if name:
            return portfolios[(name, designation)]
        else:
            return None
    return portfolios

def add_project(faculty_id, course_code, name, session):
    C = []
    c.execute("SELECT course_code from practicalcourse UNION SELECT course_code from theorycourse")
    for i in c.fetchall():
        C.append(i[0])
    if course_code in C and check_faculty(faculty_id, 1):
        temp = []
        c.execute("SELECT Project_name from project")
        for j in c.fetchall():
            temp.append(j[0])
        if name not in temp:
            c.execute("INSERT into Project VALUES ('{}','{}','{}','{}')".format(faculty_id, course_code, name, session))
            mydb.commit()
        else:
            raise ValueError

def assign_dept_duty(id, responsibility):
    if check_faculty(id, 1):
        c.execute("SELECT * FROM duty")
        lst = c.fetchall()
        if responsibility not in lst:
            c.execute("INSERT INTO duty VALUES ('{}')".format(responsibility))
            mydb.commit()
        c.execute("INSERT INTO dept_duty VALUES ('{}','{}')".format(id, responsibility))
        mydb.commit()
        return True
    else:
        return None

def add_new_theory(code, name):
    c.execute("INSERT INTO theorycourse values ('{}','{}')".format(code, name))
    mydb.commit()

def add_new_practical(code, name, hours):
    c.execute("INSERT INTO practicalcourse values ('{}','{}','{}')".format(code, name, hours))
    mydb.commit()

def add_class(sec, batch, strength):
    temp = []
    c.execute("SELECT section|'_'|batch from departmentclasses")
    for i in c.fetchall():
        temp.append(i[0])
    if str(sec) + '_' + str(batch) not in temp:
        c.execute("INSERT INTO departmentclasses values ('{}',{},{})".format(sec, batch, strength))
        mydb.commit()

def get_all_faculties__names():
    c.execute("SELECT f_name FROM users WHERE Status = 'Active'")
    lst = []
    for i in c.fetchall():
        lst.append(i)
    return lst

def get_all_faculties__names_everyone():
    c.execute("SELECT f_name FROM users")
    lst = []
    for i in c.fetchall():
        lst.append(i)
    return lst
def get_all_duty_faculties():
    c.execute("SELECT DISTINCT u.f_name FROM dept_duty d JOIN users u on d.faculty_id=u.faculty_id where u.faculty_id in (SELECT DISTINCT faculty_id FROM dept_duty )")
    lst = []
    for i in c.fetchall():
        lst.append(i)
    return lst

def get_dept_role():
    c.execute("SELECT DISTINCT Responsibilities from dept_duty")
    lst=[]
    for i in c.fetchall():
        lst.append(i)
    return lst

def remove_classes(sec, batch):
    c.execute("SELECT * FROM departmentclasses where section = %s AND batch = %s", (sec, batch))
    if c.fetchone():
        c.execute("DELETE FROM departmentclasses WHERE section = %s AND batch = %s", (sec, batch))
        mydb.commit()
        return 1
    else:
        return None
    
def remove_courses_data(faculty_id):
    pass
    
def remove_from_duty(faculty_id,responsibility):
    c.execute("DELETE FROM Dept_duty WHERE faculty_id='{}' AND Responsibilities='{}'".format(faculty_id,responsibility))
    if c.rowcount>0:
        mydb.commit()
        return True
    return False

def show_roles():
    
    c.execute('SELECT u.f_name, d.Responsibilities FROM users u JOIN dept_duty d ON d.faculty_id = u.faculty_id;')
    result = c.fetchall()
    if result:
        return result

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user is None:
            return redirect(url_for('login_page'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/', methods=['GET', 'POST'])
def login_page():
    global current_user
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Call your login function with the provided parameters
        login_result = login(username, password)

        if current_user and login_result: 
            return redirect(url_for('homepage'))
        else:
            error_message = "Invalid credentials. Please try again."
            return render_template('login.html', error_message=error_message)
    return render_template('login.html')

@app.route('/homepage', methods=['GET'])
@login_required
def homepage():
    global current_user
    if current_user[1] == "admin":
        return render_template('homepage.html', admin_logged = True)
    elif current_user:
        return render_template('homepage.html', admin_logged = None)
    else:
        return render_template('homepage.html')

@app.route('/logout', methods=['POST'])
def logout():
    global current_user
    data = request.json
    choice = data.get('choice')
    if choice == 'yes':
        current_user = None
        return redirect(url_for('login_page'))
    else:
        # Return a failure response if choice is not 'yes'
        return jsonify({'error': 'Invalid choice'}), 400

@app.route('/view_classes')
@login_required
def view_classes():
    if current_user[1] == "admin":
        classes = get_classes() 
        return render_template('view_classes.html', classes=classes)
    else:
        return render_template('unauthorized.html')

@app.route('/academic_portfolio', methods=['GET', 'POST'])
@login_required
def academic_portfolio():
    global current_user
    global faculty
    global year_to_search
    global session_to_search
    if current_user and current_user[1] == 'user':

        faculty = current_user[0]
        # Get form data from the request using request.args
        session_to_search = request.args.get('session')
        year_to_search = request.args.get('year')
        session_to_search = session_to_search if session_to_search != '--' else None
        year_to_search = year_to_search if year_to_search != '' else None

        if year_to_search and session_to_search and session_to_search != 'All sessions':
            session = session_to_search + ' ' + year_to_search
        elif session_to_search == 'All sessions':
            session = 'All Sessions'
        elif year_to_search is None and session_to_search:
            session = session_to_search
        else:
            session = year_to_search

        # Call your get_faculty_details function with the provided parameters
        faculty_details = get_faculty_details(faculty_id=faculty, session=session_to_search, year=year_to_search)

        return render_template('faculty_details.html', faculty_details=faculty_details, session= session)
    
    elif current_user and current_user[1] == 'admin':
        
        faculty_name = request.args.get('faculty')
        faculty = get_faculty_id(faculty_name)
        # Get form data from the request using request.args
        session_to_search = request.args.get('session')
        year_to_search = request.args.get('year')
        session_to_search = session_to_search if session_to_search != '--' else None
        year_to_search = year_to_search if year_to_search != '' else None
        if year_to_search and session_to_search:
            if session_to_search == 'March-Apr':
                session = 'Mar-Apr' + ' ' + year_to_search
            else:
                session = session_to_search + ' ' + year_to_search
        elif year_to_search is None and session_to_search:
            session = session_to_search
        else:
            session = year_to_search
        session_data = get_session_data(faculty)
        session_labels = list(session_data.keys())
        
        # Prepare data for theory, practical, and projects separately
        theory_counts = [session_data[session]['theory'] for session in session_labels]
        practical_counts = [session_data[session]['practical'] for session in session_labels]
        project_counts = [session_data[session]['projects'] for session in session_labels]
        total_count = [theory_counts[i] + practical_counts[i] + project_counts[i] for i in range(len(session_labels))]

        #Get faculty name
        f_name = get_faculty_name(faculty)

        # Call your get_faculty_details function with the provided parameters
        faculty_details = get_faculty_details(faculty_id=faculty, session=session_to_search, year=year_to_search)

        return render_template('faculty_details_hod.html', faculty_details=faculty_details, session= session, session_labels=session_labels, 
                               theory_counts=theory_counts, 
                               practical_counts=practical_counts, 
                               total_count=total_count,
                               project_counts=project_counts, 
                               faculty= f_name)

    else:
        return redirect(url_for('index'))

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if current_user[1] == 'user':
        return render_template('index1.html')
    else:
        faculties = get_all_faculties__names()
        return render_template('index2.html',  faculties= faculties)


@app.route('/add_courses', methods=['GET', 'POST'])
@login_required
def add_courses():
    if current_user and current_user[1] == 'admin':
        if request.method == 'POST':
            
            m = request.form['session']
            y = request.form['year']
            month = m
            year = y
            session = month + ' ' + year
            course_type = request.form.get('course_type')
            course_code = request.form['course_code']
            project_name = request.form['project_name']
            hours_per_week = request.form['hours_per_week']
            faculty_id = faculty

            # Check if all fields are entered
            if not (session and year and course_code and course_type):
                flash('Please fill in all fields', 'error')
                return redirect(url_for('add_courses'))

            # Check if the course code exists
            if not course_exists(course_code, course_type):
                flash('Course does not exist. Please enter a valid course code.', 'error')
                return redirect(url_for('add_courses'))

            # Check if the faculty already handles the subject in this session
            if course_type == 'theory':
                if faculty_already_handles_course(faculty, course_code, session):
                    flash('The faculty already handles this theory course in the specified session.', 'error')
                    return redirect(url_for('add_courses'))
                else:
                    add_theorycourse(faculty, course_code, session, hours_per_week)
            elif course_type == 'practical':
                if faculty_already_handles_course(faculty, course_code, session):
                    flash('The faculty already handles this practical course in the specified session.', 'error')
                    return redirect(url_for('add_courses'))
                else:
                    add_practicalcourse(faculty, course_code, session)
            elif course_type == 'project':
                if faculty_already_handles_course(faculty, course_code, session):
                    flash('The faculty already handles a project for this course in the specified session.', 'error')
                    return redirect(url_for('add_courses'))
                else:
                    add_project(faculty, course_code, project_name, session)
            
            f_name = get_faculty_name(faculty)
            flash(f'Course added to {f_name} portfolio successfully!', 'success')
            return redirect(url_for('add_courses'))

        else:
            # Fetch data for rendering the template
            session_data = get_session_data(faculty)
            session_labels = list(session_data.keys())
            
            # Prepare data for theory, practical, and projects separately
            theory_counts = [session_data[session]['theory'] for session in session_labels]
            practical_counts = [session_data[session]['practical'] for session in session_labels]
            project_counts = [session_data[session]['projects'] for session in session_labels]
            total_count = [theory_counts[i] + practical_counts[i] + project_counts[i] for i in range(len(session_labels))]

            # Fetch the course lists
            theory_courses = get_theory_courses()
            practical_courses = get_practical_courses()
            combined_courses = get_combined_courses()

            # Convert course lists to dictionaries
            theory_courses_dict = [{'code': code, 'name': name} for code, name in theory_courses]
            theory_courses_dict = sorted(theory_courses_dict, key=lambda x: x['name'])
            practical_courses_dict = [{'code': code, 'name': name} for code, name in practical_courses]
            practical_courses_dict = sorted(practical_courses_dict, key=lambda x: x['name'])
            combined_courses_dict = [{'code': code, 'name': name} for code, name in combined_courses]
            combined_courses_dict = sorted(combined_courses_dict, key=lambda x: x['name'])
        
            # Fetch student to faculty ratio
            ratio = get_student_to_faculty_ratio()

            #Get faculty name
            f_name = get_faculty_name(faculty)

            return render_template('add_courses.html', 
                                session_labels=session_labels, 
                                theory_counts=theory_counts, 
                                practical_counts=practical_counts, 
                                total_count=total_count,
                                project_counts=project_counts, 
                                theory_courses=theory_courses_dict, 
                                practical_courses=practical_courses_dict, 
                                combined_courses=combined_courses_dict,
                                student_to_faculty_ratio=ratio, 
                                faculty= f_name)
    else:
        return render_template('unauthorized.html')

@app.route('/add_new_course', methods=['GET', 'POST'])
@login_required
def add_new_course():
    if current_user and current_user[1] == 'admin':
        if request.method == "POST":
            course_type = request.form.get('course_type')
            course_code = request.form['course_code']
            course_name = request.form['course_name']
            hours_per_week = request.form['hours_per_week']
            if course_type == "theory" and (course_exists(course_code, "theory") != None):
                add_new_theory(course_code, course_name)
            elif course_type == "practical" and (course_exists(course_code, "practical") != None):
                add_new_practical(course_code, course_name, hours_per_week)
            else:
                flash('Course already exists!')
            flash(f'Course added successfully!', 'success')
        return render_template('add_new_course.html')
    else:
        return render_template('unauthorized.html')
    

from mysql.connector import IntegrityError

@app.route('/add_new_class', methods=['POST'])
@login_required
def add_new_class():
    if current_user and current_user[1] == "admin":
        if request.method == 'POST':
            data = request.json  # Get JSON data from the request
            section = data.get('section')
            batch = data.get('batch')
            strength = data.get('strength')

            try:
                # Add the new class to the database
                add_class(section, batch, strength)

                # Flash a message indicating success
                flash('Class added successfully', 'success')

                # Return a success response
                return jsonify({'message': 'Class added successfully'}), 200

            except IntegrityError:
                # Flash a message indicating failure due to existing class
                flash('Class already exists', 'error')

                # Return a failure response
                return jsonify({'message': 'Class already exists'}), 200
        else:
            # Return a method not allowed response for non-POST requests
            return jsonify({'error': 'Method not allowed'}), 405
    else:
        return render_template('unauthorized.html')



@app.route('/remove_class', methods=['POST'])
@login_required
def remove_class():
    if current_user and current_user[1] == "admin":
        if request.method == 'POST':
            # Get the JSON data
            data = request.json
            section = data.get('section')
            batch = data.get('batch')

            # Call the remove_class function to remove the class from the database
            removed = remove_classes(section, batch)
            if removed:
                flash('Class removed successfully', 'success')  # Add this flash message
                return jsonify({'message': 'Class removed successfully'}), 200
            else:
                flash('Class does not exist', 'failure')  # Add this flash message
                return jsonify({'message': 'Class does not exist'}), 200
        else:
            return jsonify({'error': 'Method not allowed'}), 405
    else:
        return render_template('unauthorized.html')

@app.route('/edit_faculty_details', methods=['GET', 'POST'])
@login_required
def edit_faculty_details():
    if current_user and current_user[1] == "admin":
        if request.method == 'POST':
            temp = request.form.get('faculty')
            faculty=get_faculty_id(temp)
            entity = request.form.get('entity')
            designation = request.form.get('designation')
            status = request.form.get('status')

            # Ensure you are using prepared statements to prevent SQL injection
            # Here's a simple example without prepared statements for demonstration
            c.execute("UPDATE USERS SET entity='{}', Status='{}', Designation='{}' WHERE faculty_id='{}'".format(entity, status, designation,faculty))
            mydb.commit()
            flash('Changes have been made.','success')
            return redirect(url_for('edit_faculty_details'))

        # Handle the GET request if needed
        elif request.method=='GET':
            faculties=get_all_faculties__names_everyone()
            return render_template('edit_faculty_details.html',faculties=faculties)
    else:
        return render_template('unauthorized.html')
    
@app.route('/detailed_portfolio', methods=['GET', 'POST'])
@login_required
def detailed_portfolio():
    if current_user[1] == 'admin':
    
        if request.method == 'POST':
            faculty_name = request.form['faculty_name']
            faculty_id = get_faculty_id(faculty_name)
            return render_template('index3.html', faculty_name=faculty_name, faculty_id=faculty_id)
    else:
        return render_template('unauthorized.html')

@app.route('/detailed_portfolio2', methods=['GET', 'POST'])
@login_required
def detailed_portfolio2():
    if current_user and current_user[1] == "admin":
        global faculty
        faculty = request.args.get('faculty_id')
        print(faculty)
        # Get form data from the request using request.args
        session_to_search = request.args.get('session')
        
        year_to_search = request.args.get('year')
        session_to_search = session_to_search if session_to_search != '--' else None
        year_to_search = year_to_search if year_to_search != '' else None
        if year_to_search and session_to_search:
            session = session_to_search + ' ' + year_to_search
        elif year_to_search is None and session_to_search:
            session = session_to_search
        else:
            session = year_to_search 
        session_data = get_session_data(faculty)
        session_labels = list(session_data.keys())
            
        # Prepare data for theory, practical, and projects separately
        theory_counts = [session_data[session]['theory'] for session in session_labels]
        practical_counts = [session_data[session]['practical'] for session in session_labels]
        project_counts = [session_data[session]['projects'] for session in session_labels]
        total_count = [theory_counts[i] + practical_counts[i] + project_counts[i] for i in range(len(session_labels))]
        #Get faculty name
        f_name = get_faculty_name(faculty)
        # Call your get_faculty_details function with the provided parameters
        faculty_details = get_faculty_details(faculty_id=faculty, session=session_to_search, year=year_to_search)
        return render_template('faculty_details_hod.html', faculty_details=faculty_details, session= session, session_labels=session_labels, 
                                theory_counts=theory_counts, 
                                practical_counts=practical_counts, 
                                total_count=total_count,
                                project_counts=project_counts, 
                                faculty= f_name)
    else:
        return render_template('unauthorized.html')


@app.route('/remove_courses', methods=['GET', 'POST'])
@login_required
def remove_courses():
    if current_user and current_user[1] == "admin":
        
        if request.method == 'POST':
            # Get form data from the request
            course_type = request.form['course_type']
            session = request.form['session']
            course_code=request.form['course_code']
            year=request.form['year']
            handled_duration = session + ' ' + year

            if course_type=='Theory':
                c.execute("DELETE FROM Theory WHERE faculty_id='{}' and course_code='{}' and handled_duration='{}'".format(faculty,course_code,handled_duration))
                mydb.commit()
            elif course_type=='Practical':
                c.execute("DELETE FROM Practical WHERE faculty_id='{}' and course_code='{}' and handled_duration='{}'".format(faculty,course_code,handled_duration))
                mydb.commit()
            elif course_type=='Project':
                c.execute("DELETE FROM Project WHERE faculty_id='{}' and course_code='{}' and handled_duration='{}'".format(faculty,course_code,handled_duration))
                mydb.commit()
            flash('Removed successfully.', 'success')
            return redirect(url_for('remove_courses'))
        
        elif request.method == 'GET':
            c.execute("SELECT t.course_code, tc.course_name FROM theory t JOIN theorycourse tc ON t.course_code = tc.course_code WHERE faculty_id = '{}'".format(faculty))
            theory = c.fetchall()
            theory = [{'code': course[0], 'name' : course[1]} for course in theory]
            c.execute("SELECT p.course_code, pc.course_name FROM practical p JOIN practicalcourse pc ON p.course_code = pc.course_code  WHERE faculty_id = '{}'".format(faculty))
            practical = c.fetchall()
            practical = [{'code': course[0], 'name' : course[1]} for course in practical]
            c.execute("SELECT course_code, project_name FROM project WHERE faculty_id = '{}'".format(faculty))
            project = c.fetchall()
            project = [{'code': course[0], 'name' : course[1]} for course in project]
            theory = theory if theory is not None else []
            practical = practical if practical is not None else []
            project = project if project is not None else []

            return render_template('remove_courses.html', theory=theory, practical=practical, project=project)
        return render_template('remove_courses.html')
    else:
        return render_template('unauthorized.html')


@app.route('/department_portfolio',methods=['GET', 'POST'])
@login_required
def department_portfolio():
    global current_user
    global faculty
    if request.method == 'GET':
        if current_user[2].upper()=='HOD':
            roles = show_roles()
            if roles:
                return render_template('get_committee_details_hod.html', roles=roles)
            else:
                flash('No data exists', 'error')
                return render_template('get_committee_details_hod.html', roles=None)
        else:
            roles = show_roles()
            if roles:
                return render_template('get_committee_details.html', roles=roles)
            else:
                flash('No data exists', 'error')
                return render_template('get_committee_details.html', roles=None)
        
@app.route('/academic_portfolios', methods=['GET', 'POST'])
@login_required
def academic_portfolios():
    if current_user and current_user[1] == "admin":
        if request.method == 'GET':
            # Fetch all academic portfolios
            academic_portfolios_data = get_all_academic_portfolios()

            faculties= get_all_faculties()
            sessions = sort_year(*get_all_sessions())
            faculties = list(academic_portfolios_data.keys())
            sessions = list(academic_portfolios_data[faculties[0]].keys()) if faculties else []
            
            return render_template('academic_portfolios.html', portfolios=academic_portfolios_data, sessions=sessions, session_count = len(sessions)*4)

        elif request.method == 'POST':
            # Get the faculty name from the search form
            faculty_name = request.form['faculty_name']
            
            # Get the faculty ID using the faculty name
            faculty_id = get_faculty_id(faculty_name)
            faculty_designation = get_faculty_designation(faculty_id)
            
            if faculty_id:
                # Fetch academic portfolio for the specified faculty
                academic_portfolio_data = get_all_academic_portfolios(faculty_id)

                
                if academic_portfolio_data:
                    # Sort sessions
                    sessions = sort_year(*list(academic_portfolio_data.keys()))
                    print(sessions)
                    return render_template('academic_portfolios.html', portfolios={(faculty_name, faculty_designation): academic_portfolio_data}, sessions=sessions, session_count=len(sessions)*4)
                else:
                    flash('No academic portfolio found for the specified faculty.', 'error')
                    return redirect(url_for('academic_portfolios'))
            else:
                flash('No faculty found with the provided name.', 'error')
                return redirect(url_for('academic_portfolios'))
    else:
        return render_template('unauthorized.html')



@app.route('/add_duty', methods=['POST', 'GET'])
def add_duty():
    if current_user and current_user[1] == "admin":
        if request.method == 'POST':
            faculty = request.form['faculty']
            faculty_id = get_faculty_id(faculty)
            Responsibility= request.form['Responsibility']
            temp = assign_dept_duty(faculty_id, Responsibility)
            print(temp)
            if temp != None:
                flash('Duty has been added', 'success')
            else:
                flash('Failed to add duty', 'error')
            return redirect(url_for('department_portfolio'))
        else:
            faculties = get_all_faculties__names()
            duties = get_all_duties()
            print(duties)
            return render_template('add_duty.html', faculties=faculties, duties= duties)
    else:
        return render_template('unauthorized.html')

@app.route('/remove_duty', methods=['POST', 'GET'])
def remove_duty():
    if current_user and current_user[1] == "admin":
        if request.method == 'POST':
            faculty = request.form.get('faculty')
            if faculty is None:
                flash('Faculty not selected.', 'error')
                return redirect(url_for('remove_duty'))

            faculty_id = get_faculty_id(faculty)
            responsibility = request.form.get('role')  # Use request.form.get()
            if remove_from_duty(faculty_id, responsibility):
                flash('Removed successfully', 'success')  # Use 'success' for the success message
                return redirect(url_for('department_portfolio'))
            else:
                flash('Invalid entries.', 'error')
                return redirect(url_for('department_portfolio'))
        else:
            faculties = get_all_duty_faculties()
            roles = get_dept_role()
            return render_template('remove_duty.html', faculties=faculties, roles=roles)
    else:
        return render_template('unauthorized.html')

@app.route('/remove_all_duty', methods=['POST', 'GET'])
def remove_all_duty():
    if current_user and current_user[1] == "admin":
        if request.method == 'POST':
            c.execute("DELETE FROM Dept_duty")
            mydb.commit()
            return redirect(url_for('department_portfolio'))
        else:
            # Handle GET request
            return redirect(url_for('department_portfolio'))
    else:
        return render_template('unauthorized.html')

    
#Email Varification Using OTP in Flask

app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"]=465
app.config["MAIL_USERNAME"]='mathesh2210645@ssn.edu.in'  # sender mail
app.config['MAIL_PASSWORD']='Ssnpassword2004'                   #you have to give your password of gmail account
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail=Mail(app)
otp=randint(000000,999999)

@app.route('/registration',methods=['GET', 'POST'])
def registration():
    temp=current_user[0]
    msg=Message(subject='OTP',sender='mathesh2210645@ssn.edu.in',recipients=[temp])
    msg.body=str(otp)
    mail.send(msg)
    return render_template('verify.html')
    #return render_template("index.html")

email_id=None
"""@app.route('/verify',methods=["POST"])
def verify():
    temp=current_user[0]
    msg=Message(subject='OTP',sender='mathesh2210645@ssn.edu.in',recipients=[temp])
    msg.body=str(otp)
    mail.send(msg)
    return render_template('verify.html')"""
@app.route('/validate', methods=['POST'])
def validate():
    user_otp = request.form['otp']
    try:
        if otp == int(user_otp):
            return render_template("change_password.html")
    except ValueError:
        pass
    flash("Invalid OTP")
    return render_template("verify2.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Print form data for debugging
        print("Form data received:", request.form)

        try:
            name = request.form["faculty_name"]
            temp = request.form["faculty_ID"]
            password = request.form["password"]
            dept_role = request.form["role_in_dept"]
            designation = request.form["designation"]
            entity = request.form["entity"]

            if not temp.endswith("@ssn.edu.in"):
                flash('Invalid user', 'error')
                return redirect('/register')  # Assuming you have a register page to redirect to

            id = temp

            c.execute("SELECT faculty_id FROM users WHERE faculty_id = %s", (id,))
            result = c.fetchone()

            if result is None:
                c.execute("INSERT INTO users (faculty_id, f_name, password, entity, role_in_dept, status, designation) VALUES (%s, %s, %s, %s, %s, 'Active', %s)",
                          (id, name, password, entity, dept_role, designation))
                mydb.commit()
                flash('Registration successful', 'success')
            else:
                flash('User already exists', 'error')

            return redirect('/register')
        except KeyError as e:
            flash(f"Missing form field: {str(e)}", 'error')
            return redirect('/register')

    return render_template('user_registration.html')


@app.route('/verify',methods=["GET"])
def verify():
    temp=current_user[0]
    msg=Message(subject='OTP',sender='mathesh2210645@ssn.edu.in',recipients=[temp])
    msg.body=str(otp)
    mail.send(msg)
    return render_template("verify2.html")

@app.route('/validate2', methods=['POST'])
def validate2():
    user_otp = request.form['otp']
    # Assuming `otp` is the correct OTP for validation
    if otp == int(user_otp):
        return render_template("user_registration.html")
    flash("Invalid OTP")
    return render_template("verify.html")

    

@app.route('/password', methods=["POST", "GET"])
def change_password():
    if request.method == 'POST':
        old = request.form["old_password"]
        c.execute("SELECT password FROM users WHERE faculty_id='{}'".format(current_user[0]))
        """new_password = request.form.get("new_password")
        confirm_new_password = request.form.get("confirm_new_password")"""
        apw=c.fetchone()[0]

        if old==apw:
            cpw=request.form["confirm_new_password"]
            c.execute("UPDATE users SET password ='{}' WHERE faculty_id='{}'".format(cpw,current_user[0]))
            mydb.commit()
            return redirect(url_for('homepage'))
        return "<h3>'{}'</h3>".format(apw)
    else:
        return render_template('change_password.html')

if __name__ == '__main__':
    app.run(debug=True)