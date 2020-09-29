from database import Database


def build_db_path(directory):
    return directory / 'database.sqlite'


def test_initializer(tmp_path):
    Database(build_db_path(tmp_path))


def test_insert_student(tmp_path):
    db = Database(build_db_path(tmp_path))

    student = db.insert_student('Shawn22', 'The', 'Shawn', 21, 2022,
                                'Economics')

    assert student['name'] == 'Shawn'
    assert student['age'] == 21
    assert student['class_year'] == 2022
    assert student['major'] == 'Economics'


def test_get_student_by_id(tmp_path):
    db = Database(build_db_path(tmp_path))
    assert db.get_student_by_id(1) is None

    student_inserted = db.insert_student('Shawn22', 'The', 'Shawn', 21, 2022,
                                         'Economics')
    student = db.get_student_by_id(1)

    assert student_inserted == student
    assert db.get_student_by_id(2) is None

    student_inserted = db.insert_student('Alon22', 'Alon', 'Alon', 55, 2022,
                                         'Computer Science')
    student = db.get_student_by_id(2)

    assert student_inserted == student
    assert db.get_student_by_id(3) is None


def test_get_all_students(tmp_path):
    db = Database(build_db_path(tmp_path))

    assert db.get_all_students() == []

    student_inserted = db.insert_student('Gunjan22', 'Gun', 'Gunjan', 9, 2022,
                                         'Computer Science')
    students_inserted = [student_inserted]

    students = db.get_all_students()
    assert len(students) == 1
    assert students[0] == student_inserted

    students_inserted.append(
        db.insert_student('Shawn22', 'The', 'Shawn', 21, 2022, 'Economics'))

    students = db.get_all_students()

    assert len(students) == 2

    for student in students:
        assert student in students


def test_delete_student(tmp_path):
    db = Database(build_db_path(tmp_path))
    student_inserted = db.insert_student('Gungun', 'Gun2', 'Gunjan', 9, 2022,
                                         'English')
    students = db.get_all_students()

    assert len(students) == 1
    assert students[0] == student_inserted

    students = db.delete_student(1)
    assert students is None


def test_insert_major(tmp_path):
    db = Database(build_db_path(tmp_path))
    major = db.insert_major('Economics')
    assert major['major'] == 'Economics'


def test_get_major_by_name(tmp_path):
    db = Database(build_db_path(tmp_path))
    assert db.get_major_by_name('Economics') is None

    major_inserted = db.insert_major('Economics')
    major = db.get_major_by_name('Economics')

    assert major_inserted == major
    assert db.get_major_by_name('Computer Science') is None


def test_insert_class_year(tmp_path):
    db = Database(build_db_path(tmp_path))
    class_year = db.insert_class_year(2022)
    assert class_year['class_year'] == 2022


def test_get_class_year_by_year(tmp_path):
    db = Database(build_db_path(tmp_path))
    assert db.get_class_year_by_year(2022) is None

    class_year_inserted = db.insert_class_year(2021)
    class_year = db.get_class_year_by_year(2021)

    assert class_year_inserted == class_year


def test_insert_tutor(tmp_path):
    db = Database(build_db_path(tmp_path))

    tutor = db.insert_tutor('Sommer1', 'cs232', 'Sommer', 100,
                            'Computer Science', 1)

    assert tutor['name'] == 'Sommer'
    assert tutor['age'] == 100
    assert tutor['area_of_expertise'] == 'Computer Science'
    assert tutor['cost'] == 1


def test_get_tutor_by_id(tmp_path):
    db = Database(build_db_path(tmp_path))
    assert db.get_tutor_by_id(1) is None

    tutor_inserted = db.insert_tutor('Sommer2', 'So2', 'Sommer', 100,
                                     'Computer Science', 1)
    tutor = db.get_tutor_by_id(1)

    assert tutor_inserted == tutor
    assert db.get_tutor_by_id(2) is None


def test_get_all_tutors(tmp_path):
    db = Database(build_db_path(tmp_path))
    assert db.get_all_tutors() == []

    tutor_inserted = db.insert_tutor('Visa2', 'Vi2', 'Visa', 90, 'English', 2)
    tutors_inserted = [tutor_inserted]

    tutors = db.get_all_tutors()
    assert len(tutors) == 1
    assert tutors[0] == tutor_inserted

    tutors_inserted.append(
        db.insert_tutor('Sommer2', 'So2', 'Sommer', 100, 'Computer Science',
                        1))

    tutors = db.get_all_tutors()

    assert len(tutors) == 2

    for tutor in tutors:
        assert tutor in tutors


def test_insert_student_tutor(tmp_path):
    db = Database(build_db_path(tmp_path))

    db.insert_student('Gungun', 'Gun2', 'Gunjan', 9, 2022, 'English')
    db.insert_student('Shawn22', 'The', 'Shawn', 21, 2022, 'English')
    db.insert_student('Alon22', 'Alon', 'Alon', 55, 2022, 'Computer Science')

    db.insert_tutor('Visa2', 'Vi2', 'Visa', 90, 'English', 2)
    db.insert_tutor('Sommer2', 'So2', 'Sommer', 20, 'Computer Science', 20)

    db.insert_student_tutor(1, 1)
    db.insert_student_tutor(2, 1)
    db.insert_student_tutor(3, 2)

    student_tutor = db.get_all_students()
    assert len(student_tutor) == 3


def test_get_students_from_tutor(tmp_path):
    db = Database(build_db_path(tmp_path))
    assert db.get_students_from_tutor(1) is None

    db.insert_student('Gungun', 'Gun2', 'Gunjan', 9, 2022, 'English')
    db.insert_student('Shawn22', 'The', 'Shawn', 21, 2022, 'English')
    db.insert_tutor('Visa2', 'Vi2', 'Visa', 90, 'English', 2)

    db.insert_student_tutor(1, 1)
    db.insert_student_tutor(2, 1)

    student_from_tutor = db.get_students_from_tutor(1)
    assert len(student_from_tutor) == 2


def test_get_tutor_from_student(tmp_path):
    db = Database(build_db_path(tmp_path))
    assert db.get_tutor_from_student(1) is None

    db.insert_student('Shawn22', 'The', 'Shawn', 21, 2022, 'English')
    db.insert_tutor('Visa2', 'Vi2', 'Visa', 90, 'English', 2)

    db.insert_student_tutor(1, 1)

    tutor_from_student = db.get_tutor_from_student(1)
    assert len(tutor_from_student) == 1


def test_search_tutor_id(tmp_path):
    db = Database(build_db_path(tmp_path))
    assert db.search_tutor_id(1) is False

    db.insert_tutor('Visa2', 'Vi2', 'Visa', 90, 'English', 2)

    assert db.search_tutor_id(1) is True


def test_search_student_id(tmp_path):
    db = Database(build_db_path(tmp_path))
    assert db.search_student_id(1) is False

    db.insert_student('Gungun', 'Gun2', 'Gunjan', 9, 2022, 'English')
    db.insert_student('Shawn22', 'The', 'Shawn', 21, 2022, 'English')

    assert db.search_student_id(2) is True
    assert db.search_student_id(3) is False


def test_tutor_is_hired(tmp_path):
    db = Database(build_db_path(tmp_path))
    assert db.tutor_is_hired(1, 1) is False

    db.insert_student('Shawn22', 'The', 'Shawn', 21, 2022, 'English')
    db.insert_tutor('Visa2', 'Vi2', 'Visa', 90, 'English', 2)

    db.insert_student_tutor(1, 1)
    db.tutor_is_hired(1, 1)

    hired = db.get_tutor_from_student(1)
    assert len(hired) == 1


def test_delete_student_tutor(tmp_path):
    db = Database(build_db_path(tmp_path))

    inserted_student = db.insert_student('Shawn22', 'The', 'Shawn', 21, 2022,
                                         'English')
    inserted_tutor = db.insert_tutor('Visa2', 'Vi2', 'Visa', 90, 'English', 2)

    students = db.get_all_students()
    tutors = db.get_all_tutors()

    assert len(students) == 1
    assert len(tutors) == 1

    assert students[0] == inserted_student
    assert tutors[0] == inserted_tutor

    students = db.delete_student_tutor(1, 1)
    tutors = db.delete_student_tutor(1, 1)

    assert students is None
    assert tutors is None


def test_get_student_id(tmp_path):
    db = Database(build_db_path(tmp_path))
    assert db.get_student_id('Shawn22', 'The') is False

    db.insert_student('Shawn22', 'The', 'Shawn', 21, 'Economics', 20)
    student = db.get_student_id('Shawn22', 'The')
    assert student == 1


def test_get_tutor_id(tmp_path):
    db = Database(build_db_path(tmp_path))
    assert db.get_tutor_id('Sommer2', 'So2') == 0

    db.insert_tutor('Sommer2', 'So2', 'Sommer', 50, 'CS232', 20)
    tutor = db.get_tutor_id('Sommer2', 'So2')
    assert tutor == 1
