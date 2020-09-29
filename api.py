"""
This Flask app implements the same REST API as api.py, but it uses
Flask view classes instead of decorated functions. Using view classes helps
group together all the functions for a particular resource, and can add
flexibility.
This app also adds error handling via a custom exception. The
@app.errorhandler decorator allows for defining a function that will be called
when a specific exception is raised. Our custom exception builds a JSON
response with a provided error message and status code, and the error handler
takes care of returning that response to the client.
"""

from flask import Flask, g, jsonify, request, render_template, url_for
from flask.views import MethodView
from werkzeug.utils import redirect
from database import Database
import os

app = Flask(__name__)

app.config['DATABASE'] = os.path.join(app.root_path, 'database.sqlite')


def get_db():
    """
    Returns a Database instance for accessing the database. If the database
    file does not yet exist, it creates a new database.
    """

    if not hasattr(g, 'database'):
        g.database = Database(app.config['DATABASE'])

    return g.database


class RequestError(Exception):
    """
    This custom exception class is for easily handling errors in requests,
    such as when the user provides an ID that does not exist or omits a
    required field.
    We inherit from the Exception class, which is the base Python class that
    provides basic exception functionality. Our custom exception class takes
    a status code and error message in its initializer, and then has a
    to_response() method which creates a JSON response. When an exception of
    this type is raised, the error handler will take care of sending the
    response to the client.
    """

    def __init__(self, status_code, error_message):
        # Call the super class's initializer. Unlike in C++, this does not
        # happen automatically in Python.
        super().__init__(self)

        self.status_code = str(status_code)
        self.error_message = error_message

    def to_response(self):
        """
        Create a Response object containing the error message as JSON.
        :return: the response
        """

        response = jsonify({'error': self.error_message})
        response.status = self.status_code
        return response


@app.errorhandler(RequestError)
def handle_invalid_usage(error):
    """
    Returns a JSON response built from a RequestError.
    :param error: the RequestError
    :return: a response containing the error message
    """
    return error.to_response()


class StudentsView(MethodView):
    """
    This view handles all the /students requests.
    """

    def get(self, student_id):
        """
        Handle GET requests.
        Returns JSON representing all of the students if student_id is None,
        or a single student if student_id is not None.
        :param student_id: id of a student, or None for all students
        :return: JSON response
        """
        if student_id is None:
            students = get_db().get_all_students()
            return jsonify(students)
        else:
            student = get_db().get_student_by_id(student_id)

            if student is not None:
                response = jsonify(student)
            else:
                raise RequestError(404, 'student not found')

            return response

    def post(self):
        """
        Implements POST /students
        Requires the form parameters 'name', 'age', 'class_year', 'major'
        :return: JSON response representing the new student
        """

        for parameter in ('name', 'age', 'class_year', 'major'):
            if parameter not in request.form:
                error = 'parameter {} required'.format(parameter)
                raise RequestError(422, error)

        student = get_db().insert_student(request.form['name'],
                                          request.form['age'],
                                          request.form['class_year'],
                                          request.form['major'])
        return jsonify(student)

    def delete(self, student_id):
        """
        Handle DELETE requests. The student_id must be provided.
        :param student_id: id of a student
        :return: JSON response containing a message
        """
        if get_db().get_student_by_id(student_id) is None:
            raise RequestError(404, 'student not found')

        get_db().delete_student(student_id)

        return jsonify({'message': 'student deleted successfully'})


class TutorsView(MethodView):
    """
    This view handles all the /tutors requests.
    """

    def get(self, tutor_id):
        """
        Handle GET requests.
        Returns JSON representing all of the tutors if tutor_id is None, or a
        single tutor if tutor_id is not None.
        :param tutor_id: id of a tutor, or None for all tutors
        :return: JSON response
        """
        if tutor_id is None:
            tutors = get_db().get_all_tutors()
            return jsonify(tutors)
        else:
            tutor = get_db().get_tutor_by_id(tutor_id)

            if tutor is not None:
                response = jsonify(tutor)
            else:
                raise RequestError(404, 'tutor not found')

            return response

    def post(self):
        """
        Implements POST /tutors
        Requires the form parameters 'name', 'age', 'class_year', 'major'
        :return: JSON response representing the new student
        """

        for parameter in ('name', 'age', 'area_of_expertise', 'cost'):
            if parameter not in request.form:
                error = 'parameter {} required'.format(parameter)
                raise RequestError(422, error)

        tutor = get_db().insert_tutor(request.form['name'],
                                      request.form['age'],
                                      request.form['area_of_expertise'],
                                      request.form['cost'])
        return jsonify(tutor)

    def delete(self, tutor_id):
        """
        Handle DELETE requests. The tutor_id must be provided.
        :param tutor_id: id of a tutor
        :return: JSON response containing a message
        """
        if get_db().get_tutor_by_id(tutor_id) is None:
            raise RequestError(404, 'tutor not found')

        get_db().delete_tutor(tutor_id)

        return jsonify({'message': 'tutor deleted successfully'})


# Register StudentsView as the handler for all the /students/ requests
students_view = StudentsView.as_view('students_view')
app.add_url_rule('/students', defaults={'student_id': None},
                 view_func=students_view, methods=['GET', 'DELETE'])
app.add_url_rule('/students', view_func=students_view, methods=['POST'])
app.add_url_rule('/students/<int:student_id>', view_func=students_view,
                 methods=['GET', 'DELETE'])

# Register TutorsView as the handler for all the /tutors/ requests
tutors_view = TutorsView.as_view('tutors_view')
app.add_url_rule('/tutors', defaults={'tutor_id': None},
                 view_func=tutors_view, methods=['GET', 'DELETE'])
app.add_url_rule('/tutors', view_func=tutors_view, methods=['POST'])
app.add_url_rule('/tutors/<int:tutor_id>', view_func=tutors_view,
                 methods=['GET', 'DELETE'])


@app.route('/')
def views():
    """
    Serves a page which shows the student view and tutor view.
    """
    return render_template('views.html')


@app.route('/database')
def view_database():
    """
    Serves a page which shows the database.
    """
    return render_template('database.html')


@app.route('/student_list')
def students():
    """
     Serves a page which shows the name, age, class year and major of all
     students.
    """
    return render_template('student_list.html',
                           student_list=get_db().get_all_students())


@app.route('/tutor_list')
def tutors():
    """
    Serves a page which shows the name, age, area of expertise and cost of
    all tutors.
    """
    return render_template('tutor_list.html',
                           tutor_list=get_db().get_all_tutors())


@app.route('/student_page/<student_id>', methods=['GET', 'POST'])
def student_page(student_id):
    """
    Serves a page which shows a student's page after login to view, hire
    tutors and remove them.
    """
    display_notice = False
    successful_add = None
    notice_text = None
    tutor_list = get_db().get_all_tutors()
    tutors_from_student = get_db().get_tutor_from_student(student_id)

    if tutors_from_student is None:
        tutors_from_student = []

    if 'id' in request.form:
        display_notice = True
        id = request.form['id'].strip()

        if id == '':
            successful_add = False
            notice_text = 'You must enter the field to continue.'

        elif get_db().search_tutor_id(id) is False:
            successful_add = False
            notice_text = "Tutor does not exist."

        elif get_db().tutor_is_hired(student_id, id) is True:
            successful_add = False
            notice_text = "Tutor already hired."

        else:
            successful_add = True
            get_db().insert_student_tutor(student_id, id)
            return redirect(url_for('student_page', student_id=student_id))

    display_notice2 = False
    successful_add2 = None
    notice_text2 = None
    if 'id2' in request.form:
        display_notice2 = True
        id = request.form['id2'].strip()

        if id == '':
            successful_add2 = False
            notice_text2 = 'You must enter the field to continue.'

        elif get_db().search_tutor_id(id) is False:
            successful_add2 = False
            notice_text2 = "Tutor does not exist."

        elif get_db().tutor_is_hired(student_id, id) is False:
            successful_add2 = False
            notice_text2 = "Tutor is not hired."

        else:
            successful_add2 = True
            get_db().delete_student_tutor(student_id, id)
            return redirect(url_for('student_page', student_id=student_id))

    return render_template('student_page.html',
                           tutors_from_student=tutors_from_student,
                           tutor_list=tutor_list,
                           display_notice=display_notice,
                           successful_add=successful_add,
                           notice_text=notice_text,
                           student_id=student_id,
                           display_notice2=display_notice2,
                           successful_add2=successful_add2,
                           notice_text2=notice_text2)


@app.route('/tutor_page/<tutor_id>', methods=['GET', 'POST'])
def tutor_page(tutor_id):
    """
    Serves a page which shows a tutor's page after login to view, and delete
    his students if hired by them.
    """
    students_from_tutor = get_db().get_students_from_tutor(tutor_id)
    if students_from_tutor is None:
        students_from_tutor = []

    display_notice = False
    successful_add = None
    notice_text = None

    if 'id' in request.form:
        display_notice = True
        id = request.form['id'].strip()

        if id == '':
            successful_add = False
            notice_text = 'You must enter the field to continue.'

        elif get_db().search_student_id(id) is False:
            successful_add = False
            notice_text = "Student does not exist."

        elif get_db().tutor_is_hired(id, tutor_id) is False:
            successful_add = False
            notice_text = "You are not hired by the student with that id."

        else:
            successful_add = True
            get_db().delete_student_tutor(id, tutor_id)
            return redirect(url_for('tutor_page', tutor_id=tutor_id))

    return render_template('tutor_page.html',
                           students_from_tutor=students_from_tutor,
                           student_list=get_db().get_all_students(),
                           display_notice=display_notice,
                           successful_add=successful_add,
                           notice_text=notice_text)


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    """
    Serves a page which enables students to log in create an account.
    """

    display_notice = False
    successful_add = None
    notice_text = None
    username = None
    password = None

    if 'username' in request.form and 'password' in request.form \
            and 'name' in request.form and 'age' in request.form \
            and 'class_year' in request.form and 'major' in request.form:
        display_notice = True

        # strip() removes whitespace from either side of a string
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        name = request.form['name'].strip()
        age = request.form['age'].strip()
        class_year = request.form['class_year'].strip()
        major = request.form['major'].strip()

        max_length = 100
        age_max = 2
        class_max = 4

        if username == '' or password == '' or name == '' or age == '' \
                or class_year == '' or major == '':
            successful_add = False
            notice_text = 'You must enter all the fields to continue.'
        elif len(name) > max_length or len(age) > age_max or \
                len(class_year) > class_max or len(major) > max_length:
            successful_add = False
            notice_text = 'Name & major must be 100 character long, ' \
                          'age must be 2 character, & ' \
                          'class year must be 4 character long.'
        else:
            successful_add = True
            get_db().insert_student(username, password, name, age,
                                    class_year, major)
            notice_text = '{} added successfully!'.format(username,
                                                          password, name,
                                                          age, class_year,
                                                          major)
            return redirect(url_for('student_page',
                                    student_id=get_db().get_student_id(
                                        username, password)))

    display_notice2 = False
    successful_add2 = None
    notice_text2 = None
    username = None
    password = None

    if 'username' in request.form and 'password' in request.form \
            and 'name' not in request.form and 'age' not in request.form \
            and 'class_year' not in request.form \
            and 'major' not in request.form:
        display_notice2 = True

        # strip() removes whitespace from either side of a string
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if username == '' or password == '':
            successful_add2 = False
            notice_text2 = 'You must enter all the fields to continue.'
        elif get_db().get_student_id(username, password) is False:
            successful_add2 = False
            notice_text2 = 'Wrong password.'

        elif get_db().get_student_id(username, password) is not False:
            successful_add2 = True
            return redirect(url_for('student_page',
                                    student_id=get_db().get_student_id(
                                        username, password)))

    return render_template('add_student.html', display_notice=display_notice,
                           successful_add=successful_add,
                           notice_text=notice_text,
                           display_notice2=display_notice2,
                           successful_add2=successful_add2,
                           notice_text2=notice_text2,
                           student_id=get_db().get_student_id(username,
                                                              password))


@app.route('/add_tutor', methods=['GET', 'POST'])
def add_tutor():
    """
    Serves a page which enables tutors to log in or create an account.
    """

    display_notice = False
    successful_add = None
    notice_text = None
    username = None
    password = None
    if 'username' in request.form and 'password' in request.form \
            and 'name' in request.form and 'age' in request.form \
            and 'area_of_expertise' in request.form and 'cost' in request.form:
        display_notice = True

        # strip() removes whitespace from either side of a string
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        name = request.form['name'].strip()
        age = request.form['age'].strip()
        area_of_expertise = request.form['area_of_expertise'].strip()
        cost = request.form['cost'].strip()

        max_length = 100
        age_max = 2

        if username == '' or password == '' or name == '' or age == '' \
                or area_of_expertise == '' or cost == '':
            successful_add = False
            notice_text = 'You must enter all the fields to continue.'
        elif len(name) > max_length or len(age) > age_max or \
                len(area_of_expertise) > max_length:
            successful_add = False
            notice_text = 'Name & area of expertise must be 100 character ' \
                          'long, age must be 2 character.'
        else:
            successful_add = True
            get_db().insert_tutor(username, password, name, age,
                                  area_of_expertise, cost)
            notice_text = '{} added successfully!'.format(username, password,
                                                          name, age,
                                                          area_of_expertise,
                                                          cost)
            return redirect(url_for('tutor_page',
                                    tutor_id=get_db().get_tutor_id(username,
                                                                   password)))

    display_notice2 = False
    successful_add2 = None
    notice_text2 = None
    username = None
    password = None
    if 'username' in request.form and 'password' in request.form \
            and 'name' not in request.form and 'age' not in request.form \
            and 'area_of_expertise' not in request.form \
            and 'cost' not in request.form:
        display_notice2 = True

        # strip() removes whitespace from either side of a string
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if username == '' or password == '':
            successful_add2 = False
            notice_text2 = 'You must enter all the fields to continue.'
        elif get_db().get_tutor_id(username, password) is False:
            successful_add2 = False
            notice_text2 = 'Wrong password.'

        elif get_db().get_tutor_id(username, password) is not False:
            successful_add2 = True
            return redirect(url_for('tutor_page',
                                    tutor_id=get_db().get_tutor_id(username,
                                                                   password)))

    return render_template('add_tutor.html', display_notice=display_notice,
                           successful_add=successful_add,
                           notice_text=notice_text,
                           display_notice2=display_notice2,
                           successful_add2=successful_add2,
                           notice_text2=notice_text2,
                           tutor_id=get_db().get_tutor_id(username, password))


if __name__ == '__main__':
    app.run(debug=True)
