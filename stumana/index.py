from stumana import login
from flask import render_template, url_for, jsonify
from admin import *
from flask_login import login_user, logout_user, login_required


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/user_login', methods=['get', 'post'])
def user_login():
    error_msg = ""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method.__eq__('POST'):
        try:
            username = request.form['username']
            password = request.form['password']

            user = utilities.check_login(username=username, password=password)
            if user:
                login_user(user=user)
                if current_user.user_role == UserRole.ADMIN:
                    return redirect('/admin')
                next = request.args.get('next', '/')
                return redirect(next)
            else:
                error_msg = "Sai tài khoản hoặc mật khẩu !!!"

        except Exception as ex:
            error_msg = str(ex)

    return render_template('login.html', error_msg=error_msg)


@app.route("/user_logout")
def user_logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/api/change-rule", methods=['POST'])
def change_rule():
    data = request.json
    min_age = data.get('min_age')
    max_age = data.get('max_age')
    max_size = data.get('max_size')

    result1 = utilities.change_chk_age(min=min_age, max=max_age)
    result2 = utilities.change_max_size(max=max_size)
    if result1 or result2:
        return jsonify({'status': 404})

    return jsonify({'status': 200})


@app.route("/arrange-class")
def arrange_class():
    grade12 = utilities.get_classes_by_grade(grade='12')
    grade11 = utilities.get_classes_by_grade(grade='11')
    grade10 = utilities.get_classes_by_grade(grade='10')
    select_class = request.args.get('class')
    id_this_class = ''
    if select_class:
        this_class = select_class.split('-')
        id_this_class = utilities.get_class_id(grade=this_class[0], class_name=this_class[1])

    students = utilities.get_all_student()

    return render_template('arrange-class.html',
                           grade12=grade12,
                           grade11=grade11,
                           grade10=grade10,
                           class_id=id_this_class,
                           students=students)


@app.route("/api/update-class", methods=['POST'])
@login_required
def update_class():
    data = request.json
    student_id = data.get('student_id')
    classid = data.get('class_id')

    try:
        result = utilities.update_classes(student_id=student_id, class_id=classid)
    except Exception as e:
        print(e)
        return jsonify({'status': 404})

    return jsonify({'status': 200})


@app.route("/setup-class")
def setup_class():
    err_msg = ''
    total = ''
    grade12 = utilities.get_classes_by_grade(grade='12')
    grade11 = utilities.get_classes_by_grade(grade='11')
    grade10 = utilities.get_classes_by_grade(grade='10')
    select_class = request.args.get('class')
    if select_class:
        select_grade = select_class.split('-')
        select_class_name = select_class.split('-')
        students = utilities.get_student_by_class(grade=select_grade[0],
                                                  class_name=select_class_name[1])
        total = utilities.get_total(grade=select_grade[0],
                                    class_name=select_class_name[1])
        if students:
            return render_template('set-up.html',
                                   grade12=grade12,
                                   grade11=grade11,
                                   grade10=grade10,
                                   students=students,
                                   total=total)
        else:
            err_msg = 'Không có học sinh nào !!!'

    return render_template('set-up.html',
                           grade12=grade12,
                           grade11=grade11,
                           grade10=grade10,
                           total=total,
                           err_msg=err_msg)


@app.route("/students-marks")
@login_required
def students_marks():
    classes = utilities.get_classes_of_teacher(current_user.id)

    if current_user.user_role == UserRole.TEACHER:
        course_id = request.args.get('course_id')

        if course_id:
            course = utilities.get_course_info(course_id)
            marks = utilities.get_mark_by_course_id(course_id=course_id)
            return render_template("students-marks.html",
                                   marks=marks,
                                   course=course,
                                   classes=classes)
        return render_template("students-marks.html", classes=classes)
    else:
        return redirect("/")


@app.route("/students-marks/edit/<int:student_id>")
@login_required
def edit_marks(student_id):
    year = request.args.get('year')
    subject_id = request.args.get('subject_id')
    classes = utilities.get_classes_of_teacher(current_user.id)

    marks = utilities.get_marks_of_student(student_id=student_id,
                                           subject_id=subject_id,
                                           year=year)
    return render_template("student_marks.html", marks=marks, classes=classes)


@app.route("/api/update-mark", methods=['POST'])
@login_required
def update_marks():
    data = request.json
    subject_id = data.get('subject_id')
    student_id = data.get('student_id')
    year = data.get('year')
    mark15 = {
        '1': data.get('mark15_1'),
        '2': data.get('mark15_2')
    }
    mark45 = {
        '1': data.get('mark45_1'),
        '2': data.get('mark45_2')
    }
    final_mark = {
        '1': data.get('final_mark1'),
        '2': data.get('final_mark2')
    }

    try:
        result = utilities.update_marks(subject_id=subject_id,
                                        student_id=student_id,
                                        year=year,
                                        mark15=mark15,
                                        mark45=mark45,
                                        final_mark=final_mark)
    except Exception as e:
        print(e)
        return jsonify({'status': 404})

    return jsonify({'status': 200})


@login.user_loader
def user_load(user_id):
    return utilities.get_user_by_id(user_id=user_id)


@app.context_processor
def common_response():
    return {
        'UserRole': UserRole,
        'year': datetime.now().year
    }


if __name__ == '__main__':
    app.run(debug=True)
