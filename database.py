import os
import sqlite3
import bcrypt as bcrypt


def row_to_dict_or_none(cur):
    """
    Given a cursor that has just been used to execute a query, try to fetch
    one row. If the there is no row to fetch, return None, otherwise return a
    dictionary representation of the row.
    :param cur: a cursor that has just been used to execute a query
    :return: a dict representation of the next row, or None
    """
    row = cur.fetchone()
    if row is None:
        return None
    else:
        return dict(row)


class Database:

    def __init__(self, sqlite_filename):
        """
        Creates a connection to the database, and creates tables if the
        database file did not exist prior to object creation.
        :param sqlite_filename: the name of the SQLite database file
        """
        if os.path.isfile(sqlite_filename):
            create_tables = False
        else:
            create_tables = True

        self.conn = sqlite3.connect(sqlite_filename)
        self.conn.row_factory = sqlite3.Row

        cur = self.conn.cursor()
        cur.execute('PRAGMA foreign_keys = 1')
        cur.execute('PRAGMA journal_mode = WAL')
        cur.execute('PRAGMA synchronous = NORMAL')

        if create_tables:
            self.create_tables()

    def create_tables(self):
        """
        Create the tables class_year, major, student and tutor.
        """

        cur = self.conn.cursor()
        cur.execute(
            'CREATE TABLE class_year(class_year_id INTEGER PRIMARY KEY, '
            '    class_year INTEGER UNIQUE)')
        cur.execute('CREATE TABLE major(major_id INTEGER PRIMARY KEY, '
                    '    major TEXT UNIQUE)')
        cur.execute('CREATE TABLE student(student_id INTEGER PRIMARY KEY, '
                    '    username TEXT, password TEXT, salt TEXT, '
                    '    name TEXT, age INTEGER, class_year_id INTEGER, '
                    '    major_id INTEGER, '
                    '    FOREIGN KEY (class_year_id) '
                    'REFERENCES class_year(class_year_id), '
                    '    FOREIGN KEY (major_id) REFERENCES major(major_id)) ')
        cur.execute('CREATE TABLE tutor(tutor_id INTEGER PRIMARY KEY, '
                    '     username TEXT, password TEXT, salt TEXT, '
                    '    name TEXT, age INTEGER, area_expertise_id INTEGER, '
                    '    cost INTEGER, '
                    '    FOREIGN KEY (area_expertise_id) '
                    'REFERENCES major(major_id)) ')
        cur.execute(
            'CREATE TABLE student_tutor(student_tutor INTEGER PRIMARY KEY, '
            '    student_id INTEGER, tutor_id INTEGER, '
            '    FOREIGN KEY (student_id) REFERENCES student(student_id), '
            '    FOREIGN KEY (tutor_id) REFERENCES tutor(tutor_id)) ')
        self.conn.commit()

    def insert_student(self, username, password, name, age, class_year,
                       major):
        """
        Inserts a student into the database. If the student's
        major and class year is not in the database, inserts
        class_year and major too.
        Returns a dictionary representation of the student.
        :param username: username of the student
        :param password: password for the username
        :param name: name of the student
        :param age: age of the student
        :param class_year: class_year of the student
        :param major: major of the student
        :return: a dict representing the student
        """
        cur = self.conn.cursor()
        self.insert_major(major)
        major_dict = self.get_major_by_name(major)
        major_id = major_dict['major_id']
        self.insert_class_year(class_year)
        class_year_dict = self.get_class_year_by_year(class_year)
        class_year_id = class_year_dict['class_year_id']
        salt = bcrypt.gensalt()

        query = ('INSERT INTO student(username, password, salt, name, '
                 '                    age, class_year_id, major_id) '
                 '                    VALUES(?, ?, ?, ?, ?, ?, ?)')
        cur.execute(query, (
            username, bcrypt.hashpw(password.encode(), salt).decode(),
            salt.decode(), name, age, class_year_id, major_id))
        self.conn.commit()
        return self.get_student_by_id(cur.lastrowid)

    def insert_major(self, major):
        """
        Inserts a major in the database if it does not exist. Do nothing if
        there is already a major with the given name in the database.
        :param major: name of the major
        :return: dict representing the major
        """
        cur = self.conn.cursor()
        query = 'INSERT OR IGNORE INTO major(major) VALUES(?)'
        cur.execute(query, (major,))
        self.conn.commit()
        return self.get_major_by_name(major)

    def get_major_by_name(self, major):
        """
        Get a dictionary representation of the major with the given name.
        Return None if there is no such major.
        :param major: name of the major
        :return: a dict representing the major, or None
         """
        cur = self.conn.cursor()
        query = 'SELECT major_id, major from major WHERE major = ?'
        cur.execute(query, (major,))
        return row_to_dict_or_none(cur)

    def insert_class_year(self, class_year):
        """
        Inserts a class year in the database if it does not exist. Do nothing
        if there is already a class year with the given year in the database.
        :param class_year: year of the class
        :return: dict representing the class year
        """
        cur = self.conn.cursor()
        query = 'INSERT OR IGNORE INTO class_year(class_year) VALUES(?)'
        cur.execute(query, (class_year,))
        self.conn.commit()
        return self.get_class_year_by_year(class_year)

    def get_class_year_by_year(self, class_year):
        """
        Get a dictionary representation of the class year with the
        given year.
        Return None if there is no such year.
        :param class_year: year of the class
        :return: a dict representing the class year, or None
        """
        cur = self.conn.cursor()
        query = 'SELECT class_year_id, class_year FROM class_year ' \
                'WHERE class_year = ?'
        cur.execute(query, (class_year,))
        return row_to_dict_or_none(cur)

    def insert_tutor(self, username, password, name, age, area_of_expertise,
                     cost):
        """
        Inserts a tutor into the database.
        Returns a dictionary representation of the tutor.
        :param username: username of the tutor
        :param password: password of the username
        :param name: name of the tutor
        :param age: age of the tutor
        :param area_of_expertise: area of expertise of the tutor
        :param cost: cost of hiring the tutor
        :return: a dict representing the student
        """
        cur = self.conn.cursor()
        self.insert_major(area_of_expertise)
        major_dict = self.get_major_by_name(area_of_expertise)
        area_expertise_id = major_dict['major_id']
        salt = bcrypt.gensalt()
        query = (
            'INSERT INTO tutor(username, password, salt, name, age, '
            'area_expertise_id, cost) '
            'VALUES(?, ?, ?, ?, ?, ?, ?)')
        cur.execute(query, (username,
                            bcrypt.hashpw(password.encode(), salt).decode(),
                            salt.decode(), name, age, area_expertise_id,
                            cost))
        self.conn.commit()
        return self.get_tutor_by_id(cur.lastrowid)

    def get_student_by_id(self, student_id):
        """
        Given a student's primary key, return a dictionary representation of
        the student, or None if there is no student with that primary key.
        :param student_id: the primary key of the student
        :return: a dict representing the student
        """
        cur = self.conn.cursor()

        query = (
            'SELECT student.student_id as student_id, student.name as name, '
            'student.age as age, class_year.class_year as class_year, '
            'major.major as major '
            'FROM student, major, class_year '
            'WHERE student.class_year_id = class_year.class_year_id '
            'AND student.major_id = major.major_id '
            'AND student.student_id = ? ')

        cur.execute(query, (student_id,))
        return row_to_dict_or_none(cur)

    def get_tutor_by_id(self, tutor_id):
        """
        Given a tutors's primary key, return a dictionary representation of
        the tutor, or None if there is no tutor with that primary key.
        :param tutor_id: the primary key of the tutor
        :return: a dict representing the tutor
        """
        cur = self.conn.cursor()

        query = ('SELECT tutor.tutor_id as tutor_id, tutor.name as name, '
                 'tutor.age as age, major.major as area_of_expertise, '
                 'tutor.cost as cost '
                 'FROM tutor, major '
                 'WHERE tutor.area_expertise_id = major.major_id '
                 'AND tutor.tutor_id = ? ')

        cur.execute(query, (tutor_id,))
        return row_to_dict_or_none(cur)

    def get_all_students(self):
        """
        Return a list dictionaries representing all of the students in the
        database.
        :return: a list of dict objects representing students
        """
        cur = self.conn.cursor()

        query = ('SELECT student.student_id as student_id, '
                 'student.name as name, '
                 'student.age as age, class_year.class_year as class_year, '
                 'major.major as major '
                 'FROM student, major, class_year '
                 'WHERE student.class_year_id = class_year.class_year_id '
                 'AND student.major_id = major.major_id ')

        students = []
        cur.execute(query)

        for row in cur.fetchall():
            students.append(dict(row))

        return students

    def get_all_tutors(self):
        """
        Return a list dictionaries representing all of the tutors in the
        database.
        :return: a list of dict objects representing tutors
        """
        cur = self.conn.cursor()

        query = ('SELECT tutor.tutor_id as tutor_id, tutor.name as name, '
                 'tutor.age as age, major.major as area_of_expertise, '
                 'tutor.cost as cost '
                 'FROM tutor, major '
                 'WHERE tutor.area_expertise_id = major.major_id')

        tutors = []
        cur.execute(query)

        for row in cur.fetchall():
            tutors.append(dict(row))

        return tutors

    def delete_student(self, student_id):
        """
        Delete the student with the given primary key.
        :param student_id: primary key of the student
        """
        cur = self.conn.cursor()

        query = 'DELETE FROM student WHERE student_id = ?'
        cur.execute(query, (student_id,))

        self.conn.commit()

    def delete_tutor(self, tutor_id):
        """
        Delete the student with the given primary key.
        :param tutor_id: primary key of the student
        """
        cur = self.conn.cursor()

        query = 'DELETE FROM tutor WHERE tutor_id = ?'
        cur.execute(query, (tutor_id,))

        self.conn.commit()

    def insert_student_tutor(self, student_id, tutor_id):
        """
        Creates a connection between a student and a tutor.
        :param student_id: the primary key of the student
        :param tutor_id: the primary key of the tutor
        """
        cur = self.conn.cursor()
        query = 'INSERT OR IGNORE INTO student_tutor(student_id, tutor_id) ' \
                'VALUES(?,?)'
        cur.execute(query, (student_id, tutor_id))
        self.conn.commit()
        return 0

    def get_students_from_tutor(self, tutor_id):
        """
        Gets all the students from a specific tutor.
        :param tutor_id: the primary key of the tutor
        """
        cur = self.conn.cursor()
        query = ('SELECT student_tutor.student_id as student_id '
                 'FROM student_tutor '
                 'WHERE student_tutor.tutor_id = ? ')

        students_id = []
        cur.execute(query, (tutor_id,))

        students_from_tutor = []
        for row in cur.fetchall():
            for x in row:
                students_id.append(x)

        if len(students_id) == 0:
            return None

        else:

            for ID in students_id:
                students_from_tutor.append(self.get_student_by_id(ID))

            return students_from_tutor

    def get_tutor_from_student(self, student_id):
        """
        Gets tutors from a specific student.
        :param student_id: the primary key of the student
        """
        cur = self.conn.cursor()
        query = ('SELECT student_tutor.tutor_id as tutor_id '
                 'FROM student_tutor '
                 'WHERE student_tutor.student_id = ? ')

        tutor_id = []
        cur.execute(query, (student_id,))

        tutors_from_student = []
        for row in cur.fetchall():
            for x in row:
                tutor_id.append(x)

        if len(tutor_id) == 0:
            return None

        else:
            for ID in tutor_id:
                tutors_from_student.append(self.get_tutor_by_id(ID))

            return tutors_from_student

    def get_student_id(self, username, password):
        """
        Returns the student id if there is a student with that username and
        password.
        Returns false if something is incorrect.
        :param username: username of the student
        :param password: password of the username
        """
        cur = self.conn.cursor()
        query = (
            'SELECT student.student_id as student_id, '
            'student.password as password, student.salt as salt '
            'FROM student '
            'WHERE student.username = ? ')
        cur.execute(query, (username,))

        id = row_to_dict_or_none(cur)
        if id is None:
            return False
        else:
            if bcrypt.hashpw(password.encode(), id['salt'].encode()) == \
                    id['password'].encode():
                return id['student_id']
            else:
                return False

    def get_tutor_id(self, username, password):
        """
        Returns the tutor id if there is a student with that username and
        password.
        Returns false if something is incorrect.
        :param username: username of the tutor
        :param password: password of the tutor
        """
        cur = self.conn.cursor()
        query = ('SELECT tutor.tutor_id as tutor_id, '
                 'tutor.password as password, tutor.salt as salt  '
                 'FROM tutor '
                 'WHERE tutor.username = ? ')
        cur.execute(query, (username,))
        id = row_to_dict_or_none(cur)
        if id is None:
            return False
        else:
            if bcrypt.hashpw(password.encode(), id['salt'].encode()) == \
                    id['password'].encode():
                return id['tutor_id']
            else:
                return False

    def search_tutor_id(self, tutor_id):
        """
        Returns True if a tutor with a specific id
        exists. Otherwise, returns False.
        :param tutor_id: id of the tutor
        """
        for a_tutor in self.get_all_tutors():
            if a_tutor['tutor_id'] == int(tutor_id):
                return True
        return False

    def search_student_id(self, student_id):
        """
        Returns True if a student with a specific id exists. Otherwise,
        returns False.
        :param student_id: id of the tutor
        """
        if self.get_all_students() is None:
            return False
        for a_student in self.get_all_students():
            if a_student['student_id'] == int(student_id):
                return True
        return False

    def tutor_is_hired(self, student_id, tutor_id):
        """
        Returns True if a specific tutor is hired by a specific
        student. Otherwise, returns False.
        :param student_id: id of the student
        :param tutor_id: id of the tutor
       """
        if self.get_tutor_from_student(student_id) is None:
            return False
        for a_tutor in self.get_tutor_from_student(student_id):
            if a_tutor['tutor_id'] == int(tutor_id):
                return True
        return False

    def delete_student_tutor(self, student_id, tutor_id):
        """
        Deletes match between student and tutor, removing
        it from the student_tutor table.
        :param student_id: id of the student
        :param tutor_id: id of the tutor
        """
        cur = self.conn.cursor()

        query = 'DELETE FROM student_tutor ' \
                'WHERE student_id = ? ' \
                'AND tutor_id = ? '
        cur.execute(query, (student_id, tutor_id))

        self.conn.commit()


if __name__ == '__main__':
    db = Database('database.sqlite')
    db.insert_tutor('pp22', 'pp', 'Pratisth', 21, 'Chemistry', 200)
    db.insert_tutor('shawn22', 'shawn', 'Shawn', 20, 'Computer Science', 10)
    print(db.get_all_tutors())
    print(db.search_tutor_id(8))
    for a_tutor in db.get_all_tutors():
        print(a_tutor['tutor_id'])
    db.insert_student('aloniliber', 'oliu', 'Alon', 20, 2022,
                      'Computer Science')
    db.insert_student('marco22', 'marco', 'Marco', 20, 2020,
                      'Biology')
    print(db.get_student_by_id(1))
    print(db.get_student_by_id(2))
    print(db.get_tutor_by_id(2))
    print(db.get_tutor_by_id(1))
    print(db.get_tutor_by_id(3))
