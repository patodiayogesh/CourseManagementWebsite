from datetime import timedelta
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import (g,
                   request,
                   render_template,
                   redirect,
                   Response,
                   url_for,
                   flash,
                   session,
                   )

from courseworks import app
from courseworks.forms import Create_Assignment, LoginForm, Marks_Assignment, RegisterForm, Submit_Assignment
from courseworks.queries import *
import random
import datetime

app.secret_key='key'
app.permanent_session_lifetime=timedelta(minutes=30)

@app.route('/')
def index():
    return render_template("courseworks.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form=RegisterForm()
    try:
        if request.method=="POST":
            user_id = random.randrange(1000000)
            cursor = g.conn.execute(university_details_query, form.university_id.data)
            is_uni_exists = cursor.rowcount>0
            cursor.close()
            if is_uni_exists:
                    cursor = g.conn.execute(create_admin_query,
                        user_id,
                        form.user_first_name.data,
                        form.user_last_name.data,
                        form.user_email.data,
                        form.user_password.data,
                        form.university_id.data,
                        user_id,
                        datetime.datetime.now(),
                    )
                    cursor.close()
            else:
                university_id = random.randrange(1000000)
                try:
                    cursor = g.conn.execute(create_uni_query,
                        university_id,
                        form.university_name.data,
                        form.university_city.data,
                        form.university_state.data,
                        form.university_address.data,
                        form.university_pincode.data,
                        form.university_establishment_date.data,
                    )
                    cursor.close()
                except Exception:
                    flash('Used College')
                    return redirect('/register')
                try:
                    cursor = g.conn.execute(create_admin_query,
                        user_id,
                        form.user_first_name.data,
                        form.user_last_name.data,
                        form.user_email.data,
                        form.user_password.data,
                        university_id,
                        user_id,
                        datetime.datetime.now(),
                    )
                    cursor.close()
                except Exception:
                    cursor = g.conn.execute(delete_university_query,
                        str(university_id),
                    )
                    cursor.close()
                    flash('Used email')
                    return redirect('/register')
            return redirect('/login')
        return render_template('register.html', title='Register', form=form)
    except Exception:
        flash('Something went wrong')
        return redirect('/')

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    try:
        user_details = verify_login(form)
        if user_details:
            session['user_id'] = user_details['data'].user_id
            session['user_first_name'] = user_details['data'].user_first_name
            session['university_id'] = user_details['data'].university_id
            return redirect('/home')
        else:
            pass
        return render_template('login.html', title='Login', form=form)
    except Exception:
        flash('Something went wrong')
        return redirect('/')

def verify_login(form):
    username = form.username.data
    password = form.password.data
    cursor = g.conn.execute(login_query, username, password)
    rows = cursor.rowcount
    user_info = cursor.fetchone()
    cursor.close()
    context = dict(data=user_info)
    if rows == 1:
        return context
    return False

@app.route('/logout', methods=['POST'])
def logout():
    try:
        session.clear()
        return redirect('/login')
    except Exception:
        flash('Something went wrong')
        return redirect('/')

@app.route("/home", methods=['GET'])
def home():
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            cursor = g.conn.execute(admin_details, user_id)
            admin_info = cursor.fetchall()
            cursor.close()
            cursor = g.conn.execute(prof_details, user_id)
            prof_info = cursor.fetchall()
            cursor.close()
            cursor = g.conn.execute(student_details, user_id)
            student_info = cursor.fetchall()
            cursor.close()
            session['is_admin']=len(admin_info)>0
            session['is_prof']=len(prof_info)>0
            session['is_student']=len(student_info)>0
            cursor = g.conn.execute(user_details_query,
                                    user_id,
                                )
            university_id = cursor.fetchone().university_id
            cursor.close()
            cursor = g.conn.execute(get_course_details_all, university_id)
            all_courses = cursor.fetchall()
            cursor.close()
            cursor = g.conn.execute(get_student_details_all, university_id)
            all_students = cursor.fetchall()
            cursor.close()
            cursor = g.conn.execute(get_professor_details_all, university_id)
            all_professors = cursor.fetchall()
            cursor.close()
            cursor = g.conn.execute(get_venue_details_all, university_id)
            all_venues = cursor.fetchall()
            cursor.close()
            return render_template("home.html", user_first_name=session['user_first_name'], 
                                    user_id=session['user_id'],
                                    is_admin=session['is_admin'], 
                                    is_prof=session['is_prof'], 
                                    is_student=session['is_student'],
                                    courses=all_courses,
                                    students=all_students,
                                    professors=all_professors,
                                    venues=all_venues,
                                )
        else: return redirect('/login')
    except Exception:
        flash('Something went wrong')
        return redirect('/')

@app.route('/user/', defaults={'user_id' : None})
@app.route('/user/<user_id>', methods=['GET', 'POST'])
def show_user_details(user_id):
    try:
        if 'user_id' not in session: return redirect('/login')
        viewer = session['user_id']
        cursor = g.conn.execute(user_details_query,
                                viewer,
                            )
        viewer_university_id = cursor.fetchone().university_id
        cursor.close()
        cursor = g.conn.execute(user_details_query,
                                user_id,
                            )
        user_details = cursor.fetchone()
        cursor.close() 
        if user_details.university_id != viewer_university_id:
            return redirect('/home')
        return render_template('user.html', user_info=user_details, can_update=(viewer==user_id or session['is_admin']), can_delete=(session['is_admin'] and viewer!=user_id))
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route('/update_user/', defaults={'user_id' : None})
@app.route('/update_user/<user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    try:
        if 'user_id' not in session: return redirect('/login')
        viewer = session['user_id']
        if viewer != user_id and not session['is_admin']:
            return redirect(url_for('show_user_details', user_id=user_id))
        if request.method=="POST":
            cursor = g.conn.execute(update_user_query,
                                request.form['first_name'],
                                request.form['last_name'],
                                request.form['password'],
                                user_id,
                            )
            cursor.close()
            return redirect(url_for('show_user_details', user_id=user_id))
        cursor = g.conn.execute(user_details_query,
                                user_id,
                            )
        user_info = cursor.fetchone()
        cursor.close()
        return render_template('update_user.html', user_info=user_info)
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route('/university', methods=['GET'])
def university_details():
    try:
        if 'university_id' in session:
            university_id=session['university_id']
            cursor = g.conn.execute(university_details_query, university_id)
            uni_info = cursor.fetchone()
            cursor.close()
            return render_template('university.html', uni_info=uni_info)
        else: return redirect('/login')
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/active_courses", methods=['GET'])
@app.route("/inactive_courses", methods=['GET'])
def get_courses_registered():
    try:
        if 'user_id' in session:
            if 'inactive_courses' in request.url:
                active = 'f'
            else:
                active = 't'
            user_id=session['user_id']
            cursor = g.conn.execute(registered_courses_student, user_id, active)
            course_info = cursor.fetchall()
            cursor.close()

            return render_template('courses.html',
                                active = 'Active' if active=='t' else 'Inactive',
                                course_data = course_info,
                                title='Courses')
        else: return redirect('/login')
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/active_courses_prof", methods=['GET'])
@app.route("/inactive_courses_prof", methods=['GET'])
def get_courses_prof():
    try:
        if 'user_id' in session:
            if 'inactive_courses' in request.url:
                active = 'f'
            else:
                active = 't'
            user_id=session['user_id']
            cursor = g.conn.execute(courses_prof, user_id, active)
            course_info = cursor.fetchall()
            cursor.close()

            return render_template('courses.html',
                                active = 'Active' if active=='t' else 'Inactive',
                                course_data = course_info,
                                title='Courses')
        else: return redirect('/login')
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/active_courses_ta", methods=['GET'])
@app.route("/inactive_courses_ta", methods=['GET'])
def get_courses_ta():
    try:
        if 'user_id' in session:
            if 'inactive_courses' in request.url:
                active = 'f'
            else:
                active = 't'
            user_id=session['user_id']
            cursor = g.conn.execute(courses_ta, user_id, active)
            course_info = cursor.fetchall()
            cursor.close()

            return render_template('courses.html',
                                active = 'Active' if active=='t' else 'Inactive',
                                course_data = course_info,
                                title='Courses')
        else: return redirect('/login')
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route('/create_student', methods=['GET', 'POST'])
def create_student():
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            cursor = g.conn.execute(admin_details,
                                    user_id,
                                )
            is_admin = cursor.rowcount>0
            cursor.close()
            if not is_admin:
                return redirect('/home')
            cursor = g.conn.execute(user_details_query,
                                    user_id,
                                )
            university_id = cursor.fetchone().university_id
            cursor.close()
            if request.method == "POST":
                user_id = random.randrange(1000000)
                cursor = g.conn.execute(create_student_query,
                    user_id,
                    request.form['first_name'],
                    request.form['last_name'],
                    request.form['email'],
                    request.form['password'],
                    university_id,
                    user_id,
                    request.form['department'],
                    request.form['max_credits_per_sem'],
                )
                cursor.close()
                return redirect('/home')
            return render_template('create_student.html')
        return redirect('/home') 
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route('/create_professor', methods=['GET', 'POST'])
def create_professor():
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            cursor = g.conn.execute(admin_details,
                                    user_id,
                                )
            is_admin = cursor.rowcount>0
            cursor.close()
            if not is_admin:
                return redirect('/home')
            cursor = g.conn.execute(user_details_query,
                                    user_id,
                                )
            university_id = cursor.fetchone().university_id
            cursor.close()
            if request.method == "POST":
                user_id = random.randrange(1000000)
                cursor = g.conn.execute(create_professor_query,
                    user_id,
                    request.form['first_name'],
                    request.form['last_name'],
                    request.form['email'],
                    request.form['password'],
                    university_id,
                    user_id,
                    request.form['department'],
                )
                cursor.close()
                return redirect('/home')
            return render_template('create_professor.html')
        return redirect('/home') 
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route('/create_venue', methods=['GET', 'POST'])
def create_venue():
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            cursor = g.conn.execute(admin_details,
                                    user_id,
                                )
            is_admin = cursor.rowcount>0
            cursor.close()
            if not is_admin:
                return redirect('/home')
            cursor = g.conn.execute(user_details_query,
                                    user_id,
                                )
            university_id = cursor.fetchone().university_id
            cursor.close()
            if request.method == "POST":
                venue_id = random.randrange(1000000)
                cursor = g.conn.execute(create_venue_query,
                    venue_id,
                    request.form['venue_building'],
                    request.form['venue_class_number'],
                    university_id,
                )
                cursor.close()
                return redirect('/home')
            return render_template('create_venue.html')
        return redirect('/home') 
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/course_details/", defaults={'course_id' : None})
@app.route("/course_details/<course_id>", methods=['GET'])
def course_details(course_id):
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            if course_id is None and 'course_id' in session:
                course_id = session['course_id']
            if course_id is None:
                return redirect('/home')
            session['course_id'] = course_id
            cursor = g.conn.execute(get_course_details, str(course_id))
            course_data = cursor.fetchone()
            cursor.close()
            cursor = g.conn.execute(get_venue_by_venue_id, course_data.venue_id)
            venue_data = cursor.fetchone()
            cursor.close()
            cursor = g.conn.execute(get_course_assignments, str(course_id))
            assignment_data = cursor.fetchall()
            cursor.close()
            cursor = g.conn.execute(prof_of_course,
                                    course_id,
                                    user_id,
                                )
            is_prof = cursor.rowcount>0
            cursor.close()
            cursor = g.conn.execute(admin_details,
                                    user_id,
                                )
            is_admin = cursor.rowcount>0
            cursor.close()
            cursor = g.conn.execute(prof_of_course_details,
                                    course_id,
                                )
            prof_details = cursor.fetchall()
            cursor.close()
            cursor = g.conn.execute(ta_of_course_details,
                                    course_id,
                                )
            ta_details = cursor.fetchall()
            cursor.close()
            cursor = g.conn.execute(student_of_course_details,
                                    course_id,
                                )
            stud_details = cursor.fetchall()
            cursor.close()
            return render_template('course_details.html',
                                course_data = course_data,
                                assignment_data = assignment_data,
                                title='Course Details',
                                is_prof=is_prof,
                                prof_details=prof_details,
                                ta_details=ta_details,
                                stud_details=stud_details,
                                is_admin=is_admin,
                                venue=venue_data,
                                )
        else: return redirect('/login')
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/create_course", methods=['GET', 'POST'])
def create_course():
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            cursor = g.conn.execute(admin_details,
                                    user_id,
                                )
            is_admin = cursor.rowcount>0
            cursor.close()
            if not is_admin:
                return redirect('/home')
            cursor = g.conn.execute(user_details_query,
                                    user_id,
                                )
            university_id = cursor.fetchone().university_id
            cursor.close()
            cursor = g.conn.execute(get_venue,
                                    university_id,
                                )
            venues = cursor.fetchall()
            cursor.close()
            if request.method == "POST":
                course_id = random.randrange(1000000)
                cursor = g.conn.execute(create_course_query,
                    course_id,
                    request.form['course_name'],
                    request.form['user_description'],
                    None if request.form['course_credits']=='' else request.form['course_credits'],
                    request.form.get('is_active', default=False),
                    None if request.form['course_year']=='' else request.form['course_year'],
                    request.form['course_semester'],
                    university_id,
                    request.form.get('venues'),
                    request.form['course_time_slot'],
                    request.form.get('is_course_online', default=False),
                )
                cursor.close()
                return redirect('/home')
            return render_template('create_course.html', venues=venues)
        return redirect('/home') 
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route('/add_course_professor/', defaults={'course_id' : None})
@app.route("/add_course_professor/<course_id>", methods=['GET', 'POST'])
def add_course_professor(course_id):
    try:
        if 'user_id' not in session or not session['is_admin']: return redirect('/home')
        cursor = g.conn.execute(get_course_details, str(course_id))
        course_details = cursor.fetchone()
        cursor.close()
        university_id, course_name =course_details.university_id,course_details.course_name
        if request.method=="POST":
            professors_to_be_added = request.form.getlist('professors')
            for prof in professors_to_be_added:
                cursor = g.conn.execute(add_course_profs,
                    course_id,
                    prof,
                )
                cursor.close()
            return redirect(url_for('course_details', course_id=course_id))
        cursor = g.conn.execute(get_professor_details_all_not_in_course, course_id, university_id)
        all_professors = cursor.fetchall()
        cursor.close()
        return render_template('add_course_professor.html', course_name=course_name, professors=all_professors, course_id=course_id)
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route('/add_course_student/', defaults={'course_id' : None})
@app.route("/add_course_student/<course_id>", methods=['GET', 'POST'])
def add_course_student(course_id):
    try:
        if 'user_id' not in session or not session['is_admin']: return redirect('/home')
        cursor = g.conn.execute(get_course_details, str(course_id))
        course_details = cursor.fetchone()
        university_id, course_name =course_details.university_id,course_details.course_name
        cursor.close()
        if request.method=="POST":
            students_to_be_added = request.form.getlist('students')
            for stud in students_to_be_added:
                cursor = g.conn.execute(student_details,
                    stud,
                )
                total_credits = cursor.fetchone().max_credits_per_sem
                cursor.close()
                cursor = g.conn.execute(get_current_credits_per_sem,
                    course_id,
                    stud,
                )
                credits_already_registered = cursor.fetchone().credits_already_registered
                cursor.close()
                if (0 if credits_already_registered is None else credits_already_registered) + course_details.course_credits > total_credits:
                    cursor = g.conn.execute(user_details_query,
                        stud,
                    )
                    user_info = cursor.fetchone()
                    cursor.close()
                    flash("Exceeding total credits  Email: "+user_info.user_email+" , First Name: "+ user_info.user_first_name + " , Last Name: "+user_info.user_last_name)
                    continue
                cursor = g.conn.execute(add_course_students,
                    course_id,
                    stud,
                )
                cursor.close()
            return redirect(url_for('course_details', course_id=course_id))
        cursor = g.conn.execute(get_student_details_all_not_registered_and_not_ta_in_course, course_id, course_id, university_id)
        all_students = cursor.fetchall()
        cursor.close()
        return render_template('add_course_student.html', course_name=course_name, students=all_students, course_id=course_id)
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route('/add_course_ta/', defaults={'course_id' : None})
@app.route("/add_course_ta/<course_id>", methods=['GET', 'POST'])
def add_course_ta(course_id):
    try:
        if 'user_id' not in session or not session['is_admin']: return redirect('/home')
        cursor = g.conn.execute(get_course_details, str(course_id))
        course_details = cursor.fetchone()
        cursor.close()
        university_id, course_name =course_details.university_id,course_details.course_name
        if request.method=="POST":
            tas_to_be_added = request.form.getlist('students')
            for ta in tas_to_be_added:
                cursor = g.conn.execute(add_course_tas,
                    course_id,
                    ta,
                )
                cursor.close()
            return redirect(url_for('course_details', course_id=course_id))
        cursor = g.conn.execute(get_student_details_all_not_registered_and_not_ta_in_course, course_id, course_id, university_id)
        all_students = cursor.fetchall()
        cursor.close()
        return render_template('add_course_ta.html', course_name=course_name, students=all_students, course_id=course_id)
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route('/remove_course_professor/', defaults={'course_id' : None})
@app.route("/remove_course_professor/<course_id>", methods=['GET', 'POST'])
def remove_course_professor(course_id):
    try:
        if 'user_id' not in session or not session['is_admin']: return redirect('/home')
        cursor = g.conn.execute(get_course_details, str(course_id))
        course_details = cursor.fetchone()
        cursor.close()
        course_name = course_details.course_name
        if request.method=="POST":
            professors_to_be_added = request.form.getlist('professors')
            for prof in professors_to_be_added:
                cursor = g.conn.execute(remove_course_profs,
                    course_id,
                    prof,
                )
                cursor.close()
            return redirect(url_for('course_details', course_id=course_id))
        cursor = g.conn.execute(prof_of_course_details,
                                course_id,
                            )
        all_professors = cursor.fetchall()
        cursor.close()
        return render_template('remove_course_professor.html', course_name=course_name, professors=all_professors, course_id=course_id)
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route('/remove_course_student/', defaults={'course_id' : None})
@app.route("/remove_course_student/<course_id>", methods=['GET', 'POST'])
def remove_course_student(course_id):
    try:
        if 'user_id' not in session or not session['is_admin']: return redirect('/home')
        cursor = g.conn.execute(get_course_details, str(course_id))
        course_details = cursor.fetchone()
        course_name = course_details.course_name
        cursor.close()
        if request.method=="POST":
            students_to_be_added = request.form.getlist('students')
            for stud in students_to_be_added:
                cursor = g.conn.execute(remove_course_students,
                    course_id,
                    stud,
                )
                cursor.close()
            return redirect(url_for('course_details', course_id=course_id))
        cursor = g.conn.execute(student_of_course_details,
                                course_id,
                            )
        all_students = cursor.fetchall()
        cursor.close()
        return render_template('remove_course_student.html', course_name=course_name, students=all_students, course_id=course_id)
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route('/remove_course_ta/', defaults={'course_id' : None})
@app.route("/remove_course_ta/<course_id>", methods=['GET', 'POST'])
def remove_course_ta(course_id):
    try:
        if 'user_id' not in session or not session['is_admin']: return redirect('/home')
        cursor = g.conn.execute(get_course_details, str(course_id))
        course_details = cursor.fetchone()
        cursor.close()
        course_name = course_details.course_name
        if request.method=="POST":
            tas_to_be_added = request.form.getlist('students')
            for ta in tas_to_be_added:
                cursor = g.conn.execute(remove_course_tas,
                    course_id,
                    ta,
                )
                cursor.close()
            return redirect(url_for('course_details', course_id=course_id))
        cursor = g.conn.execute(ta_of_course_details,
                                course_id,
                            )
        all_students = cursor.fetchall()
        cursor.close()
        return render_template('remove_course_ta.html', course_name=course_name, students=all_students, course_id=course_id)
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/assignment_details/", defaults={'assignment_id' : None})
@app.route("/assignment_details/<assignment_id>", methods=['GET','POST'])
def assignment_details(assignment_id):
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            if assignment_id is None and 'assignment_id' in session:
                assignment_id=session['assignment_id']
            if assignment_id is None:
                return redirect('/home')
            session['assignment_id']=assignment_id
            cursor = g.conn.execute(get_assignment_data,
                                    assignment_id,
                                    )
            assignment_data = cursor.fetchone()
            cursor.close()
            submitted_material=None
            marks_obtained=None
            submission_details_all=None
            posted_date=assignment_data.assignment_posted_date
            due_date=assignment_data.assignment_due_date
            course_id=assignment_data.course_id
            current_time=datetime.datetime.now()

            cursor = g.conn.execute(prof_of_course,
                                    course_id,
                                    user_id,
                                )
            is_prof = cursor.rowcount>0
            cursor.close()
            cursor = g.conn.execute(ta_of_course,
                                    course_id,
                                    user_id,
                                )
            is_ta = cursor.rowcount>0
            cursor.close()
            cursor = g.conn.execute(student_of_course,
                                    course_id,
                                    user_id,
                                )
            is_student = cursor.rowcount>0
            cursor.close()

            cursor = g.conn.execute(get_assignment_submission_statistics,
                                    assignment_id,
                                    assignment_id,
                                )
            stats = cursor.fetchone()
            cursor.close()
            if session['is_student'] and posted_date > current_time:
                return redirect('/home')
            form=None
            if is_student:
                cursor = g.conn.execute(get_assignment_submission_data,
                                    assignment_id,
                                    user_id,
                                    )
                assignment_submission_data = cursor.fetchone()
                cursor.close()
                submitted_material = assignment_submission_data.submitted_material if assignment_submission_data else None
                marks_obtained = assignment_submission_data.marks_obtained if assignment_submission_data else None
                if marks_obtained is None and current_time<=due_date:
                    form = Submit_Assignment()
                    if request.method == 'POST':
                        submit_assignment(form.material.data,submitted_material is None)
                        return redirect(url_for('assignment_details', assignment_id=assignment_id))
            if is_prof or is_ta or session['is_admin']:
                cursor = g.conn.execute(get_assignment_submission_data_all,
                                    assignment_id,
                                    assignment_id,
                                    )
                submission_details_all = cursor.fetchall()
                cursor.close()
                

            return render_template('assignment_details.html',
                                assignment_id = assignment_id,
                                is_student=is_student,
                                is_prof=is_prof,
                                submitted_material = submitted_material,
                                marks_obtained = marks_obtained,
                                course_id = session['course_id'],
                                form = form,
                                submission_details_all=submission_details_all,
                                title='Assignment Details',
                                assignment=assignment_data,
                                stats=stats,
                                )
        else: return redirect('/login')
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/create_assignment/", defaults={'course_id' : None})
@app.route('/create_assignment/<course_id>', methods=['GET', 'POST'])
def create_assignment(course_id):
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            cursor = g.conn.execute(prof_of_course,
                                    course_id,
                                    user_id,
                                )
            is_prof = cursor.rowcount>0
            cursor.close()
            if not is_prof:
                return redirect('/home')
            if course_id is None and 'course_id' in session:
                course_id=session['course_id']
            if course_id is None: return redirect('/home')
            form=Create_Assignment()
            if request.method == "POST":
                assignment_id = random.randrange(1000000)
                cursor = g.conn.execute(create_assignment_query,
                    assignment_id,
                    form.assignment_name.data,
                    form.assignment_posted_date.data,
                    form.assignment_due_date.data,
                    form.total_marks.data,
                    course_id,
                )
                cursor.close()
                return redirect(url_for('course_details', course_id=course_id))
            return render_template('create_assignment.html', form=form)
        return redirect('/home') 
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/delete_assignment/", defaults={'assignment_id' : None})
@app.route('/delete_assignment/<assignment_id>', methods=['POST'])
def delete_assignment(assignment_id):
    try:
        if 'user_id' in session:
            if assignment_id is None and 'assignment_id' in session:
                assignment_id=session['assignment_id']
            if assignment_id is None: return redirect('/home')
            user_id=session['user_id']
            cursor = g.conn.execute(get_assignment_data,
                                    assignment_id,
                                )
            course_id = cursor.fetchone().course_id
            cursor.close()
            cursor = g.conn.execute(prof_of_course,
                                    course_id,
                                    user_id,
                                )
            is_prof = cursor.rowcount>0
            if not is_prof:
                return redirect('/home')
            cursor = g.conn.execute(delete_assignment_query,
                assignment_id,
            )
            cursor.close()
            return redirect(url_for('course_details', course_id=course_id))
        return redirect('/home') 
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/delete_course/", defaults={'course_id' : None})
@app.route('/delete_course/<course_id>', methods=['POST'])
def delete_course(course_id):
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            if course_id is None and 'course_id' in session:
                course_id=session['course_id']
            cursor = g.conn.execute(get_course_details,
                course_id,
            )
            university_id = cursor.fetchone().university_id
            cursor.close()
            cursor = g.conn.execute(user_details_query,
                user_id,
            )
            university_id_user = cursor.fetchone().university_id
            cursor.close()
            if course_id is None: return redirect('/home')
            if not session['is_admin'] or university_id != university_id_user:
                return redirect('/home')
            cursor = g.conn.execute(delete_course_query,
                course_id,
            )
            cursor.close()
            return redirect('/home')
        return redirect('/home') 
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route('/delete_university', methods=['POST'])
def delete_university():
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            if not session['is_admin']:
                return redirect('/home')
            cursor = g.conn.execute(user_details_query,
                        user_id,
                        )
            university_id = cursor.fetchone().university_id
            cursor.close()
            cursor = g.conn.execute(delete_university_query,
                university_id,
            )
            cursor.close()
            return redirect('/login')
        return redirect('/home') 
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/delete_user/", defaults={'user_id' : None})
@app.route('/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        if 'user_id' in session:
            if user_id is None: return redirect('/home')
            viewer = session['user_id']
            cursor = g.conn.execute(user_details_query,
                        user_id,
                        )
            university_id = cursor.fetchone().university_id
            cursor.close()
            cursor = g.conn.execute(user_details_query,
                        viewer,
                        )
            university_id_viewer = cursor.fetchone().university_id
            cursor.close()
            if (not session['is_admin'] and user_id != viewer) or university_id!=university_id_viewer:
                return redirect('/home')
            cursor = g.conn.execute(delete_user_query,
                user_id,
            )
            cursor.close()
            return redirect('/home')
        return redirect('/home') 
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/delete_venue/", defaults={'venue_id' : None})
@app.route('/delete_venue/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    try:
        if 'user_id' in session:
            if venue_id is None: return redirect('/home')
            if not session['is_admin']:
                return redirect('/home')
            cursor = g.conn.execute(user_details_query,
                        session['user_id'],
                        )
            university_id_viewer = cursor.fetchone().university_id
            cursor.close()
            cursor = g.conn.execute(get_venue_by_venue_id,
                        venue_id,
                        )
            university_id = cursor.fetchone().university_id
            cursor.close()
            if university_id!=university_id_viewer:
                return redirect('/home')
            cursor = g.conn.execute(delete_venue_query,
                venue_id,
            )
            cursor.close()
            return redirect('/home')
        return redirect('/home') 
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/update_course/", defaults={'course_id' : None})
@app.route('/update_course/<course_id>', methods=['GET', 'POST'])
def update_course(course_id):
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            if course_id is None and 'course_id' in session:
                course_id=session['course_id']
            if course_id is None: return redirect('/home')
            cursor = g.conn.execute(get_course_details,
                course_id,
            )
            course_details = cursor.fetchone()
            cursor.close()
            university_id = course_details.university_id
            cursor = g.conn.execute(user_details_query,
                user_id,
            )
            university_id_user = cursor.fetchone().university_id
            cursor.close()
            cursor = g.conn.execute(get_venue,
                                    university_id,
                                )
            venues = cursor.fetchall()
            cursor.close()
            if (not session['is_admin'] and not session['is_prof']) or university_id != university_id_user:
                return redirect('/home')
            if request.method == "POST":
                cursor = g.conn.execute(update_course_query,
                    request.form['course_name'],
                    request.form['user_description'],
                    request.form['course_credits'],
                    request.form.get('is_active', default=False),
                    request.form['course_year'],
                    request.form['course_semester'],
                    request.form.get('venues'),
                    request.form['course_time_slot'],
                    request.form.get('is_course_online', default=False),
                    course_id,
                )
                cursor.close()    
                return redirect(url_for('course_details', course_id=course_id))
            return render_template('update_course.html', course=course_details, venues=venues)
        return redirect('/home') 
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/update_assignment/", defaults={'assignment_id' : None})
@app.route('/update_assignment/<assignment_id>', methods=['GET', 'POST'])
def update_assignment(assignment_id):
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            if assignment_id is None and 'assignment_id' in session:
                assignment_id=session['assignment_id']
            if assignment_id is None: return redirect('/home')
            cursor = g.conn.execute(get_assignment_data,
                assignment_id,
            )
            assignment_details = cursor.fetchone()
            cursor.close()
            cursor = g.conn.execute(get_course_details,
                assignment_details.course_id,
            )
            course_details = cursor.fetchone()
            cursor.close()
            university_id = course_details.university_id
            university_id = course_details.university_id
            cursor = g.conn.execute(user_details_query,
                user_id,
            )
            university_id_user = cursor.fetchone().university_id
            cursor.close()
            if (not session['is_admin'] and not session['is_prof']) or university_id != university_id_user:
                return redirect('/home')
            if request.method == "POST":
                cursor = g.conn.execute(update_assignment_query,
                    request.form['assignment_name'],
                    request.form['assignment_posted_date'],
                    request.form['assignment_due_date'],
                    request.form['total_marks'],
                    assignment_id,
                )
                cursor.close()    
                return redirect(url_for('assignment_details', assignment_id=assignment_id))
            return render_template('update_assignment.html', assignment=assignment_details)
        return redirect('/home') 
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route("/update_venue/", defaults={'venue_id' : None})
@app.route('/update_venue/<venue_id>', methods=['GET', 'POST'])
def update_venue(venue_id):
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            if venue_id is None and 'venue_id' in session:
                venue_id=session['venue_id']
            if venue_id is None: return redirect('/home')
            if not session['is_admin']:
                return redirect('/home')
            cursor = g.conn.execute(user_details_query,
                                    user_id,
                                )
            university_id = cursor.fetchone().university_id
            cursor.close()
            cursor = g.conn.execute(get_venue_by_venue_id,
                                    venue_id,
                                )
            venue = cursor.fetchone()
            cursor.close()        
            if university_id!=venue.university_id:
                return redirect('/home')
            if request.method == "POST":
                cursor = g.conn.execute(update_venue_query,
                    request.form['venue_building'],
                    request.form['venue_class_number'],
                    venue_id,
                )
                cursor.close()
                return redirect('/home')
            return render_template('update_venue.html', venue=venue)
        return redirect('/home') 
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

@app.route('/update_university', methods=['GET', 'POST'])
def update_university():
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            if not session['is_admin']:
                return redirect('/home')
            cursor = g.conn.execute(user_details_query,
                                    user_id,                    
                                    )
            university_id = cursor.fetchone().university_id
            cursor.close()
            cursor = g.conn.execute(university_details_query, university_id)
            uni_info = cursor.fetchone()
            cursor.close()
            if request.method == "POST":
                cursor = g.conn.execute(update_university_query,
                    request.form['university_city'],
                    request.form['university_state'],
                    request.form['university_address'],
                    None if request.form['university_pincode']=='' else request.form['university_pincode'],
                    None if request.form['university_establishment_date']=='' else request.form['university_establishment_date'],
                    university_id,
                )
                cursor.close()
                return redirect('/university')
            return render_template('update_university.html', university=uni_info)
        return redirect('/home')
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

def submit_assignment(new_link,
                      is_first_submission,
                      ):
    assignment_id = session['assignment_id']
    user_id = session['user_id']
    if is_first_submission:
        cursor = g.conn.execute(submit_assignment_material_first,
                        assignment_id,
                        user_id,
                        new_link,
                    )
        cursor.close()
    else:
        cursor = g.conn.execute(submit_assignment_material_update,
                        new_link,
                        assignment_id,
                        user_id,
                ) 
        cursor.close()

@app.route('/update_marks', defaults={'user_id': None})
@app.route('/update_marks/<user_id>', methods=["GET", "POST"])
def update_assignment_marks(user_id):
    try:
        if 'user_id' not in session: return redirect('/login')
        form = Marks_Assignment()
        if user_id is None:
            return redirect('/home')
        assignment_id = session['assignment_id']
        cursor = g.conn.execute(get_assignment_submission_data,
                        assignment_id,
                        user_id,
                        )
        assignment_submission_data = cursor.fetchone()
        cursor.close()
        cursor = g.conn.execute(get_assignment_data,
                        assignment_id,
                        )
        total_marks = cursor.fetchone().total_marks
        cursor.close()
        cursor = g.conn.execute(user_details_query,
                        user_id,
                        )
        user_details = cursor.fetchone()
        cursor.close()
        if request.method=="POST":
            if form.marks.data > total_marks:
                flash("Marks assigned exceeding total marks of assignment")
            else:
                give_assignment_marks(form.marks.data, assignment_submission_data is None, user_id)
            return redirect(url_for('update_assignment_marks', user_id=user_id))
        return render_template('update_marks.html', form=form, assignment_submission_data=assignment_submission_data, user_details=user_details)
    except Exception:
        flash('Something went wrong')
        return redirect('/home')

def give_assignment_marks(marks,
                      is_first_submission,
                      user_id,
                      ):
    assignment_id = session['assignment_id']
    if is_first_submission:
        cursor = g.conn.execute(give_assignment_marks_first,
                        assignment_id,
                        user_id,
                        None,
                        marks,
                    )
        cursor.close()
    else:
        cursor = g.conn.execute(give_assignment_marks_update,
                        marks,
                        assignment_id,
                        user_id,
                ) 
        cursor.close()
