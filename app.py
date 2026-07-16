import streamlit as st
import pandas as pd
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def sign_up_user(email, password):
    return supabase.auth.sign_up(
        {
            "email": email,
            "password": password,
        }
    )


def sign_in_user(email, password):
    return supabase.auth.sign_in_with_password(
        {
            "email": email,
            "password": password,
        }
    )


def sign_out_user():
    supabase.auth.sign_out()
    st.session_state.pop("user", None)
    st.session_state.pop("access_token", None)
    st.session_state.pop("refresh_token", None)

SKILL_OPTIONS = [
    "Listening",
    "Reading",
    "Speaking",
    "Writing",
    "Grammar",
    "Vocabulary",
    "Pronunciation",
]


def parse_skills_focus(value):
    if pd.isna(value) or str(value).strip() in ["", "[]", "None", "nan"]:
        return []

    if isinstance(value, list):
        return [skill for skill in value if skill in SKILL_OPTIONS]

    skills = [skill.strip() for skill in str(value).split(",")]
    return [skill for skill in skills if skill in SKILL_OPTIONS]

st.set_page_config(page_title="CourseKit", page_icon="📚")

def load_css(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        st.markdown(f"<style>{file.read()}</style>", unsafe_allow_html=True)


load_css("style.css")

def display_value(value, fallback="Not specified"):
    if pd.isna(value) or str(value).strip() == "":
        return fallback
    return value

def student_label(row):
    language_value = display_value(
        row["target_language"],
        "",
    )

    if language_value:
        language_label = t(
            LANGUAGE_TRANSLATION_KEYS.get(
                language_value,
                language_value,
            )
        )
    else:
        language_label = t("not_specified")

    level_label = display_value(
        row["level"],
        t("not_specified"),
    )

    return (
        f"{int(row['id'])} — {row['name']} "
        f"({language_label} {level_label})"
    )

def course_label(row):
    target_language_value = display_value(
        row["target_language"],
        "",
    )

    instruction_language_value = display_value(
        row["instruction_language"],
        "",
    )

    if target_language_value:
        target_language_label = t(
            LANGUAGE_TRANSLATION_KEYS.get(
                target_language_value,
                target_language_value,
            )
        )
    else:
        target_language_label = t("not_specified")

    if instruction_language_value:
        instruction_language_label = t(
            LANGUAGE_TRANSLATION_KEYS.get(
                instruction_language_value,
                instruction_language_value,
            )
        )
    else:
        instruction_language_label = t("not_specified")

    level_label = display_value(
        row["level"],
        t("not_specified"),
    )

    return (
        f"{int(row['id'])} — {row['title']} "
        f"({target_language_label} {level_label} · "
        f"{t('taught_in')} {instruction_language_label})"
    )

def show_auth_screen():
    st.title("CourseKit 📚")
    st.subheader("Sign in or create an account")

    auth_tab, signup_tab = st.tabs(["Sign in", "Sign up"])

    with auth_tab:
        with st.form("sign_in_form"):
            email = st.text_input("Email", key="sign_in_email")
            password = st.text_input("Password", type="password", key="sign_in_password")
            sign_in_submitted = st.form_submit_button("Sign in")

        if sign_in_submitted:
            if email.strip() == "" or password.strip() == "":
                st.error("Please enter your email and password.")
            else:
                try:
                    response = sign_in_user(email, password)

                    st.session_state["user"] = response.user
                    st.session_state["access_token"] = response.session.access_token
                    st.session_state["refresh_token"] = response.session.refresh_token

                    st.success("Signed in successfully!")
                    st.rerun()
                except Exception as error:
                    st.error(f"Sign in failed: {error}")

    with signup_tab:
        with st.form("sign_up_form"):
            email = st.text_input("Email", key="sign_up_email")
            password = st.text_input("Password", type="password", key="sign_up_password")
            sign_up_submitted = st.form_submit_button("Create account")

        if sign_up_submitted:
            if email.strip() == "" or password.strip() == "":
                st.error("Please enter your email and password.")
            elif len(password) < 6:
                st.error("Password should be at least 6 characters long.")
            else:
                try:
                    response = sign_up_user(email, password)

                    if response.session:
                        st.session_state["user"] = response.user
                        st.session_state["access_token"] = response.session.access_token
                        st.session_state["refresh_token"] = response.session.refresh_token

                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.success("Account created. Please check your email to confirm your account.")
                except Exception as error:
                    st.error(f"Sign up failed: {error}")

if "user" not in st.session_state:
    show_auth_screen()
    st.stop()

if "access_token" in st.session_state and "refresh_token" in st.session_state:
    try:
        supabase.auth.set_session(
            st.session_state["access_token"],
            st.session_state["refresh_token"]
        )
    except Exception:
        sign_out_user()
        st.warning("Your session expired. Please sign in again.")
        show_auth_screen()
        st.stop()

st.markdown(
"""
<div class="hero-card">
    <div class="hero-content">
        <div class="hero-main">
            <p class="eyebrow">Mini LMS · EdTech · Course Management</p>
            <h1>CourseKit 📚</h1>
            <p class="hero-text">
                A lightweight LMS for language teachers to manage courses, lessons,
                assignments, student skills, and learning progress.
            </p>
        </div>
        <div class="hero-features">
            <div class="feature-pill">Course planning</div>
            <div class="feature-pill">Lesson goals</div>
            <div class="feature-pill">Assignments</div>
            <div class="feature-pill">Skills tracking</div>
            <div class="feature-pill">Progress</div>
        </div>
    </div>
</div>
""",
unsafe_allow_html=True
)

TRANSLATIONS = {
    "English": {
        "interface_language": "Interface language",
        "signed_in_as": "Signed in as",
        "sign_out": "Sign out",
        "workspace": "Workspace",

        "dashboard": "Dashboard",
        "students": "Students",
        "student_profile": "Student Profile",
        "courses": "Courses",
        "lessons": "Lessons",
        "assignments": "Assignments",
        "progress": "Progress",
        "student_skills": "Student Skills",

        "assignment_status_overview": "Assignment status overview",
        "progress_status_overview": "Progress status overview",
        "no_assignments_yet": "No assignments yet.",
        "no_progress_records_yet": "No progress records yet.",

        "assigned": "Assigned",
        "submitted": "Submitted",
        "checked": "Checked",
        "needs_revision": "Needs revision",
        "completed": "Completed",
        "not_started": "Not started",
        "in_progress": "In progress",

        "student_list": "Student list",
        "search_by_student_name": "Search by student name",

        "filter_by_language": "Filter by language",
        "filter_by_level": "Filter by level",
        "filter_by_status": "Filter by status",
        "all": "All",

        "edit_student": "Edit student",
        "no_students_to_edit": "No students to edit.",
        "select_student_to_edit": "Select student to edit",
        "student_name": "Student name",
        "target_language": "Target language",
        "level": "Level",
        "status": "Status",
        "notes": "Notes",
        "save_student_changes": "Save student changes",
        "please_enter_student_name": "Please enter the student name.",
        "student_updated_successfully": "Student updated successfully!",

        "language_english": "English",
        "language_chinese": "Chinese",
        "language_russian": "Russian",
        "language_german": "German",
        "language_spanish": "Spanish",
        "language_other": "Other",

        "status_active": "Active",
        "status_paused": "Paused",
        "status_completed": "Completed",

        "add_new_student": "Add a new student",
        "language": "Language",
        "add_student": "Add student",
        "student_added_successfully": "Student added successfully!",

        "delete_student": "Delete student",
        "no_students_to_delete": "No students to delete.",
        "select_student_to_delete": "Select student to delete",
        "confirm_delete_student": (
            "I understand that this will also delete this student's "
            "assignments, progress records, and skills."
        ),
        "please_confirm_deletion": "Please confirm deletion first.",
        "student_deleted_successfully": (
            "Student and related records deleted successfully!"
        ),

        "no_students_yet": "No students yet. Please add a student first.",
        "select_student": "Select student",
        "basic_info": "Basic info",
        "student": "Student",
        "unknown_student": "Unknown student",
        "not_specified": "Not specified",
        "no_notes_yet": "No notes yet.",

        "skills_summary": "Skills summary",
        "no_skills_record": "No skills record for this student yet.",
        "average_score": "Average score",
        "strongest_skill": "Strongest skill",
        "needs_focus": "Needs focus",
        "full_skills_profile": "Full skills profile",

        "listening": "Listening",
        "reading": "Reading",
        "speaking": "Speaking",
        "writing": "Writing",
        "grammar": "Grammar",
        "vocabulary": "Vocabulary",
        "comments": "Comments",
        "no_comments_yet": "No comments yet.",

        "course_list": "Course list",
        "title": "Title",
        "taught_in": "Taught in",
        "add_new_course": "Add a new course",
        "course_title": "Course title",
        "instruction_language": "Instruction language",
        "course_level": "Course level",
        "course_description": "Course description",
        "add_course": "Add course",
        "please_enter_course_title": "Please enter the course title.",
        "course_added_successfully": "Course added successfully!",

        "edit_course": "Edit course",
        "no_courses_to_edit": "No courses to edit.",
        "select_course_to_edit": "Select course to edit",
        "save_course_changes": "Save course changes",
        "course_updated_successfully": "Course updated successfully!",

        "lesson_list": "Lesson list",
        "course": "Course",
        "date": "Date",
        "time": "Time",
        "minutes_short": "Min",

        "lesson_details": "Lesson details",
        "no_lessons_yet": "No lessons yet.",
        "unknown_course": "Unknown course",
        "start_time": "Start time",
        "duration": "Duration",
        "minutes": "minutes",
        "lesson_goal": "Lesson goal",
        "skills_focus": "Skills focus",
        "materials": "Materials",
        "materials_link": "Materials link",
        "open_resource": "Open resource",
        "homework_template": "Homework template",
        "homework_link": "Homework link",

        "add_new_lesson": "Add a new lesson",
        "add_course_before_lessons": "Please add a course before creating lessons.",
        "lesson_title": "Lesson title",
        "lesson_date": "Lesson date",
        "duration_minutes": "Duration, minutes",
        "materials_url": "Materials URL",
        "homework_url": "Homework URL",
        "add_lesson": "Add lesson",
        "please_enter_lesson_title": "Please enter the lesson title.",
        "lesson_added_successfully": "Lesson added successfully!",

        "edit_lesson": "Edit lesson",
        "no_lessons_to_edit": "No lessons to edit.",
        "select_lesson_to_edit": "Select lesson to edit",
        "save_lesson_changes": "Save lesson changes",
        "lesson_updated_successfully": "Lesson updated successfully!",

        "archive_lesson": "Archive lesson",
        "no_active_lessons_to_archive": "No active lessons to archive.",
        "select_lesson_to_archive": "Select lesson to archive",
        "confirm_archive_lesson": (
            "I understand that this lesson will be archived "
            "and hidden from active lesson lists."
        ),
        "please_confirm_archiving": "Please confirm archiving first.",
        "lesson_archived_successfully": "Lesson archived successfully!",

        "archived_lessons": "Archived lessons",
        "no_archived_lessons_yet": "No archived lessons yet.",

        "restore_lesson": "Restore lesson",
        "no_archived_lessons_to_restore": "No archived lessons to restore.",
        "select_lesson_to_restore": "Select lesson to restore",
        "confirm_restore_lesson": (
            "I understand that this lesson will be restored "
            "to active lesson lists."
        ),
        "please_confirm_restore": "Please confirm restore first.",
        "lesson_restored_successfully": "Lesson restored successfully!",

        "assignment_list": "Assignment list",
        "assignment_details": "Assignment details",
        "lesson": "Lesson",
        "evaluation": "Evaluation",
        "homework": "Homework",
        "teacher_comments": "Teacher comments",

        "unknown_lesson": "Unknown lesson",

        "add_new_assignment": "Add a new assignment",
        "add_student_before_assignments": (
            "Please add a student before creating assignments."
        ),
        "add_course_before_assignments": (
            "Please add a course before creating assignments."
        ),
        "add_lesson_before_assignments": (
            "Please add a lesson before creating assignments."
        ),
        "course_has_no_lessons": (
            "This course has no lessons yet. Please add a lesson first."
        ),

        "assignment_status": "Assignment status",
        "add_assignment": "Add assignment",
        "add_lesson_for_course_first": (
            "Please add a lesson for this course before creating an assignment."
        ),
        "please_enter_homework_task": "Please enter the homework task.",
        "assignment_added_successfully": "Assignment added successfully!",

        "not_evaluated": "Not evaluated",
        "excellent": "Excellent",
        "good": "Good",
        "satisfactory": "Satisfactory",
        "needs_improvement": "Needs improvement",

        "edit_assignment": "Edit assignment",
        "no_assignments_to_edit": "No assignments to edit.",
        "select_assignment_to_edit": "Select assignment to edit",
        "save_assignment_changes": "Save assignment changes",
        "assignment_updated_successfully": "Assignment updated successfully!",

        "delete_assignment": "Delete assignment",
        "no_assignments_to_delete": "No assignments to delete.",
        "select_assignment_to_delete": "Select assignment to delete",
        "confirm_delete_assignment": (
            "I understand that this assignment will be permanently deleted."
        ),
        "assignment_deleted_successfully": "Assignment deleted successfully!",

        "progress_overview": "Progress overview",
        "progress_details": "Progress details",
        "no_progress_records_yet": "No progress records yet.",
        "teacher_comment": "Teacher comment",

        "add_progress_record": "Add progress record",
        "add_student_before_progress": (
            "Please add a student before adding progress."
        ),
        "add_course_before_progress": (
            "Please add a course before adding progress."
        ),
        "add_lesson_before_progress": (
            "Please add a lesson before adding progress."
        ),
        "progress_status": "Progress status",
        "add_progress": "Add progress",
        "add_lesson_for_progress_first": (
            "Please add a lesson for this course before adding progress."
        ),
        "progress_added_successfully": "Progress added successfully!",

        "edit_progress_record": "Edit progress record",
        "no_progress_records_to_edit": "No progress records to edit.",
        "select_progress_record_to_edit": "Select progress record to edit",
        "save_progress_changes": "Save progress changes",
        "progress_updated_successfully": "Progress updated successfully!",

        "delete_progress_record": "Delete progress record",
        "no_progress_records_to_delete": "No progress records to delete.",
        "select_progress_record_to_delete": "Select progress record to delete",
        "confirm_delete_progress": (
            "I understand that this progress record will be permanently deleted."
        ),
        "progress_record_deleted_successfully": (
            "Progress record deleted successfully!"
        ),

        "skills_overview": "Skills overview",
        "skills_details": "Skills details",
        "no_skill_records_yet": "No skill records yet.",
        "skills_profile": "Skills profile",
        "average_skill_score": "Average skill score",

        "add_student_skills": "Add student skills",
        "add_student_before_skills": "Please add a student before adding skills.",
        "add_skills": "Add skills",
        "student_already_has_skills_profile": (
            "This student already has a skills profile."
        ),
        "student_skills_added_successfully": (
            "Student skills added successfully!"
        ),

        "edit_student_skills": "Edit student skills",
        "no_skills_records_to_edit": "No skills records to edit yet.",
        "select_skills_record_to_edit": "Select skills record to edit",
        "update_skills": "Update skills",
        "student_skills_updated_successfully": (
            "Student skills updated successfully!"
        ),

        "no_assignments_for_student": "No assignments for this student yet.",

        "assignment_assigned": "Assigned",
        "assignment_submitted": "Submitted",
        "assignment_checked": "Checked",
        "assignment_needs_revision": "Needs revision",
        "assignment_completed": "Completed",

        "no_progress_for_student": "No progress records for this student yet.",

        "progress_not_started": "Not started",
        "progress_in_progress": "In progress",
        "progress_completed": "Completed",

        "no_courses_yet": "No courses yet.",
    },

    "Русский": {
        "interface_language": "Язык интерфейса",
        "signed_in_as": "Вы вошли как",
        "sign_out": "Выйти",
        "workspace": "Разделы",

        "dashboard": "Главная",
        "students": "Ученики",
        "student_profile": "Профиль ученика",
        "courses": "Курсы",
        "lessons": "Уроки",
        "assignments": "Домашние задания",
        "progress": "Прогресс",
        "student_skills": "Навыки учеников",

        "assignment_status_overview": "Статусы домашних заданий",
        "progress_status_overview": "Статусы прогресса",
        "no_assignments_yet": "Домашних заданий пока нет.",
        "no_progress_records_yet": "Записей о прогрессе пока нет.",

        "assigned": "Задано",
        "submitted": "Сдано",
        "checked": "Проверено",
        "needs_revision": "Требует доработки",
        "completed": "Завершено",
        "not_started": "Не начато",
        "in_progress": "В процессе",

        "student_list": "Список учеников",
        "search_by_student_name": "Поиск по имени ученика",

        "filter_by_language": "Фильтр по языку",
        "filter_by_level": "Фильтр по уровню",
        "filter_by_status": "Фильтр по статусу",
        "all": "Все",

        "edit_student": "Редактировать ученика",
        "no_students_to_edit": "Нет учеников для редактирования.",
        "select_student_to_edit": "Выберите ученика",
        "student_name": "Имя ученика",
        "target_language": "Изучаемый язык",
        "level": "Уровень",
        "status": "Статус",
        "notes": "Заметки",
        "save_student_changes": "Сохранить изменения",
        "please_enter_student_name": "Введите имя ученика.",
        "student_updated_successfully": "Данные ученика успешно обновлены!",

        "language_english": "Английский",
        "language_chinese": "Китайский",
        "language_russian": "Русский",
        "language_german": "Немецкий",
        "language_spanish": "Испанский",
        "language_other": "Другой",

        "status_active": "Активен",
        "status_paused": "Приостановлен",
        "status_completed": "Завершён",

        "add_new_student": "Добавить нового ученика",
        "language": "Язык",
        "add_student": "Добавить ученика",
        "student_added_successfully": "Ученик успешно добавлен!",

        "delete_student": "Удалить ученика",
        "no_students_to_delete": "Нет учеников для удаления.",
        "select_student_to_delete": "Выберите ученика для удаления",
        "confirm_delete_student": (
            "Я понимаю, что вместе с учеником будут удалены его домашние задания, "
            "записи о прогрессе и навыки."
        ),
        "please_confirm_deletion": "Сначала подтвердите удаление.",
        "student_deleted_successfully": (
            "Ученик и связанные с ним записи успешно удалены!"
        ),

        "no_students_yet": "Учеников пока нет. Сначала добавьте ученика.",
        "select_student": "Выберите ученика",
        "basic_info": "Основная информация",
        "student": "Ученик",
        "unknown_student": "Неизвестный ученик",
        "not_specified": "Не указано",
        "no_notes_yet": "Заметок пока нет.",

        "skills_summary": "Обзор навыков",
        "no_skills_record": "Для этого ученика пока нет записей о навыках.",
        "average_score": "Средний балл",
        "strongest_skill": "Самый сильный навык",
        "needs_focus": "Требует внимания",
        "full_skills_profile": "Полный профиль навыков",

        "listening": "Аудирование",
        "reading": "Чтение",
        "speaking": "Говорение",
        "writing": "Письмо",
        "grammar": "Грамматика",
        "vocabulary": "Лексика",
        "comments": "Комментарии",
        "no_comments_yet": "Комментариев пока нет.",

        "course_list": "Список курсов",
        "title": "Название",
        "taught_in": "Язык преподавания",
        "add_new_course": "Добавить новый курс",
        "course_title": "Название курса",
        "instruction_language": "Язык преподавания",
        "course_level": "Уровень курса",
        "course_description": "Описание курса",
        "add_course": "Добавить курс",
        "please_enter_course_title": "Введите название курса.",
        "course_added_successfully": "Курс успешно добавлен!",

        "edit_course": "Редактировать курс",
        "no_courses_to_edit": "Нет курсов для редактирования.",
        "select_course_to_edit": "Выберите курс для редактирования",
        "save_course_changes": "Сохранить изменения курса",
        "course_updated_successfully": "Курс успешно обновлён!",

        "lesson_list": "Список уроков",
        "course": "Курс",
        "date": "Дата",
        "time": "Время",
        "minutes_short": "Мин.",

        "lesson_details": "Информация об уроках",
        "no_lessons_yet": "Уроков пока нет.",
        "unknown_course": "Неизвестный курс",
        "start_time": "Время начала",
        "duration": "Продолжительность",
        "minutes": "минут",
        "lesson_goal": "Цель урока",
        "skills_focus": "Основные навыки",
        "materials": "Материалы",
        "materials_link": "Ссылка на материалы",
        "open_resource": "Открыть ресурс",
        "homework_template": "Шаблон домашнего задания",
        "homework_link": "Ссылка на домашнее задание",

        "add_new_lesson": "Добавить новый урок",
        "add_course_before_lessons": "Сначала добавьте курс, а затем создавайте уроки.",
        "lesson_title": "Название урока",
        "lesson_date": "Дата урока",
        "duration_minutes": "Продолжительность, минуты",
        "materials_url": "Ссылка на материалы",
        "homework_url": "Ссылка на домашнее задание",
        "add_lesson": "Добавить урок",
        "please_enter_lesson_title": "Введите название урока.",
        "lesson_added_successfully": "Урок успешно добавлен!",

        "edit_lesson": "Редактировать урок",
        "no_lessons_to_edit": "Нет уроков для редактирования.",
        "select_lesson_to_edit": "Выберите урок для редактирования",
        "save_lesson_changes": "Сохранить изменения урока",
        "lesson_updated_successfully": "Урок успешно обновлён!",

        "archive_lesson": "Архивировать урок",
        "no_active_lessons_to_archive": "Нет активных уроков для архивации.",
        "select_lesson_to_archive": "Выберите урок для архивации",
        "confirm_archive_lesson": (
            "Я понимаю, что урок будет перенесён в архив "
            "и скрыт из списка активных уроков."
        ),
        "please_confirm_archiving": "Сначала подтвердите архивацию.",
        "lesson_archived_successfully": "Урок успешно архивирован!",

        "archived_lessons": "Архивные уроки",
        "no_archived_lessons_yet": "В архиве пока нет уроков.",

        "restore_lesson": "Восстановить урок",
        "no_archived_lessons_to_restore": "Нет архивных уроков для восстановления.",
        "select_lesson_to_restore": "Выберите урок для восстановления",
        "confirm_restore_lesson": (
            "Я понимаю, что урок будет восстановлен "
            "и снова появится в списке активных уроков."
        ),
        "please_confirm_restore": "Сначала подтвердите восстановление.",
        "lesson_restored_successfully": "Урок успешно восстановлен!",

        "assignment_list": "Список домашних заданий",
        "assignment_details": "Информация о домашних заданиях",
        "lesson": "Урок",
        "evaluation": "Оценка",
        "homework": "Домашнее задание",
        "teacher_comments": "Комментарии преподавателя",

        "unknown_lesson": "Неизвестный урок",

        "add_new_assignment": "Добавить новое домашнее задание",
        "add_student_before_assignments": (
            "Сначала добавьте ученика, а затем создавайте домашние задания."
        ),
        "add_course_before_assignments": (
            "Сначала добавьте курс, а затем создавайте домашние задания."
        ),
        "add_lesson_before_assignments": (
            "Сначала добавьте урок, а затем создавайте домашние задания."
        ),
        "course_has_no_lessons": (
            "В этом курсе пока нет уроков. Сначала добавьте урок."
        ),

        "assignment_status": "Статус домашнего задания",
        "add_assignment": "Добавить домашнее задание",
        "add_lesson_for_course_first": (
            "Сначала добавьте урок для этого курса."
        ),
        "please_enter_homework_task": "Введите задание.",
        "assignment_added_successfully": "Домашнее задание успешно добавлено!",

        "not_evaluated": "Не оценено",
        "excellent": "Отлично",
        "good": "Хорошо",
        "satisfactory": "Удовлетворительно",
        "needs_improvement": "Требует улучшения",

        "edit_assignment": "Редактировать домашнее задание",
        "no_assignments_to_edit": "Нет домашних заданий для редактирования.",
        "select_assignment_to_edit": "Выберите домашнее задание",
        "save_assignment_changes": "Сохранить изменения",
        "assignment_updated_successfully": "Домашнее задание успешно обновлено!",

        "delete_assignment": "Удалить домашнее задание",
        "no_assignments_to_delete": "Нет домашних заданий для удаления.",
        "select_assignment_to_delete": "Выберите домашнее задание для удаления",
        "confirm_delete_assignment": (
            "Я понимаю, что это домашнее задание будет удалено безвозвратно."
        ),
        "assignment_deleted_successfully": "Домашнее задание успешно удалено!",

        "progress_overview": "Обзор прогресса",
        "progress_details": "Информация о прогрессе",
        "no_progress_records_yet": "Записей о прогрессе пока нет.",
        "teacher_comment": "Комментарий преподавателя",

        "add_progress_record": "Добавить запись о прогрессе",
        "add_student_before_progress": (
            "Сначала добавьте ученика, а затем создавайте записи о прогрессе."
        ),
        "add_course_before_progress": (
            "Сначала добавьте курс, а затем создавайте записи о прогрессе."
        ),
        "add_lesson_before_progress": (
            "Сначала добавьте урок, а затем создавайте записи о прогрессе."
        ),
        "progress_status": "Статус прогресса",
        "add_progress": "Добавить прогресс",
        "add_lesson_for_progress_first": (
            "Сначала добавьте урок для этого курса."
        ),
        "progress_added_successfully": "Запись о прогрессе успешно добавлена!",

        "edit_progress_record": "Редактировать запись о прогрессе",
        "no_progress_records_to_edit": "Нет записей о прогрессе для редактирования.",
        "select_progress_record_to_edit": "Выберите запись о прогрессе",
        "save_progress_changes": "Сохранить изменения",
        "progress_updated_successfully": "Запись о прогрессе успешно обновлена!",

        "delete_progress_record": "Удалить запись о прогрессе",
        "no_progress_records_to_delete": "Нет записей о прогрессе для удаления.",
        "select_progress_record_to_delete": "Выберите запись о прогрессе для удаления",
        "confirm_delete_progress": (
            "Я понимаю, что эта запись о прогрессе будет удалена безвозвратно."
        ),
        "progress_record_deleted_successfully": (
            "Запись о прогрессе успешно удалена!"
        ),

        "skills_overview": "Обзор навыков",
        "skills_details": "Информация о навыках",
        "no_skill_records_yet": "Записей о навыках пока нет.",
        "skills_profile": "Профиль навыков",
        "average_skill_score": "Средний балл навыков",

        "add_student_skills": "Добавить навыки ученика",
        "add_student_before_skills": (
            "Сначала добавьте ученика, а затем добавляйте навыки."
        ),
        "add_skills": "Добавить навыки",
        "student_already_has_skills_profile": (
            "У этого ученика уже есть профиль навыков."
        ),
        "student_skills_added_successfully": (
            "Навыки ученика успешно добавлены!"
        ),

        "edit_student_skills": "Редактировать навыки ученика",
        "no_skills_records_to_edit": (
            "Пока нет записей о навыках для редактирования."
        ),
        "select_skills_record_to_edit": (
            "Выберите профиль навыков для редактирования"
        ),
        "update_skills": "Обновить навыки",
        "student_skills_updated_successfully": (
            "Навыки ученика успешно обновлены!"
        ),

        "no_assignments_for_student": "У этого ученика пока нет домашних заданий.",

        "assignment_assigned": "Назначено",
        "assignment_submitted": "Сдано",
        "assignment_checked": "Проверено",
        "assignment_needs_revision": "Требует доработки",
        "assignment_completed": "Выполнено",

        "no_progress_for_student": "У этого ученика пока нет записей о прогрессе.",

        "progress_not_started": "Не начато",
        "progress_in_progress": "В процессе",
        "progress_completed": "Завершено",

        "no_courses_yet": "Курсов пока нет.",
    },

    "中文": {
        "interface_language": "界面语言",
        "signed_in_as": "当前登录账号",
        "sign_out": "退出登录",
        "workspace": "功能区",

        "dashboard": "首页",
        "students": "学生",
        "student_profile": "学生档案",
        "courses": "课程",
        "lessons": "课时",
        "assignments": "作业",
        "progress": "学习进度",

        "progress_overview": "学习进度概览",
        "progress_details": "学习进度详情",
        "no_progress_records_yet": "暂无学习进度记录。",
        "teacher_comment": "教师评语",

        "add_progress_record": "添加学习进度记录",
        "add_student_before_progress": "请先添加学生，再添加学习进度。",
        "add_course_before_progress": "请先添加课程，再添加学习进度。",
        "add_lesson_before_progress": "请先添加课时，再添加学习进度。",
        "progress_status": "学习进度状态",
        "add_progress": "添加学习进度",
        "add_lesson_for_progress_first": "请先为该课程添加课时。",
        "progress_added_successfully": "学习进度添加成功！",

        "edit_progress_record": "编辑学习进度记录",
        "no_progress_records_to_edit": "暂无可编辑的学习进度记录。",
        "select_progress_record_to_edit": "选择要编辑的学习进度记录",
        "save_progress_changes": "保存学习进度修改",
        "progress_updated_successfully": "学习进度更新成功！",

        "delete_progress_record": "删除学习进度记录",
        "no_progress_records_to_delete": "暂无可删除的学习进度记录。",
        "select_progress_record_to_delete": "选择要删除的学习进度记录",
        "confirm_delete_progress": "我明白，该学习进度记录将被永久删除。",
        "progress_record_deleted_successfully": "学习进度记录删除成功！",

        "student_skills": "学生技能",

        "skills_details": "技能详情",
        "no_skill_records_yet": "暂无技能记录。",

        "add_student_skills": "添加学生技能",
        "add_student_before_skills": "请先添加学生，再添加技能。",
        "add_skills": "添加技能",
        "student_already_has_skills_profile": "该学生已有技能档案。",
        "student_skills_added_successfully": "学生技能添加成功！",

        "edit_student_skills": "编辑学生技能",
        "no_skills_records_to_edit": "暂无可编辑的技能记录。",
        "select_skills_record_to_edit": "选择要编辑的技能记录",
        "update_skills": "更新技能",
        "student_skills_updated_successfully": "学生技能更新成功！",

        "assignment_status_overview": "作业状态概览",
        "progress_status_overview": "学习进度概览",
        "no_assignments_yet": "暂无作业。",
        "no_progress_records_yet": "暂无学习进度记录。",

        "assigned": "已布置",
        "submitted": "已提交",
        "checked": "已批改",
        "needs_revision": "需要修改",
        "completed": "已完成",
        "not_started": "未开始",
        "in_progress": "进行中",

        "student_list": "学生列表",
        "search_by_student_name": "按学生姓名搜索",

        "filter_by_language": "按语言筛选",
        "filter_by_level": "按级别筛选",
        "filter_by_status": "按状态筛选",
        "all": "全部",

        "edit_student": "编辑学生",
        "no_students_to_edit": "暂无可编辑的学生。",
        "select_student_to_edit": "选择要编辑的学生",
        "student_name": "学生姓名",
        "target_language": "目标语言",
        "level": "级别",
        "status": "状态",
        "notes": "备注",
        "save_student_changes": "保存学生信息",
        "please_enter_student_name": "请输入学生姓名。",
        "student_updated_successfully": "学生信息更新成功！",

        "language_english": "英语",
        "language_chinese": "中文",
        "language_russian": "俄语",
        "language_german": "德语",
        "language_spanish": "西班牙语",
        "language_other": "其他",

        "status_active": "学习中",
        "status_paused": "已暂停",
        "status_completed": "已完成",

        "add_new_student": "添加新学生",
        "language": "语言",
        "add_student": "添加学生",
        "student_added_successfully": "学生添加成功！",

        "delete_student": "删除学生",
        "no_students_to_delete": "暂无可删除的学生。",
        "select_student_to_delete": "选择要删除的学生",
        "confirm_delete_student": (
            "我明白，删除该学生时，其作业、学习进度记录和技能记录也会被删除。"
        ),
        "please_confirm_deletion": "请先确认删除。",
        "student_deleted_successfully": "学生及相关记录已成功删除！",

        "no_students_yet": "暂无学生。请先添加学生。",
        "select_student": "选择学生",
        "basic_info": "基本信息",
        "student": "学生",
        "unknown_student": "未知学生",
        "not_specified": "未填写",
        "no_notes_yet": "暂无备注。",

        "skills_summary": "技能概览",
        "no_skills_record": "该学生暂无技能记录。",
        "average_score": "平均分",
        "strongest_skill": "最强技能",
        "needs_focus": "需要加强",
        "full_skills_profile": "完整技能档案",

        "listening": "听力",
        "reading": "阅读",
        "speaking": "口语",
        "writing": "写作",
        "grammar": "语法",
        "vocabulary": "词汇",
        "comments": "评语",
        "no_comments_yet": "暂无评语。",

        "course_list": "课程列表",
        "title": "课程名称",
        "taught_in": "授课语言",
        "add_new_course": "添加新课程",
        "course_title": "课程名称",
        "instruction_language": "授课语言",
        "course_level": "课程级别",
        "course_description": "课程描述",
        "add_course": "添加课程",
        "please_enter_course_title": "请输入课程名称。",
        "course_added_successfully": "课程添加成功！",

        "edit_course": "编辑课程",
        "no_courses_to_edit": "暂无可编辑的课程。",
        "select_course_to_edit": "选择要编辑的课程",
        "save_course_changes": "保存课程修改",
        "course_updated_successfully": "课程更新成功！",

        "lesson_list": "课时列表",
        "course": "课程",
        "date": "日期",
        "time": "时间",
        "minutes_short": "分钟",

        "lesson_details": "课时详情",
        "no_lessons_yet": "暂无课时。",
        "unknown_course": "未知课程",
        "start_time": "开始时间",
        "duration": "时长",
        "minutes": "分钟",
        "lesson_goal": "课时目标",
        "skills_focus": "重点技能",
        "materials": "材料",
        "materials_link": "材料链接",
        "open_resource": "打开资源",
        "homework_template": "作业模板",
        "homework_link": "作业链接",

        "add_new_lesson": "添加新课时",
        "add_course_before_lessons": "请先添加课程，再创建课时。",
        "lesson_title": "课时名称",
        "lesson_date": "课时日期",
        "duration_minutes": "时长（分钟）",
        "materials_url": "材料链接",
        "homework_url": "作业链接",
        "add_lesson": "添加课时",
        "please_enter_lesson_title": "请输入课时名称。",
        "lesson_added_successfully": "课时添加成功！",

        "edit_lesson": "编辑课时",
        "no_lessons_to_edit": "暂无可编辑的课时。",
        "select_lesson_to_edit": "选择要编辑的课时",
        "save_lesson_changes": "保存课时修改",
        "lesson_updated_successfully": "课时更新成功！",

        "archive_lesson": "归档课时",
        "no_active_lessons_to_archive": "暂无可归档的课时。",
        "select_lesson_to_archive": "选择要归档的课时",
        "confirm_archive_lesson": (
            "我明白，该课时将被归档，"
            "并从当前课时列表中隐藏。"
        ),
        "please_confirm_archiving": "请先确认归档。",
        "lesson_archived_successfully": "课时归档成功！",

        "archived_lessons": "已归档课时",
        "no_archived_lessons_yet": "暂无已归档课时。",

        "restore_lesson": "恢复课时",
        "no_archived_lessons_to_restore": "暂无可恢复的已归档课时。",
        "select_lesson_to_restore": "选择要恢复的课时",
        "confirm_restore_lesson": (
            "我明白，该课时将被恢复，"
            "并重新显示在当前课时列表中。"
        ),
        "please_confirm_restore": "请先确认恢复。",
        "lesson_restored_successfully": "课时恢复成功！",

        "assignment_list": "作业列表",
        "assignment_details": "作业详情",
        "lesson": "课时",
        "evaluation": "评价",
        "homework": "作业内容",
        "teacher_comments": "教师评语",

        "unknown_lesson": "未知课时",

        "add_new_assignment": "添加新作业",
        "add_student_before_assignments": (
            "请先添加学生，再创建作业。"
        ),
        "add_course_before_assignments": (
            "请先添加课程，再创建作业。"
        ),
        "add_lesson_before_assignments": (
            "请先添加课时，再创建作业。"
        ),
        "course_has_no_lessons": (
            "该课程暂无课时。请先添加课时。"
        ),

        "assignment_status": "作业状态",
        "add_assignment": "添加作业",
        "add_lesson_for_course_first": (
            "请先为该课程添加课时。"
        ),
        "please_enter_homework_task": "请输入作业内容。",
        "assignment_added_successfully": "作业添加成功！",

        "not_evaluated": "未评价",
        "excellent": "优秀",
        "good": "良好",
        "satisfactory": "合格",
        "needs_improvement": "需要改进",

        "edit_assignment": "编辑作业",
        "no_assignments_to_edit": "暂无可编辑的作业。",
        "select_assignment_to_edit": "选择要编辑的作业",
        "save_assignment_changes": "保存作业修改",
        "assignment_updated_successfully": "作业更新成功！",

        "delete_assignment": "删除作业",
        "no_assignments_to_delete": "暂无可删除的作业。",
        "select_assignment_to_delete": "选择要删除的作业",
        "confirm_delete_assignment": "我明白，该作业将被永久删除。",
        "assignment_deleted_successfully": "作业删除成功！",
    },

    "edit_assignment": "编辑作业",
    "no_assignments_to_edit": "暂无可编辑的作业。",
    "select_assignment_to_edit": "选择要编辑的作业",
    "save_assignment_changes": "保存作业修改",
    "assignment_updated_successfully": "作业更新成功！",

    "delete_assignment": "删除作业",
    "no_assignments_to_delete": "暂无可删除的作业。",
    "select_assignment_to_delete": "选择要删除的作业",
    "confirm_delete_assignment": (
        "我明白，该作业将被永久删除。"
    ),
    "assignment_deleted_successfully": "作业删除成功！",

    "progress_overview": "学习进度概览",
    "progress_details": "学习进度详情",
    "no_progress_records_yet": "暂无学习进度记录。",
    "teacher_comment": "教师评语",

    "add_progress_record": "添加学习进度记录",
    "add_student_before_progress": (
        "请先添加学生，再添加学习进度。"
    ),
    "add_course_before_progress": (
        "请先添加课程，再添加学习进度。"
    ),
    "add_lesson_before_progress": (
        "请先添加课时，再添加学习进度。"
    ),
    "progress_status": "学习进度状态",
    "add_progress": "添加学习进度",
    "add_lesson_for_progress_first": (
        "请先为该课程添加课时。"
    ),
    "progress_added_successfully": "学习进度添加成功！",

    "edit_progress_record": "编辑学习进度记录",
    "no_progress_records_to_edit": "暂无可编辑的学习进度记录。",
    "select_progress_record_to_edit": "选择要编辑的学习进度记录",
    "save_progress_changes": "保存学习进度修改",
    "progress_updated_successfully": "学习进度更新成功！",

    "delete_progress_record": "删除学习进度记录",
    "no_progress_records_to_delete": "暂无可删除的学习进度记录。",
    "select_progress_record_to_delete": "选择要删除的学习进度记录",
    "confirm_delete_progress": (
        "我明白，该学习进度记录将被永久删除。"
    ),
    "progress_record_deleted_successfully": (
        "学习进度记录删除成功！"
    ),

    "skills_overview": "技能概览",
    "skills_details": "技能详情",
    "no_skill_records_yet": "暂无技能记录。",
    "skills_profile": "技能档案",
    "average_skill_score": "技能平均分",

    "add_student_skills": "添加学生技能",
    "add_student_before_skills": (
        "请先添加学生，再添加技能。"
    ),
    "add_skills": "添加技能",
    "student_already_has_skills_profile": (
        "该学生已有技能档案。"
    ),
    "student_skills_added_successfully": (
        "学生技能添加成功！"
    ),

    "edit_student_skills": "编辑学生技能",
    "no_skills_records_to_edit": "暂无可编辑的技能记录。",
    "select_skills_record_to_edit": "选择要编辑的技能记录",
    "update_skills": "更新技能",
    "student_skills_updated_successfully": (
        "学生技能更新成功！"
    ),

    "no_assignments_for_student": "该学生暂无作业。",

    "assignment_assigned": "已布置",
    "assignment_submitted": "已提交",
    "assignment_checked": "已检查",
    "assignment_needs_revision": "需要修改",
    "assignment_completed": "已完成",

    "no_progress_for_student": "该学生暂无学习进度记录。",

    "progress_not_started": "未开始",
    "progress_in_progress": "进行中",
    "progress_completed": "已完成",

     "no_courses_yet": "暂时还没有课程。",
}


LANGUAGE_TRANSLATION_KEYS = {
    "English": "language_english",
    "Chinese": "language_chinese",
    "Russian": "language_russian",
    "German": "language_german",
    "Spanish": "language_spanish",
    "Other": "language_other",
}

STUDENT_STATUS_TRANSLATION_KEYS = {
    "active": "status_active",
    "paused": "status_paused",
    "completed": "status_completed",
}

ASSIGNMENT_STATUS_TRANSLATION_KEYS = {
    "assigned": "assignment_assigned",
    "submitted": "assignment_submitted",
    "checked": "assignment_checked",
    "needs revision": "assignment_needs_revision",
    "completed": "assignment_completed",
}

EVALUATION_TRANSLATION_KEYS = {
    "not evaluated": "not_evaluated",
    "excellent": "excellent",
    "good": "good",
    "satisfactory": "satisfactory",
    "needs improvement": "needs_improvement",
}

PROGRESS_STATUS_TRANSLATION_KEYS = {
    "not started": "progress_not_started",
    "in progress": "progress_in_progress",
    "completed": "progress_completed",
}

def t(key):
    language = st.session_state.get("interface_language", "English")

    return TRANSLATIONS.get(
        language,
        TRANSLATIONS["English"],
    ).get(
        key,
        TRANSLATIONS["English"].get(key, key),
    )

TABLE_COLUMNS = {
    "students": ["id", "user_id", "name", "target_language", "level", "status", "notes"],
    "courses": ["id", "user_id", "title", "target_language", "instruction_language", "level", "description"],
    "lessons": [
        "id",
        "user_id",
        "course_id",
        "title",
        "lesson_date",
        "start_time",
        "duration_minutes",
        "lesson_goal",
        "skills_focus",
        "materials",
        "materials_url",
        "homework_template",
        "homework_url",
        "is_archived",
    ],
    "assignments": [
        "id",
        "user_id",
        "student_id",
        "course_id",
        "lesson_id",
        "homework",
        "status",
        "evaluation",
        "comments",
    ],
    "progress": [
        "id",
        "user_id",
        "student_id",
        "course_id",
        "lesson_id",
        "status",
        "teacher_comment",
    ],
    "student_skills": [
        "id",
        "user_id",
        "student_id",
        "listening",
        "reading",
        "speaking",
        "writing",
        "grammar",
        "vocabulary",
        "comments",
    ],
}

def load_table(table_name):
    user_id = st.session_state["user"].id

    response = (
        supabase.table(table_name)
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    data = response.data or []
    return pd.DataFrame(data, columns=TABLE_COLUMNS[table_name])


students = load_table("students")
courses = load_table("courses")
lessons = load_table("lessons")
assignments = load_table("assignments")
progress = load_table("progress")
student_skills = load_table("student_skills")

if "is_archived" not in lessons.columns:
    lessons["is_archived"] = False

lessons["is_archived"] = lessons["is_archived"].astype(str).str.lower().isin(["true", "1", "yes"])

if "lesson_date" not in lessons.columns:
    lessons["lesson_date"] = ""

if "start_time" not in lessons.columns:
    lessons["start_time"] = ""

if "duration_minutes" not in lessons.columns:
    lessons["duration_minutes"] = 60

if "materials_url" not in lessons.columns:
    lessons["materials_url"] = ""

if "homework_url" not in lessons.columns:
    lessons["homework_url"] = ""

# Normalize ID columns after reading CSV files
for df in [students, courses, lessons, assignments, student_skills, progress]:
    if "id" in df.columns and not df.empty:
        df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")

if "student_id" in assignments.columns and not assignments.empty:
    assignments["student_id"] = pd.to_numeric(assignments["student_id"], errors="coerce").astype("Int64")

if "course_id" in assignments.columns and not assignments.empty:
    assignments["course_id"] = pd.to_numeric(assignments["course_id"], errors="coerce").astype("Int64")

if "lesson_id" in assignments.columns and not assignments.empty:
    assignments["lesson_id"] = pd.to_numeric(assignments["lesson_id"], errors="coerce").astype("Int64")

if "student_id" in progress.columns and not progress.empty:
    progress["student_id"] = pd.to_numeric(progress["student_id"], errors="coerce").astype("Int64")

if "course_id" in progress.columns and not progress.empty:
    progress["course_id"] = pd.to_numeric(progress["course_id"], errors="coerce").astype("Int64")

if "lesson_id" in progress.columns and not progress.empty:
    progress["lesson_id"] = pd.to_numeric(progress["lesson_id"], errors="coerce").astype("Int64")

if "student_id" in student_skills.columns and not student_skills.empty:
    student_skills["student_id"] = pd.to_numeric(student_skills["student_id"], errors="coerce").astype("Int64")

if "course_id" in lessons.columns and not lessons.empty:
    lessons["course_id"] = pd.to_numeric(lessons["course_id"], errors="coerce").astype("Int64")

active_lessons = lessons[lessons["is_archived"] == False].copy()

# Normalize text columns
for column in ["title", "target_language", "instruction_language", "level", "description"]:
    if column in courses.columns:
        courses[column] = courses[column].astype("object")

for column in ["name", "target_language", "level", "status", "notes"]:
    if column in students.columns:
        students[column] = students[column].astype("object")

for column in [
    "title",
    "lesson_date",
    "start_time",
    "lesson_goal",
    "skills_focus",
    "materials",
    "materials_url",
    "homework_template",
    "homework_url",
]:
    if column in lessons.columns:
        lessons[column] = lessons[column].astype("object")

for column in ["homework", "status", "evaluation", "comments"]:
    if column in assignments.columns:
        assignments[column] = assignments[column].astype("object")

for column in ["status", "teacher_comment"]:
    if column in progress.columns:
        progress[column] = progress[column].astype("object")

for column in ["comments"]:
    if column in student_skills.columns:
        student_skills[column] = student_skills[column].astype("object")
for column in ["title", "lesson_date", "start_time", "lesson_goal", "skills_focus", "materials", "homework_template"]:
    if column in lessons.columns:
        lessons[column] = lessons[column].astype("object")

# Normalize text columns
for column in ["title", "lesson_date", "start_time", "lesson_goal", "skills_focus", "materials", "homework_template"]:
    if column in lessons.columns:
        lessons[column] = lessons[column].astype("object")

# Normalize numeric lesson columns
if "duration_minutes" in lessons.columns and not lessons.empty:
    lessons["duration_minutes"] = pd.to_numeric(
        lessons["duration_minutes"],
        errors="coerce"
    ).fillna(60).astype(int)

current_user = st.session_state["user"]
user_id = current_user.id

st.sidebar.title("CourseKit")

st.sidebar.selectbox(
    t("interface_language"),
    ["English", "Русский", "中文"],
    key="interface_language",
)

st.sidebar.caption(
    f"{t('signed_in_as')}: {current_user.email}"
)

if st.sidebar.button(t("sign_out")):
    sign_out_user()
    st.rerun()


PAGE_TRANSLATION_KEYS = {
    "Dashboard": "dashboard",
    "Students": "students",
    "Student Profile": "student_profile",
    "Courses": "courses",
    "Lessons": "lessons",
    "Assignments": "assignments",
    "Progress": "progress",
    "Student Skills": "student_skills",
}


page = st.sidebar.radio(
    t("workspace"),
    list(PAGE_TRANSLATION_KEYS.keys()),
    format_func=lambda page_name: t(
        PAGE_TRANSLATION_KEYS[page_name]
    ),
)

# if page == "Dashboard":

#     st.subheader("Dashboard")

#     col1, col2, col3, col4, col5 = st.columns(5)
    
#     col1.metric("Students", len(students))
#     col2.metric("Courses", len(courses))
#     col3.metric("Lessons", len(active_lessons))
#     col4.metric("Assignments", len(assignments))
#     col5.metric("Progress", len(progress))

#     st.subheader("Assignment status overview")

#     if assignments.empty:
#         st.info("No assignments yet.")
#     else:
#         status_counts = assignments["status"].value_counts()

#         col1, col2, col3, col4, col5 = st.columns(5)

#         col1.metric("Assigned", int(status_counts.get("assigned", 0)))
#         col2.metric("Submitted", int(status_counts.get("submitted", 0)))
#         col3.metric("Checked", int(status_counts.get("checked", 0)))
#         col4.metric("Needs revision", int(status_counts.get("needs revision", 0)))
#         col5.metric("Completed", int(status_counts.get("completed", 0)))
    
#     st.subheader("Progress status overview")

#     if progress.empty:
#         st.info("No progress records yet.")
#     else:
#         progress_status_counts = progress["status"].value_counts()

#         col1, col2, col3 = st.columns(3)

#         col1.metric("Not started", int(progress_status_counts.get("not started", 0)))
#         col2.metric("In progress", int(progress_status_counts.get("in progress", 0)))
#         col3.metric("Completed", int(progress_status_counts.get("completed", 0)))

if page == "Dashboard":

    st.subheader(t("dashboard"))

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(t("students"), len(students))
    col2.metric(t("courses"), len(courses))
    col3.metric(t("lessons"), len(active_lessons))
    col4.metric(t("assignments"), len(assignments))
    col5.metric(t("progress"), len(progress))

    st.subheader(t("assignment_status_overview"))

    if assignments.empty:
        st.info(t("no_assignments_yet"))

    else:
        status_counts = assignments["status"].value_counts()

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            t("assigned"),
            int(status_counts.get("assigned", 0)),
        )
        col2.metric(
            t("submitted"),
            int(status_counts.get("submitted", 0)),
        )
        col3.metric(
            t("checked"),
            int(status_counts.get("checked", 0)),
        )
        col4.metric(
            t("needs_revision"),
            int(status_counts.get("needs_revision", 0)),
        )
        col5.metric(
            t("completed"),
            int(status_counts.get("completed", 0)),
        )

    st.subheader(t("progress_status_overview"))

    if progress.empty:
        st.info(t("no_progress_records_yet"))

    else:
        progress_status_counts = progress["status"].value_counts()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            t("not_started"),
            int(progress_status_counts.get("not_started", 0)),
        )
        col2.metric(
            t("in_progress"),
            int(progress_status_counts.get("in_progress", 0)),
        )
        col3.metric(
            t("completed"),
            int(progress_status_counts.get("completed", 0)),
        )

elif page == "Students":

    st.header(t("students"))

    st.subheader(t("student_list"))

    filtered_students = students.copy()

    search_name = st.text_input(
        t("search_by_student_name"),
        key="student_search",
    )

    # language_options = (
    #     students["target_language"]
    #     .dropna()
    #     .astype(str)
    #     .str.strip()
    # )

    # language_filter = st.selectbox(
    #     "Filter by language",
    #     ["All"] + language_options,
    #     key="student_language_filter"
    # )
    
    # level_filter = st.selectbox(
    #     "Filter by level",
    #     ["All"] + sorted(students["level"].dropna().unique().tolist()),
    #     key="student_level_filter"
    # )
    
    # status_filter = st.selectbox(
    #     "Filter by status",
    #     ["All"] + sorted(students["status"].dropna().unique().tolist()),
    #     key="student_status_filter"
    # )

    language_options = sorted(
    students["target_language"]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
    .tolist()
    )

    language_filter = st.selectbox(
        t("filter_by_language"),
        ["All"] + language_options,
        format_func=lambda value: t("all") if value == "All" else value,
        key="student_language_filter",
    )

    level_options = sorted(
        students["level"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    level_filter = st.selectbox(
        t("filter_by_level"),
        ["All"] + level_options,
        format_func=lambda value: t("all") if value == "All" else value,
        key="student_level_filter",
    )

    status_options = sorted(
        students["status"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    status_filter = st.selectbox(
        t("filter_by_status"),
        ["All"] + status_options,
        format_func=lambda value: t("all") if value == "All" else value,
        key="student_status_filter",
    )
    
    if search_name.strip():
        filtered_students = filtered_students[
            filtered_students["name"].str.contains(search_name, case=False, na=False)
        ]
    
    if language_filter != "All":
        filtered_students = filtered_students[
            filtered_students["target_language"] == language_filter
        ]
    
    if level_filter != "All":
        filtered_students = filtered_students[
            filtered_students["level"] == level_filter
        ]
    
    if status_filter != "All":
        filtered_students = filtered_students[
            filtered_students["status"] == status_filter
        ]

    students_view = filtered_students.copy()

    students_view["target_language"] = students_view["target_language"].apply(
        lambda value: t(
            LANGUAGE_TRANSLATION_KEYS.get(value, value)
        )
        if not pd.isna(value) and str(value).strip() != ""
        else t("not_specified")
    )

    students_view["level"] = students_view["level"].apply(
        lambda value: display_value(value, t("not_specified"))
    )

    students_view["status"] = students_view["status"].apply(
        lambda value: t(
            STUDENT_STATUS_TRANSLATION_KEYS.get(value, value)
        )
        if not pd.isna(value) and str(value).strip() != ""
        else t("not_specified")
    )

    students_view["notes"] = students_view["notes"].apply(
        lambda value: display_value(value, t("no_notes"))
    )

    students_view = students_view[
        ["name", "target_language", "level", "status", "notes"]
    ]

    st.dataframe(
        students_view,
        width="stretch",
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn(
                t("student_name"),
                width="medium",
            ),
            "target_language": st.column_config.TextColumn(
                t("target_language"),
                width="medium",
            ),
            "level": st.column_config.TextColumn(
                t("level"),
                width="small",
            ),
            "status": st.column_config.TextColumn(
                t("status"),
                width="small",
            ),
            "notes": st.column_config.TextColumn(
                t("notes"),
                width="large",
            ),
        }
    )
    
    st.subheader(t("add_new_student"))

    with st.form("add_student_form"):
        name = st.text_input(t("student_name"))

        language_options = [
            "English",
            "Chinese",
            "Russian",
            "German",
            "Spanish",
            "Other",
        ]

        language = st.selectbox(
            t("language"),
            language_options,
            format_func=lambda value: t(
                LANGUAGE_TRANSLATION_KEYS[value]
            ),
        )

        level = st.selectbox(
            t("level"),
            ["A1", "A2", "B1", "B2", "C1", "C2"],
        )

        student_status_options = [
            "active",
            "paused",
            "completed",
        ]

        status = st.selectbox(
            t("status"),
            student_status_options,
            format_func=lambda value: t(
                STUDENT_STATUS_TRANSLATION_KEYS[value]
            ),
        )

        notes = st.text_area(t("notes"))

        submitted = st.form_submit_button(
            t("add_student")
        )

        if submitted:
            if name.strip() == "":
                st.error(t("please_enter_student_name"))
            else:
                new_student = {
                    "user_id": user_id,
                    "name": name,
                    "target_language": language,
                    "level": level,
                    "status": status,
                    "notes": notes,
                }

                supabase.table("students").insert(new_student).execute()

                st.success(t("student_added_successfully"))
                st.rerun()

    # st.subheader("Edit student")
    
    # if students.empty:
    #     st.info("No students to edit.")
    
    # else:

    #     edit_student_options = {
    #         student_label(row): int(row["id"])
    #         for _, row in students.iterrows()
    #     }
        
    #     selected_student_to_edit = st.selectbox(
    #         "Select student to edit",
    #         list(edit_student_options.keys()),
    #         key="edit_student_select"
    #     )

    st.subheader(t("edit_student"))

    if students.empty:
        st.info(t("no_students_to_edit"))

    else:
        edit_student_options = {
            student_label(row): int(row["id"])
            for _, row in students.iterrows()
        }

        selected_student_to_edit = st.selectbox(
            t("select_student_to_edit"),
            list(edit_student_options.keys()),
            key="edit_student_select",
        )
            
        student_id_to_edit = edit_student_options[selected_student_to_edit]
        
        student_row = students[
            students["id"].astype(int) == int(student_id_to_edit)
        ].iloc[0]
        
        with st.form("edit_student_form"):
            edited_name = st.text_input(
                t("student_name"),
                value=student_row["name"],
            )

            student_target_language = display_value(student_row["target_language"], "Other")

            language_options = ["English", "Chinese", "Russian", "German", "Spanish", "Other"]

            # edited_target_language = st.selectbox(
            #     "Target language",
            #     language_options,
            #     index=language_options.index(student_target_language)
            #     if student_target_language in language_options
            #     else language_options.index("Other")
            # )

            edited_target_language = st.selectbox(
                t("target_language"),
                language_options,
                index=(
                    language_options.index(student_target_language)
                    if student_target_language in language_options
                    else language_options.index("Other")
                ),
                format_func=lambda value: t(
                    LANGUAGE_TRANSLATION_KEYS.get(value, value)
                ),
            )

            # edited_level = st.selectbox(
            #     "Level",
            #     ["A1", "A2", "B1", "B2", "C1", "C2"],
            #     index=["A1", "A2", "B1", "B2", "C1", "C2"].index(student_row["level"])
            #     if student_row["level"] in ["A1", "A2", "B1", "B2", "C1", "C2"]
            #     else 0
            # )

            edited_level = st.selectbox(
                t("level"),
                ["A1", "A2", "B1", "B2", "C1", "C2"],
                index=(
                    ["A1", "A2", "B1", "B2", "C1", "C2"].index(
                        student_row["level"]
                    )
                    if student_row["level"] in [
                        "A1",
                        "A2",
                        "B1",
                        "B2",
                        "C1",
                        "C2",
                    ]
                    else 0
                ),
            )

            student_status_options = [
                "active",
                "paused",
                "completed",
            ]

            edited_status = st.selectbox(
                t("status"),
                student_status_options,
                index=(
                    student_status_options.index(student_row["status"])
                    if student_row["status"] in student_status_options
                    else 0
                ),
                format_func=lambda value: t(
                    STUDENT_STATUS_TRANSLATION_KEYS.get(value, value)
                ),
            )

            current_notes = student_row["notes"]

            if pd.isna(current_notes):
                current_notes = ""

            edited_notes = st.text_area(
                t("notes"),
                value=current_notes
            )

            edit_student_submitted = st.form_submit_button(
                t("save_student_changes")
            )

        if edit_student_submitted:
            if edited_name.strip() == "":
                st.error(t("please_enter_student_name"))
            else:
                updated_student = {
                    "name": edited_name,
                    "target_language": edited_target_language,
                    "level": edited_level,
                    "status": edited_status,
                    "notes": edited_notes,
                }

                supabase.table("students").update(updated_student).eq(
                    "id",
                    int(student_id_to_edit)
                ).eq(
                    "user_id",
                    user_id
                ).execute()

                st.success(t("student_updated_successfully"))
                st.rerun()

    # st.subheader(t("delete_student"))
    
    # if students.empty:
    #     st.info(t("no_students_to_delete"))
    # else:

    #     delete_student_options = {
    #         student_label(row): int(row["id"])
    #         for _, row in students.iterrows()
    #     }
        
    #     with st.form("delete_student_form"):
    #         student_to_delete = st.selectbox(
    #             student_to_delete = st.selectbox(
    #             t("select_student_to_delete"),
    #             list(delete_student_options.keys()),
    #             key="delete_student_select",
    #         )
    #         )

    #         confirm_delete_student = st.checkbox(
    #             t("confirm_delete_student")
    #             "I understand that this will also delete this student's assignments, progress records, and skills."
    #         )
            
    #         delete_student_submitted = st.form_submit_button(
    #             t("delete_student")
    #         )
                        
    #         if delete_student_submitted:
    #             if not confirm_delete_student:
    #                 st.error("Please confirm deletion first.")
    #             else:
    #                 student_id_to_delete = delete_student_options[student_to_delete]

    st.subheader(t("delete_student"))

    if students.empty:
        st.info(t("no_students_to_delete"))
    else:
        delete_student_options = {
            student_label(row): int(row["id"])
            for _, row in students.iterrows()
        }

        with st.form("delete_student_form"):
            student_to_delete = st.selectbox(
                t("select_student_to_delete"),
                list(delete_student_options.keys()),
                key="delete_student_select",
            )

            confirm_delete_student = st.checkbox(
                t("confirm_delete_student")
            )

            delete_student_submitted = st.form_submit_button(
                t("delete_student")
            )

            if delete_student_submitted:
                if not confirm_delete_student:
                    st.error(t("please_confirm_deletion"))
                else:
                    student_id_to_delete = delete_student_options[
                        student_to_delete
                    ]

                    supabase.table("assignments").delete().eq(
                        "student_id",
                        int(student_id_to_delete)
                    ).eq(
                        "user_id",
                        user_id
                    ).execute()

                    supabase.table("progress").delete().eq(
                        "student_id",
                        int(student_id_to_delete)
                    ).eq(
                        "user_id",
                        user_id
                    ).execute()

                    supabase.table("student_skills").delete().eq(
                        "student_id",
                        int(student_id_to_delete)
                    ).eq(
                        "user_id",
                        user_id
                    ).execute()

                    supabase.table("students").delete().eq(
                        "id",
                        int(student_id_to_delete)
                    ).eq(
                        "user_id",
                        user_id
                    ).execute()

                    st.success(t("student_deleted_successfully"))
                    st.rerun()

elif page == "Student Profile":
    st.header(t("student_profile"))

    if students.empty:
        st.info(t("no_students_yet"))
    else:
        student_options = {
            student_label(row): int(row["id"])
            for _, row in students.iterrows()
        }

        selected_student = st.selectbox(
            t("select_student"),
            list(student_options.keys()),
            key="profile_student_select",
        )

        selected_student_id = student_options[selected_student]

        student_row = students[
            students["id"].astype(int) == int(selected_student_id)
        ].iloc[0]

        st.subheader(t("basic_info"))

        col1, col2, col3 = st.columns(3)

        col1.metric(
            t("student"),
            display_value(student_row["name"], t("unknown_student")),
        )
        
        student_language = student_row["target_language"]

        if pd.isna(student_language) or str(student_language).strip() == "":
            student_language_label = t("not_specified")
        else:
            student_language_label = t(
                LANGUAGE_TRANSLATION_KEYS.get(
                    student_language,
                    student_language,
                )
            )

        col2.metric(
            t("target_language"),
            student_language_label,
        )

        col3.metric(
            t("level"),
            display_value(student_row["level"], t("not_specified")),
        )

        student_status = display_value(
            student_row["status"],
            "",
        )

        if student_status:
            student_status_label = t(
                STUDENT_STATUS_TRANSLATION_KEYS.get(
                    student_status,
                    student_status,
                )
            )
        else:
            student_status_label = t("not_specified")

        st.write(
            f"**{t('status')}:** {student_status_label}"
        )

        notes = student_row["notes"]

        if pd.isna(notes) or str(notes).strip() == "":
            notes = t("no_notes_yet")

        st.write(
            f"**{t('notes')}:** {notes}"
        )

        st.subheader(t("skills_summary"))

        student_skill_records = student_skills[
            student_skills["student_id"].astype(int) == int(selected_student_id)
        ]

        if student_skill_records.empty:
            st.info(t("no_skills_record"))
        else:
            latest_skills = student_skill_records.iloc[-1]

            skill_columns = ["listening", "reading", "speaking", "writing", "grammar", "vocabulary"]

            scores = {
                skill: latest_skills[skill]
                for skill in skill_columns
            }

            average_score = sum(scores.values()) / len(scores)
            strongest_skill = max(scores, key=scores.get)
            weakest_skill = min(scores, key=scores.get)

            col1, col2, col3 = st.columns(3)

            col1.metric(
                t("average_score"),
                f"{average_score:.1f} / 5",
            )

            col2.metric(
                t("strongest_skill"),
                t(strongest_skill),
            )

            col3.metric(
                t("needs_focus"),
                t(weakest_skill),
            )

            with st.expander(t("full_skills_profile")):
                st.write(
                    f"**{t('listening')}:** "
                    f"{latest_skills['listening']} / 5"
                )
                st.write(
                    f"**{t('reading')}:** "
                    f"{latest_skills['reading']} / 5"
                )
                st.write(
                    f"**{t('speaking')}:** "
                    f"{latest_skills['speaking']} / 5"
                )
                st.write(
                    f"**{t('writing')}:** "
                    f"{latest_skills['writing']} / 5"
                )
                st.write(
                    f"**{t('grammar')}:** "
                    f"{latest_skills['grammar']} / 5"
                )
                st.write(
                    f"**{t('vocabulary')}:** "
                    f"{latest_skills['vocabulary']} / 5"
                )

                skill_comments = latest_skills["comments"]

                if pd.isna(skill_comments) or str(skill_comments).strip() == "":
                    skill_comments = t("no_comments_yet")

                st.write(
                    f"**{t('comments')}:** {skill_comments}"
                )

        st.subheader(t("assignments"))

        student_assignments = assignments[
            assignments["student_id"].astype(int) == int(selected_student_id)
        ]

        if student_assignments.empty:
            st.info(t("no_assignments_for_student"))
        else:
            course_titles = dict(zip(courses["id"], courses["title"]))
            lesson_titles = dict(zip(lessons["id"], lessons["title"]))

            student_assignments_view = student_assignments.copy()

            student_assignments_view["course"] = student_assignments_view["course_id"].map(course_titles)
            student_assignments_view["lesson"] = student_assignments_view["lesson_id"].map(lesson_titles)

            student_assignments_view["course"] = student_assignments_view["course"].apply(
                lambda value: display_value(value, t("unknown_course"))
            )

            student_assignments_view["lesson"] = student_assignments_view["lesson"].apply(
                lambda value: display_value(value, t("unknown_lesson"))
            )

            student_assignments_view["status"] = student_assignments_view["status"].apply(
                lambda value: t(
                    ASSIGNMENT_STATUS_TRANSLATION_KEYS.get(
                        value,
                        value,
                    )
                )
                if not pd.isna(value) and str(value).strip() != ""
                else t("not_specified")
            )

            student_assignments_view["evaluation"] = student_assignments_view["evaluation"].apply(
                lambda value: t(
                    EVALUATION_TRANSLATION_KEYS.get(
                        value,
                        value,
                    )
                )
                if not pd.isna(value) and str(value).strip() != ""
                else t("not_evaluated")
            )

            student_assignments_view = student_assignments_view[
                ["lesson", "status", "evaluation"]
            ]

            st.dataframe(
                student_assignments_view,
                width="stretch",
                hide_index=True,
                column_config={
                    "lesson": st.column_config.TextColumn(
                        t("lesson"),
                        width="large",
                    ),
                    "status": st.column_config.TextColumn(
                        t("status"),
                        width="medium",
                    ),
                    "evaluation": st.column_config.TextColumn(
                        t("evaluation"),
                        width="medium",
                    ),
                }
            )

            with st.expander(t("assignment_details")):
                for _, row in student_assignments.iterrows():
                    course_name = course_titles.get(row["course_id"], "Unknown course")
                    lesson_name = lesson_titles.get(row["lesson_id"], "Unknown lesson")

                    comments = row["comments"]
                    if pd.isna(comments) or str(comments).strip() == "":
                        comments = "No comments yet."

                    assignment_status_label = t(
                        ASSIGNMENT_STATUS_TRANSLATION_KEYS.get(
                            row["status"],
                            row["status"],
                        )
                    )

                    evaluation_label = t(
                        EVALUATION_TRANSLATION_KEYS.get(
                            row["evaluation"],
                            row["evaluation"],
                        )
                    )

                    assignment_comments = row["comments"]

                    if pd.isna(assignment_comments) or str(assignment_comments).strip() == "":
                        assignment_comments = t("no_comments_yet")

                    st.write(f"### {lesson_name}")
                
                    st.write(
                        f"**{t('course')}:** {course_name}"
                    )

                    st.write(
                        f"**{t('homework')}:** {row['homework']}"
                    )

                    st.write(
                        f"**{t('status')}:** {assignment_status_label}"
                    )

                    st.write(
                        f"**{t('evaluation')}:** {evaluation_label}"
                    )

                    st.write(
                        f"**{t('teacher_comments')}:** {assignment_comments}"
                    )

        st.subheader(t("progress"))

        student_progress = progress[
            progress["student_id"].astype(int) == int(selected_student_id)
        ]

        if student_progress.empty:
            st.info(t("no_progress_for_student"))
        else:
            course_titles = dict(zip(courses["id"], courses["title"]))
            lesson_titles = dict(zip(lessons["id"], lessons["title"]))

            st.subheader("Course progress summary")

            student_course_ids = student_progress["course_id"].dropna().astype(int).unique()

            for course_id in student_course_ids:
                course_lessons = lessons[
                    lessons["course_id"].astype(int) == int(course_id)
                ]

                course_progress = student_progress[
                    student_progress["course_id"].astype(int) == int(course_id)
                ]

                completed_lessons = course_progress[
                    course_progress["status"] == "completed"
                ]

                total_lessons_count = len(course_lessons)
                completed_lessons_count = len(completed_lessons)

                if total_lessons_count == 0:
                    progress_ratio = 0
                else:
                    progress_ratio = completed_lessons_count / total_lessons_count

                course_name = course_titles.get(course_id, "Unknown course")

                st.write(f"**{course_name}**")
                st.write(f"{completed_lessons_count} / {total_lessons_count} lessons completed")
                st.progress(progress_ratio)
            
            student_progress_rows = []

            student_course_ids = student_progress["course_id"].dropna().astype(int).unique()

            for course_id in student_course_ids:
                course_lessons = active_lessons[
                active_lessons["course_id"].astype(int) == int(course_id)
                ]

                for _, lesson_row in course_lessons.iterrows():
                    lesson_id = int(lesson_row["id"])

                    matching_progress = student_progress[
                        student_progress["lesson_id"].astype(int) == lesson_id
                    ]

                    if matching_progress.empty:
                        lesson_status = "not started"
                    else:
                        lesson_status = matching_progress.iloc[-1]["status"]

                    student_progress_rows.append(
                        {
                            "course": course_titles.get(course_id, "Unknown course"),
                             "lesson": lesson_row["title"],
                             "status": lesson_status,
                        }
                    )

                student_progress_view = pd.DataFrame(student_progress_rows)

                st.dataframe(
                    student_progress_view[["lesson", "status"]],
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "lesson": st.column_config.TextColumn("Lesson", width="large"),
                        "status": st.column_config.TextColumn("Status", width="medium"),
                    }
                )

            with st.expander("Progress details"):
                for _, row in student_progress.iterrows():
                    course_name = course_titles.get(row["course_id"], "Unknown course")
                    lesson_name = lesson_titles.get(row["lesson_id"], "Unknown lesson")

                    teacher_comment = row["teacher_comment"]
                    if pd.isna(teacher_comment) or str(teacher_comment).strip() == "":
                        teacher_comment = "No comments yet."

                    st.write(f"### {lesson_name}")
                    st.write(f"**Course:** {course_name}")
                    st.write(f"**Status:** {row['status']}")
                    st.write(f"**Teacher comment:** {teacher_comment}")

elif page == "Courses":
    st.header(t("courses"))
    st.subheader(t("course_list"))

    courses_view = courses.copy()

    if courses_view.empty:
        st.info(t("no_courses_yet"))

    else:
        courses_view["target_language"] = courses_view["target_language"].apply(
            lambda value: t(
                LANGUAGE_TRANSLATION_KEYS.get(
                    value,
                    value,
                )
            )
            if not pd.isna(value) and str(value).strip() != ""
            else t("not_specified")
        )

        courses_view["instruction_language"] = courses_view["instruction_language"].apply(
            lambda value: t(
                LANGUAGE_TRANSLATION_KEYS.get(
                    value,
                    value,
                )
            )
            if not pd.isna(value) and str(value).strip() != ""
            else t("not_specified")
        )

        courses_view = courses_view[
            ["title", "target_language", "instruction_language", "level"]
        ]

        st.dataframe(
            courses_view,
            width="stretch",
            hide_index=True,
            column_config={
                "title": st.column_config.TextColumn(
                    t("title"),
                    width="large",
                ),
                "target_language": st.column_config.TextColumn(
                    t("target_language"),
                    width="medium",
                ),
                "instruction_language": st.column_config.TextColumn(
                    t("taught_in"),
                    width="large",
                ),
                "level": st.column_config.TextColumn(
                    t("level"),
                    width="small",
                ),
            },
        )
    
    st.subheader(t("add_new_course"))

    with st.form("add_course_form"):
        title = st.text_input(t("course_title"))

        course_language_options = [
            "English",
            "Chinese",
            "Russian",
            "German",
            "Spanish",
            "Other",
        ]

        course_language = st.selectbox(
            t("target_language"),
            course_language_options,
            format_func=lambda value: t(
                LANGUAGE_TRANSLATION_KEYS[value]
            ),
        )

        instruction_language = st.selectbox(
            t("instruction_language"),
            course_language_options,
            format_func=lambda value: t(
                LANGUAGE_TRANSLATION_KEYS[value]
            ),
        )

        course_level = st.selectbox(
            t("course_level"),
            ["A1", "A2", "B1", "B2", "C1", "C2"],
            key="course_level",
        )

        description = st.text_area(
            t("course_description")
        )

        course_submitted = st.form_submit_button(
            t("add_course")
        )

        if course_submitted:
            if title.strip() == "":
                st.error(t("please_enter_course_title"))
            else:
                new_course = {
                    "user_id": user_id,
                    "title": title,
                    "target_language": course_language,
                    "instruction_language": instruction_language,
                    "level": course_level,
                    "description": description,
                }

                supabase.table("courses").insert(new_course).execute()

                st.success(t("course_added_successfully"))
                st.rerun()
    
    st.subheader(t("edit_course"))

    if courses.empty:
        st.info(t("no_courses_to_edit"))
    else:
        edit_course_options = {}

        for _, row in courses.iterrows():
            target_language_label = t(
                LANGUAGE_TRANSLATION_KEYS.get(
                    row["target_language"],
                    row["target_language"],
                )
            )

            instruction_language_label = t(
                LANGUAGE_TRANSLATION_KEYS.get(
                    row["instruction_language"],
                    row["instruction_language"],
                )
            )

            label = (
                f"{row['id']} – {row['title']} "
                f"({target_language_label} {row['level']} "
                f"· {t('taught_in')} {instruction_language_label})"
            )

            edit_course_options[label] = int(row["id"])

        selected_course_to_edit = st.selectbox(
            t("select_course_to_edit"),
            list(edit_course_options.keys()),
            key="edit_course_select",
        )

        course_id_to_edit = edit_course_options[selected_course_to_edit]

        course_row = courses[
            courses["id"].astype(int) == int(course_id_to_edit)
        ].iloc[0]

        language_options = ["English", "Chinese", "Russian", "German", "Spanish", "Other"]
        level_options = ["A1", "A2", "B1", "B2", "C1", "C2"]

        with st.form("edit_course_form"):
            edited_title = st.text_input(
                t("course_title"),
                value=course_row["title"],
            )

            edited_target_language = st.selectbox(
                t("target_language"),
                language_options,
                index=(
                    language_options.index(course_row["target_language"])
                    if course_row["target_language"] in language_options
                    else 5
                ),
                format_func=lambda value: t(
                    LANGUAGE_TRANSLATION_KEYS[value]
                ),
            )

            edited_instruction_language = st.selectbox(
                t("instruction_language"),
                language_options,
                index=(
                    language_options.index(course_row["instruction_language"])
                    if course_row["instruction_language"] in language_options
                    else 5
                ),
                format_func=lambda value: t(
                    LANGUAGE_TRANSLATION_KEYS[value]
                ),
            )

            edited_level = st.selectbox(
                t("course_level"),
                level_options,
                index=level_options.index(course_row["level"])
                if course_row["level"] in level_options
                else 0,
                key="edit_course_level",
            )

            current_description = course_row["description"]

            if pd.isna(current_description):
                current_description = ""

            edited_description = st.text_area(
                t("course_description"),
                value=current_description,
            )

            edit_course_submitted = st.form_submit_button(
                t("save_course_changes")
            )

            if edit_course_submitted:
                if edited_title.strip() == "":
                    st.error(t("please_enter_course_title"))
                else:
                    updated_course = {
                        "title": edited_title,
                        "target_language": edited_target_language,
                        "instruction_language": edited_instruction_language,
                        "level": edited_level,
                        "description": edited_description,
                    }

                    supabase.table("courses").update(updated_course).eq(
                        "id",
                        int(course_id_to_edit)
                    ).eq(
                        "user_id",
                        user_id
                    ).execute()

                    st.success(t("course_updated_successfully"))
                    st.rerun()

elif page == "Lessons":

    st.header(t("lessons"))

    st.subheader(t("lesson_list"))

    lessons_view = active_lessons.copy()

    if lessons_view.empty:
        st.info(t("no_lessons_yet"))

    elif courses.empty:
        st.info(t("no_courses_yet"))

    else:
        course_titles = dict(zip(courses["id"], courses["title"]))

        lessons_view["course"] = lessons_view["course_id"].map(course_titles)

        lessons_view = lessons_view[
            ["course", "title", "lesson_date", "start_time", "duration_minutes"]
        ]

        st.dataframe(
            lessons_view,
            width="stretch",
            hide_index=True,
            column_config={
                "course": st.column_config.TextColumn(
                    t("course"),
                    width="medium",
                ),
                "title": st.column_config.TextColumn(
                    t("title"),
                    width="large",
                ),
                "lesson_date": st.column_config.TextColumn(
                    t("date"),
                    width="small",
                ),
                "start_time": st.column_config.TextColumn(
                    t("time"),
                    width="small",
                ),
                "duration_minutes": st.column_config.NumberColumn(
                    t("minutes_short"),
                    width="small",
                ),
            },
        )
    
    st.subheader(t("lesson_details"))
    
    if lessons.empty:
        st.info(t("no_lessons_yet"))
    else:
        course_titles = dict(zip(courses["id"], courses["title"]))

        for _, row in lessons.iterrows():
            course_name = course_titles.get(
                row["course_id"],
                t("unknown_course"),
            )
            
            with st.expander(f"{row['title']}"):
                st.write(
                    f"**{t('course')}:** {course_name}"
                )

                st.write(
                    f"**{t('date')}:** {row['lesson_date']}"
                )

                st.write(
                    f"**{t('start_time')}:** {row['start_time']}"
                )

                st.write(
                    f"**{t('duration')}:** "
                    f"{row['duration_minutes']} {t('minutes')}"
                )

                st.write(
                    f"**{t('lesson_goal')}:** {row['lesson_goal']}"
                )

                st.write(
                    f"**{t('skills_focus')}:** {row['skills_focus']}"
                )

                st.write(
                    f"**{t('materials')}:** {row['materials']}"
                )

                materials_url = row["materials_url"]

                if not pd.isna(materials_url) and str(materials_url).strip() != "":
                    st.markdown(
                        f"**{t('materials_link')}:** "
                        f"[{t('open_resource')}]({materials_url})"
                    )

                st.write(
                    f"**{t('homework_template')}:** "
                    f"{row['homework_template']}"
                )

                homework_url = row["homework_url"]

                if not pd.isna(homework_url) and str(homework_url).strip() != "":
                    st.markdown(
                        f"**{t('homework_link')}:** "
                        f"[{t('open_resource')}]({homework_url})"
                    )

    st.subheader(t("add_new_lesson"))
    
    if courses.empty:
        st.warning(t("add_course_before_lessons"))
    else:
        course_options = {}

        for _, row in courses.iterrows():
            target_language_label = t(
                LANGUAGE_TRANSLATION_KEYS.get(
                    row["target_language"],
                    row["target_language"],
                )
            )

            instruction_language_label = t(
                LANGUAGE_TRANSLATION_KEYS.get(
                    row["instruction_language"],
                    row["instruction_language"],
                )
            )

            label = (
                f"{row['id']} – {row['title']} "
                f"({target_language_label} {row['level']} "
                f"· {t('taught_in')} {instruction_language_label})"
            )

            course_options[label] = int(row["id"])
        
        with st.form("add_lesson_form"):
            selected_course = st.selectbox(
                t("course"),
                list(course_options.keys()),
            )
            title = st.text_input(t("lesson_title"))
            lesson_date = st.date_input(t("lesson_date"))

            start_time = st.time_input(t("start_time"))
            
            duration_minutes = st.number_input(
                t("duration_minutes"),
                min_value=15,
                max_value=240,
                value=60,
                step=15,
            )

            lesson_goal = st.text_area(t("lesson_goal"))
            skill_options = [
                "listening",
                "reading",
                "speaking",
                "writing",
                "grammar",
                "vocabulary",
            ]

            skills_focus = st.multiselect(
                t("skills_focus"),
                skill_options,
                format_func=lambda value: t(value),
            )

            materials = st.text_area(t("materials"))
            materials_url = st.text_input(t("materials_url"))
            homework_template = st.text_area(t("homework_template"))
            homework_url = st.text_input(t("homework_url"))
            
            lesson_submitted = st.form_submit_button(
                t("add_lesson")
            )
                        
            if lesson_submitted:
                if title.strip() == "":
                    st.error(t("please_enter_lesson_title"))
                else:
                    new_lesson = {
                        "user_id": user_id,
                        "course_id": int(str(selected_course).split(" — ")[0]),
                        "title": title,
                        "lesson_date": str(lesson_date),
                        "start_time": str(start_time),
                        "duration_minutes": int(duration_minutes),
                        "lesson_goal": lesson_goal,
                        "skills_focus": ", ".join(skills_focus) if isinstance(skills_focus, list) else skills_focus,
                        "materials": materials,
                        "materials_url": materials_url,
                        "homework_template": homework_template,
                        "homework_url": homework_url,
                        "is_archived": False,
                    }

                    supabase.table("lessons").insert(new_lesson).execute()

                    st.success(t("lesson_added_successfully"))
                    st.rerun()

    st.subheader(t("edit_lesson"))

    if lessons.empty:
        st.info(t("no_lessons_to_edit"))

    else:
        lesson_options = {
            f"{row['id']} — {row['title']}": int(row["id"])
            for _, row in lessons.iterrows()
        }

        selected_lesson_to_edit = st.selectbox(
            t("select_lesson_to_edit"),
            list(lesson_options.keys()),
            key="edit_lesson_select",
        )

        lesson_id_to_edit = lesson_options[selected_lesson_to_edit]
        lesson_row = lessons[lessons["id"].astype(int) == int(lesson_id_to_edit)].iloc[0]

        with st.form("edit_lesson_form"):
            edited_title = st.text_input(
                t("lesson_title"),
                value=lesson_row["title"],
            )

            current_lesson_date = lesson_row["lesson_date"]
            if pd.isna(current_lesson_date) or str(current_lesson_date).strip() == "":
                current_lesson_date = pd.Timestamp.today().date()
            else:
                current_lesson_date = pd.to_datetime(current_lesson_date).date()

            edited_lesson_date = st.date_input(
                t("lesson_date"),
                value=current_lesson_date,
            )

            current_start_time = lesson_row["start_time"]
            if pd.isna(current_start_time) or str(current_start_time).strip() == "":
                current_start_time = pd.to_datetime("13:00").time()
            else:
                current_start_time = pd.to_datetime(str(current_start_time)).time()

            edited_start_time = st.time_input(
                t("start_time"),
                value=current_start_time,
            )

            edited_duration_minutes = st.number_input(
                t("duration_minutes"),
                min_value=15,
                max_value=240,
                value=int(lesson_row["duration_minutes"]),
                step=15,
            )

            edited_lesson_goal = st.text_area(
                t("lesson_goal"),
                value=lesson_row["lesson_goal"],
            )

            skill_options = ["listening", "reading", "speaking", "writing", "grammar", "vocabulary"]

            current_skills_focus = lesson_row["skills_focus"]

            if pd.isna(current_skills_focus) or str(current_skills_focus).strip() in ["", "[]", "None", "nan"]:
                current_skills_focus = []
            else:
                current_skills_focus = [
                    skill.strip()
                    for skill in str(current_skills_focus).split(",")
                    if skill.strip() in skill_options
                ]

            edited_skills_focus = st.multiselect(
                t("skills_focus"),
                skill_options,
                default=current_skills_focus,
                format_func=lambda value: t(value),
            )

            edited_materials = st.text_area(
                t("materials"),
                value=lesson_row["materials"],
            )

            current_materials_url = lesson_row["materials_url"]
            if pd.isna(current_materials_url):
                current_materials_url = ""

            edited_materials_url = st.text_input(
                t("materials_url"),
                value=current_materials_url,
            )

            edited_homework_template = st.text_area(
                t("homework_template"),
                value=lesson_row["homework_template"],
            )

            current_homework_url = lesson_row["homework_url"]
            if pd.isna(current_homework_url):
                current_homework_url = ""

            edited_homework_url = st.text_input(
                t("homework_url"),
                value=current_homework_url,
            )

            edit_lesson_submitted = st.form_submit_button(
                t("save_lesson_changes")
            )

            if edit_lesson_submitted:
                if edited_title.strip() == "":
                    st.error(t("please_enter_lesson_title"))
                else:
                    updated_lesson = {
                        "title": edited_title,
                        "lesson_date": str(edited_lesson_date),
                        "start_time": str(edited_start_time),
                        "duration_minutes": int(edited_duration_minutes),
                        "lesson_goal": edited_lesson_goal,
                        "skills_focus": ", ".join(edited_skills_focus),
                        "materials": edited_materials,
                        "materials_url": edited_materials_url,
                        "homework_template": edited_homework_template,
                        "homework_url": edited_homework_url,
                    }

                    supabase.table("lessons").update(updated_lesson).eq(
                        "id",
                        int(lesson_id_to_edit)
                    ).eq(
                        "user_id",
                        user_id
                    ).execute()

                    st.success(t("lesson_updated_successfully"))
                    st.rerun()
                
    st.subheader(t("archive_lesson"))

    if active_lessons.empty:
        st.info(t("no_active_lessons_to_archive"))
    else:
        course_titles = dict(zip(courses["id"], courses["title"]))

        archive_lesson_options = {}

        for _, row in active_lessons.iterrows():
            course_name = course_titles.get(
                row["course_id"],
                t("unknown_course"),
            )
            label = f"{row['id']} — {row['title']} ({course_name})"
            archive_lesson_options[label] = int(row["id"])

        with st.form("archive_lesson_form"):
            lesson_to_archive = st.selectbox(
                t("select_lesson_to_archive"),
                list(archive_lesson_options.keys()),
                key="archive_lesson_select",
            )

            confirm_archive_lesson = st.checkbox(
                t("confirm_archive_lesson")
            )

            archive_lesson_submitted = st.form_submit_button(
                t("archive_lesson")
            )

            if archive_lesson_submitted:
                if not confirm_archive_lesson:
                    st.error(t("please_confirm_archiving"))
                else:
                    lesson_id_to_archive = archive_lesson_options[lesson_to_archive]

                    supabase.table("lessons").update(
                        {"is_archived": True}
                    ).eq(
                        "id",
                        int(lesson_id_to_archive)
                    ).eq(
                        "user_id",
                        user_id
                    ).execute()

                    st.success(t("lesson_archived_successfully"))
                    st.rerun()
               
    st.subheader(t("archived_lessons"))

    archived_lessons = lessons[lessons["is_archived"] == True].copy()

    if archived_lessons.empty:
        st.info(t("no_archived_lessons_yet"))
    else:
        course_titles = dict(zip(courses["id"], courses["title"]))

        archived_lessons["course"] = archived_lessons["course_id"].map(course_titles)

        archived_lessons_view = archived_lessons[
            ["course", "title"]
        ]

        st.dataframe(
            archived_lessons_view,
            width="stretch",
            hide_index=True,
            column_config={
                "course": st.column_config.TextColumn(
                    t("course"),
                    width="medium",
                ),
                "title": st.column_config.TextColumn(
                    t("title"),
                    width="large",
                ),
            }
        )
    
    st.subheader(t("restore_lesson"))

    archived_lessons = lessons[lessons["is_archived"] == True].copy()

    if archived_lessons.empty:
        st.info(t("no_archived_lessons_to_restore"))
    else:
        course_titles = dict(zip(courses["id"], courses["title"]))

        restore_lesson_options = {}

        for _, row in archived_lessons.iterrows():
            course_name = course_titles.get(
                row["course_id"],
                t("unknown_course"),
            )
            label = f"{row['id']} — {row['title']} ({course_name})"
            restore_lesson_options[label] = int(row["id"])

        with st.form("restore_lesson_form"):
            lesson_to_restore = st.selectbox(
                t("select_lesson_to_restore"),
                list(restore_lesson_options.keys()),
                key="restore_lesson_select",
            )

            confirm_restore_lesson = st.checkbox(
                t("confirm_restore_lesson")
            )

            restore_lesson_submitted = st.form_submit_button(
                t("restore_lesson")
            )

            if restore_lesson_submitted:
                if not confirm_restore_lesson:
                    st.error(t("please_confirm_restore"))
                else:
                    lesson_id_to_restore = restore_lesson_options[lesson_to_restore]

                    supabase.table("lessons").update(
                        {"is_archived": False}
                    ).eq(
                        "id",
                        int(lesson_id_to_restore)
                    ).eq(
                        "user_id",
                        user_id
                    ).execute()

                    st.success(t("lesson_restored_successfully"))
                    st.rerun()


elif page == "Assignments":

    st.header(t("assignments"))

    st.subheader(t("assignment_list"))

    assignments_view = assignments.copy()

    if assignments_view.empty:
        st.info(t("no_assignments_yet"))

    else:
        student_names = dict(zip(students["id"], students["name"]))
        course_titles = dict(zip(courses["id"], courses["title"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))

        assignments_view["student"] = assignments_view["student_id"].map(student_names)
        assignments_view["course"] = assignments_view["course_id"].map(course_titles)
        assignments_view["lesson"] = assignments_view["lesson_id"].map(lesson_titles)

        assignments_view["status"] = assignments_view["status"].apply(
            lambda value: t(ASSIGNMENT_STATUS_TRANSLATION_KEYS[value])
        )

        assignments_view["evaluation"] = assignments_view["evaluation"].apply(
            lambda value: t(EVALUATION_TRANSLATION_KEYS[value])
        )

        assignments_view = assignments_view[
            ["student", "lesson", "status", "evaluation"]
        ]

        st.dataframe(
            assignments_view,
            width="stretch",
            hide_index=True,
            column_config={
                "student": st.column_config.TextColumn(
                    t("student"),
                    width="medium",
                ),
                "lesson": st.column_config.TextColumn(
                    t("lesson"),
                    width="large",
                ),
                "status": st.column_config.TextColumn(
                    t("status"),
                    width="small",
                ),
                "evaluation": st.column_config.TextColumn(
                    t("evaluation"),
                    width="medium",
                ),
            },
        )
        
    st.subheader(t("assignment_details"))

    if assignments.empty:
        st.info(t("no_assignments_yet"))
    else:
        student_names = dict(zip(students["id"], students["name"]))
        course_titles = dict(zip(courses["id"], courses["title"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))
        
        for _, row in assignments.iterrows():
            student_name = student_names.get(
                row["student_id"],
                t("unknown_student"),
            )

            course_name = course_titles.get(
                row["course_id"],
                t("unknown_course"),
            )

            lesson_name = lesson_titles.get(
                row["lesson_id"],
                t("unknown_lesson"),
            )
            
            with st.expander(f"{student_name} – {lesson_name}"):

                st.write(
                    f"**{t('student')}:** {student_name}"
                )

                st.write(
                    f"**{t('course')}:** {course_name}"
                )

                st.write(
                    f"**{t('lesson')}:** {lesson_name}"
                )

                st.write(
                    f"**{t('homework')}:** {row['homework']}"
                )

                st.write(
                    f"**{t('status')}:** {row['status']}"
                )

                st.write(
                    f"**{t('evaluation')}:** {row['evaluation']}"
                )

                st.write(
                    f"**{t('teacher_comments')}:** {row['comments']}"
                )
    
    st.subheader(t("add_new_assignment"))

    if students.empty:
        st.warning(t("add_student_before_assignments"))

    elif courses.empty:
        st.warning(t("add_course_before_assignments"))

    elif lessons.empty:
        st.warning(t("add_lesson_before_assignments"))

    else:

        student_options = {
            student_label(row): int(row["id"])
            for _, row in students.iterrows()
        }

        course_options = {
            f"{row['id']} – {row['title']} "
            f"({row['target_language']} {row['level']} "
            f"· taught in {row['instruction_language']})": int(row["id"])
            for _, row in courses.iterrows()
        }
            
        selected_student = st.selectbox(
            t("student"),
            list(student_options.keys()),
            key="assignment_student",
        )

        selected_course = st.selectbox(
            t("course"),
            list(course_options.keys()),
            key="assignment_course",
        )
            
        selected_course_id = course_options[selected_course]

        filtered_lessons = active_lessons[
            active_lessons["course_id"].astype(int) == int(selected_course_id)
        ]

        if filtered_lessons.empty:
            st.warning(t("course_has_no_lessons"))
            selected_lesson = None
            lesson_options = {}
        else:
            lesson_options = {
                f"{row['id']} — {row['title']}": int(row["id"])
                for _, row in filtered_lessons.iterrows()
            }
        
            selected_lesson = st.selectbox(
                t("lesson"),
                list(lesson_options.keys()),
                key="assignment_lesson",
            )
            
        with st.form("add_assignment_form"):

            homework = st.text_area(
                t("homework")
            )

            assignment_statuses = [
                "assigned",
                "submitted",
                "checked",
                "needs revision",
                "completed",
            ]

            status = st.selectbox(
                t("assignment_status"),
                assignment_statuses,
                format_func=lambda value: t(
                    ASSIGNMENT_STATUS_TRANSLATION_KEYS[value]
                ),
            )

            evaluation_options = [
                "not evaluated",
                "excellent",
                "good",
                "satisfactory",
                "needs improvement",
            ]

            evaluation = st.selectbox(
                t("evaluation"),
                evaluation_options,
                format_func=lambda value: t(
                    EVALUATION_TRANSLATION_KEYS[value]
                ),
            )

            comments = st.text_area(
                t("teacher_comments")
            )

            assignment_submitted = st.form_submit_button(
                t("add_assignment")
            )

            if assignment_submitted:
                if selected_lesson is None:
                    st.error(t("add_lesson_for_course_first"))

                elif homework.strip() == "":
                    st.error(t("please_enter_homework_task"))
                else:
                    new_assignment = {
                        "user_id": user_id,
                        "student_id": int(student_options[selected_student]),
                        "course_id": int(selected_course_id),
                        "lesson_id": int(lesson_options[selected_lesson]),
                        "homework": homework,
                        "status": status,
                        "evaluation": evaluation,
                        "comments": comments,
                    }

                    supabase.table("assignments").insert(new_assignment).execute()

                    st.success(t("assignment_added_successfully"))
                    st.rerun()

    st.subheader(t("edit_assignment"))

    if assignments.empty:
        st.info(t("no_assignments_to_edit"))

    else:
        student_names = dict(zip(students["id"], students["name"]))
        course_titles = dict(zip(courses["id"], courses["title"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))

        edit_assignment_options = {}

        for _, row in assignments.iterrows():
            student_name = student_names.get(
                row["student_id"],
                t("unknown_student"),
            )

            lesson_name = lesson_titles.get(
                row["lesson_id"],
                t("unknown_lesson"),
            )

            assignment_status_label = t(
                ASSIGNMENT_STATUS_TRANSLATION_KEYS.get(
                    row["status"],
                    row["status"],
                )
            )

            label = (
                f"{row['id']} — {student_name} — "
                f"{lesson_name} ({assignment_status_label})"
            )

            edit_assignment_options[label] = int(row["id"])

        selected_assignment_to_edit = st.selectbox(
            t("select_assignment_to_edit"),
            list(edit_assignment_options.keys()),
            key="edit_assignment_select",
        )

        assignment_id_to_edit = edit_assignment_options[selected_assignment_to_edit]

        assignment_row = assignments[
            assignments["id"].astype(int) == int(assignment_id_to_edit)
        ].iloc[0]

        with st.form("edit_assignment_form"):
            current_homework = assignment_row["homework"]
            if pd.isna(current_homework):
                current_homework = ""

            edited_homework = st.text_area(
                t("homework"),
                value=current_homework,
            )

            assignment_statuses = ["assigned", "submitted", "checked", "needs revision", "completed"]

            edited_status = st.selectbox(
                t("assignment_status"),
                assignment_statuses,
                index=(
                    assignment_statuses.index(assignment_row["status"])
                    if assignment_row["status"] in assignment_statuses
                    else 0
                ),
                format_func=lambda value: t(
                    ASSIGNMENT_STATUS_TRANSLATION_KEYS[value]
                ),
            )

            evaluation_options = [
                "not evaluated",
                "excellent",
                "good",
                "satisfactory",
                "needs improvement"
            ]

            edited_evaluation = st.selectbox(
                t("evaluation"),
                evaluation_options,
                index=(
                    evaluation_options.index(assignment_row["evaluation"])
                    if assignment_row["evaluation"] in evaluation_options
                    else 0
                ),
                format_func=lambda value: t(
                    EVALUATION_TRANSLATION_KEYS[value]
                ),
            )

            current_comments = assignment_row["comments"]
            if pd.isna(current_comments):
                current_comments = ""

            edited_comments = st.text_area(
                t("teacher_comments"),
                value=current_comments,
            )

            edit_assignment_submitted = st.form_submit_button(
                t("save_assignment_changes")
            )

            if edit_assignment_submitted:
                if edited_homework.strip() == "":
                    st.error(t("please_enter_homework_task"))
                else:
                    updated_assignment = {
                        "homework": edited_homework,
                        "status": edited_status,
                        "evaluation": edited_evaluation,
                        "comments": edited_comments,
                    }

                    supabase.table("assignments").update(updated_assignment).eq(
                        "id",
                        int(assignment_row["id"])
                    ).eq(
                        "user_id",
                        user_id
                    ).execute()

                    st.success(t("assignment_updated_successfully"))
                    st.rerun()

    st.subheader(t("delete_assignment"))

    if assignments.empty:
        st.info(t("no_assignments_to_delete"))
    else:
        student_names = dict(zip(students["id"], students["name"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))

        delete_assignment_options = {}

        for _, row in assignments.iterrows():
            student_name = student_names.get(
                row["student_id"],
                t("unknown_student"),
            )

            lesson_name = lesson_titles.get(
                row["lesson_id"],
                t("unknown_lesson"),
            )

            label = f"{row['id']} — {student_name} — {lesson_name} ({row['status']})"
            delete_assignment_options[label] = row["id"]

        with st.form("delete_assignment_form"):
            assignment_to_delete = st.selectbox(
                t("select_assignment_to_delete"),
                list(delete_assignment_options.keys()),
                key="delete_assignment_select",
            )

            confirm_delete_assignment = st.checkbox(
                t("confirm_delete_assignment")
            )

            delete_assignment_submitted = st.form_submit_button(
                t("delete_assignment")
            )

            if delete_assignment_submitted:
                if not confirm_delete_assignment:
                    st.error(t("please_confirm_deletion"))
                else:
                    assignment_id_to_delete = delete_assignment_options[assignment_to_delete]

                    supabase.table("assignments").delete().eq(
                        "id",
                        int(assignment_id_to_delete)
                    ).eq(
                        "user_id",
                        user_id
                    ).execute()

                    st.success(t("assignment_deleted_successfully"))
                    st.rerun()

elif page == "Progress":
    st.header(t("progress"))

    progress_view = progress.copy()

    st.subheader(t("progress_overview"))

    if progress_view.empty:
        st.info(t("no_progress_records_yet"))

    else:
        student_names = dict(zip(students["id"], students["name"]))
        course_titles = dict(zip(courses["id"], courses["title"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))

        progress_view["student"] = progress_view["student_id"].map(student_names)
        progress_view["course"] = progress_view["course_id"].map(course_titles)
        progress_view["lesson"] = progress_view["lesson_id"].map(lesson_titles)

        progress_view["status"] = progress_view["status"].apply(
            lambda value: t(
                PROGRESS_STATUS_TRANSLATION_KEYS.get(
                    value,
                    value,
                )
            )
        )

        progress_view = progress_view[
            ["student", "course", "lesson", "status"]
        ]

        st.dataframe(
            progress_view,
            width="stretch",
            hide_index=True,
            column_config={
                "student": st.column_config.TextColumn(
                    t("student"),
                    width="medium",
                ),
                "course": st.column_config.TextColumn(
                    t("course"),
                    width="medium",
                ),
                "lesson": st.column_config.TextColumn(
                    t("lesson"),
                    width="large",
                ),
                "status": st.column_config.TextColumn(
                    t("status"),
                    width="small",
                ),
            },
        )

    st.subheader(t("progress_details"))

    if progress.empty:
        st.info(t("no_progress_records_yet"))
    else:
        student_names = dict(zip(students["id"], students["name"]))
        course_titles = dict(zip(courses["id"], courses["title"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))

        for _, row in progress.iterrows():
            student_name = student_names.get(row["student_id"], "Unknown student")
            course_name = course_titles.get(row["course_id"], "Unknown course")
            lesson_name = lesson_titles.get(row["lesson_id"], "Unknown lesson")

            teacher_comment = row["teacher_comment"]

            if pd.isna(teacher_comment) or str(teacher_comment).strip() == "":
                teacher_comment = t("no_comments_yet")

            with st.expander(f"{student_name} – {lesson_name}"):
                st.write(
                    f"**{t('student')}:** {student_name}"
                )
                st.write(
                    f"**{t('course')}:** {course_name}"
                )
                st.write(
                    f"**{t('lesson')}:** {lesson_name}"
                )
                st.write(
                    f"**{t('status')}:** {row['status']}"
                )
                st.write(
                    f"**{t('teacher_comment')}:** {teacher_comment}"
                )

    st.subheader(t("add_progress_record"))

    if students.empty:
        st.warning(t("add_student_before_progress"))

    elif courses.empty:
        st.warning(t("add_course_before_progress"))

    elif lessons.empty:
        st.warning(t("add_lesson_before_progress"))

    else:

        student_options = {
            student_label(row): int(row["id"])
            for _, row in students.iterrows()
        }

        course_options = {
            course_label(row): int(row["id"])
            for _, row in courses.iterrows()
        }

        selected_student = st.selectbox(
            t("student"),
            list(student_options.keys()),
            key="progress_student",
        )

        selected_course = st.selectbox(
            t("course"),
            list(course_options.keys()),
            key="progress_course",
        )

        selected_course_id = course_options[selected_course]

        filtered_lessons = active_lessons[
            active_lessons["course_id"].astype(int) == int(selected_course_id)
        ]

        if filtered_lessons.empty:
            st.warning(t("course_has_no_lessons"))
            selected_lesson = None
            lesson_options = {}
        else:
            lesson_options = {
                f"{row['id']} — {row['title']}": int(row["id"])
                for _, row in filtered_lessons.iterrows()
            }

            selected_lesson = st.selectbox(
                t("lesson"),
                list(lesson_options.keys()),
                key="progress_lesson",
            )

        with st.form("add_progress_form"):
            progress_statuses = [
                "not started",
                "in progress",
                "completed",
            ]

            status = st.selectbox(
                t("progress_status"),
                progress_statuses,
                key="progress_status",
                format_func=lambda value: t(
                    PROGRESS_STATUS_TRANSLATION_KEYS[value]
                ),
            )

            teacher_comment = st.text_area(
                t("teacher_comment")
            )

            progress_submitted = st.form_submit_button(
                t("add_progress")
            )

            if progress_submitted:
                if selected_lesson is None:
                    st.error(t("add_lesson_for_progress_first"))
                else:
                    new_progress = {
                        "user_id": user_id,
                        "student_id": int(student_options[selected_student]),
                        "course_id": int(selected_course_id),
                        "lesson_id": int(lesson_options[selected_lesson]),
                        "status": status,
                        "teacher_comment": teacher_comment,
                    }

                    supabase.table("progress").insert(new_progress).execute()

                    st.success(t("progress_added_successfully"))
                    st.rerun()
    
    st.subheader(t("edit_progress_record"))

    if progress.empty:
        st.info(t("no_progress_records_to_edit"))
    else:
        student_names = dict(zip(students["id"], students["name"]))
        course_titles = dict(zip(courses["id"], courses["title"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))

        edit_progress_options = {}

        for _, row in progress.iterrows():
            student_name = student_names.get(
                row["student_id"],
                t("unknown_student"),
            )

            lesson_name = lesson_titles.get(
                row["lesson_id"],
                t("unknown_lesson"),
            )

            label = f"{row['id']} — {student_name} — {lesson_name} ({row['status']})"
            edit_progress_options[label] = int(row["id"])

        selected_progress_to_edit = st.selectbox(
            t("select_progress_record_to_edit"),
            list(edit_progress_options.keys()),
            key="edit_progress_select",
        )

        progress_id_to_edit = edit_progress_options[selected_progress_to_edit]

        progress_row = progress[
            progress["id"].astype(int) == int(progress_id_to_edit)
        ].iloc[0]

        with st.form("edit_progress_form"):
            progress_statuses = ["not started", "in progress", "completed"]

            edited_progress_status = st.selectbox(
                t("progress_status"),
                progress_statuses,
                index=(
                    progress_statuses.index(progress_row["status"])
                    if progress_row["status"] in progress_statuses
                    else 0
                ),
            )

            current_teacher_comment = progress_row["teacher_comment"]

            if pd.isna(current_teacher_comment):
                current_teacher_comment = ""

            edited_teacher_comment = st.text_area(
                t("teacher_comment"),
                value=current_teacher_comment,
            )

            edit_progress_submitted = st.form_submit_button(
                t("save_progress_changes")
            )

            if edit_progress_submitted:
                updated_progress = {
                    "status": edited_progress_status,
                    "teacher_comment": edited_teacher_comment,
                }

                supabase.table("progress").update(updated_progress).eq(
                    "id",
                    int(progress_row["id"])
                ).eq(
                    "user_id",
                    user_id
                ).execute()

                st.success(t("progress_updated_successfully"))
                st.rerun()

    st.subheader(t("delete_progress_record"))

    if progress.empty:
        st.info(t("no_progress_records_to_delete"))
    else:
        student_names = dict(zip(students["id"], students["name"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))

        delete_progress_options = {}

        for _, row in progress.iterrows():
            student_name = student_names.get(
                row["student_id"],
                t("unknown_student"),
            )

            lesson_name = lesson_titles.get(
                row["lesson_id"],
                t("unknown_lesson"),
            )

            label = f"{row['id']} — {student_name} — {lesson_name} ({row['status']})"
            delete_progress_options[label] = row["id"]

        with st.form("delete_progress_form"):
            progress_to_delete = st.selectbox(
                t("select_progress_record_to_delete"),
                list(delete_progress_options.keys()),
                key="delete_progress_select",
            )

            confirm_delete_progress = st.checkbox(
                t("confirm_delete_progress")
            )

            delete_progress_submitted = st.form_submit_button(
                t("delete_progress_record")
            )

            if delete_progress_submitted:
                if not confirm_delete_progress:
                    st.error(t("please_confirm_deletion"))
                else:
                    progress_id_to_delete = delete_progress_options[progress_to_delete]

                    supabase.table("progress").delete().eq(
                        "id",
                        int(progress_id_to_delete)
                    ).eq(
                        "user_id",
                        user_id
                    ).execute()

                    st.success(t("progress_record_deleted_successfully"))
                    st.rerun()

elif page == "Student Skills":
    st.header(t("student_skills"))
    
    student_skills_view = student_skills.copy()
    
    if not student_skills_view.empty and not students.empty:
        student_names = dict(zip(students["id"], students["name"]))
        student_skills_view["student"] = student_skills_view["student_id"].map(student_names)
    
        student_skills_view = student_skills_view[
            ["student", "listening", "reading", "speaking", "writing"]
        ]
        
        st.subheader(t("skills_overview"))
        st.dataframe(
            student_skills_view,
            width="stretch",
            hide_index=True,
            column_config={
                "student": st.column_config.TextColumn(
                    t("student"),
                    width="medium",
                ),
                "listening": st.column_config.NumberColumn(
                    t("listening"),
                    width="small",
                ),
                "reading": st.column_config.NumberColumn(
                    t("reading"),
                    width="small",
                ),
                "speaking": st.column_config.NumberColumn(
                    t("speaking"),
                    width="small",
                ),
                "writing": st.column_config.NumberColumn(
                    t("writing"),
                    width="small",
                ),
            }
        )
        
    st.subheader(t("skills_details"))

    if student_skills.empty:
        st.info(t("no_skill_records_yet"))
    else:
        student_names = dict(zip(students["id"], students["name"]))
        skill_columns = ["listening", "reading", "speaking", "writing", "grammar", "vocabulary"]

        for _, row in student_skills.iterrows():
            student_name = student_names.get(
                row["student_id"],
                t("unknown_student"),
            )

            scores = {
                skill: row[skill]
                for skill in skill_columns
            }

            average_score = sum(scores.values()) / len(scores)
            strongest_skill = max(scores, key=scores.get)
            weakest_skill = min(scores, key=scores.get)

            with st.expander(
                f"{student_name} – {t('skills_profile')}"
            ):
                st.write(
                    f"**{t('student')}:** {student_name}"
                )

                st.write(
                    f"**{t('average_skill_score')}:** "
                    f"{average_score:.1f} / 5"
                )

                st.write(
                    f"**{t('strongest_skill')}:** "
                    f"{t(strongest_skill)} "
                    f"({scores[strongest_skill]}/5)"
                )

                st.write(
                    f"**{t('needs_focus')}:** "
                    f"{t(weakest_skill)} "
                    f"({scores[weakest_skill]}/5)"
                )

                st.write(
                    f"**{t('listening')}:** {row['listening']} / 5"
                )

                st.write(
                    f"**{t('reading')}:** {row['reading']} / 5"
                )

                st.write(
                    f"**{t('speaking')}:** {row['speaking']} / 5"
                )

                st.write(
                    f"**{t('writing')}:** {row['writing']} / 5"
                )

                st.write(
                    f"**{t('grammar')}:** {row['grammar']} / 5"
                )

                st.write(
                    f"**{t('vocabulary')}:** {row['vocabulary']} / 5"
                )

                comments = row["comments"]

                if pd.isna(comments) or str(comments).strip() == "":
                    comments = t("no_comments_yet")

                st.write(
                    f"**{t('comments')}:** {comments}"
                )

    st.subheader(t("add_student_skills"))

    if students.empty:
        st.warning(t("add_student_before_skills"))

    else:
        student_options = {
            student_label(row): int(row["id"])
            for _, row in students.iterrows()
        }

        with st.form("add_student_skills_form"):
            selected_student = st.selectbox(
                t("student"),
                list(student_options.keys()),
                key="skills_student_select",
            )

            listening = st.slider(t("listening"), 1, 5, 3)
            reading = st.slider(t("reading"), 1, 5, 3)
            speaking = st.slider(t("speaking"), 1, 5, 3)
            writing = st.slider(t("writing"), 1, 5, 3)
            grammar = st.slider(t("grammar"), 1, 5, 3)
            vocabulary = st.slider(t("vocabulary"), 1, 5, 3)

            comments = st.text_area(t("comments"))

            skills_submitted = st.form_submit_button(
                t("add_skills")
            )

            if skills_submitted:
                existing_skill = student_skills[
                    student_skills["student_id"].astype(int) == int(student_options[selected_student])
                ]

                if not existing_skill.empty:
                    st.error(t("student_already_has_skills_profile"))
                else:
                    new_skill = {
                        "user_id": user_id,
                        "student_id": int(student_options[selected_student]),
                        "listening": listening,
                        "reading": reading,
                        "speaking": speaking,
                        "writing": writing,
                        "grammar": grammar,
                        "vocabulary": vocabulary,
                        "comments": comments,
                    }

                    supabase.table("student_skills").insert(new_skill).execute()

                    st.success(t("student_skills_added_successfully"))
                    st.rerun()

    st.subheader(t("edit_student_skills"))

    if student_skills.empty:
        st.info(t("no_skills_records_to_edit"))
    else:
        student_names = dict(zip(students["id"], students["name"]))

        edit_skill_options = {}

        for _, row in student_skills.iterrows():
            student_name = student_names.get(
                row["student_id"],
                t("unknown_student"),
            )
            edit_skill_options[f"{row['id']} — {student_name}"] = int(row["id"])

        selected_skill_to_edit = st.selectbox(
            t("select_skills_record_to_edit"),
            list(edit_skill_options.keys()),
            key="edit_skills_select",
        )

        skill_id_to_edit = edit_skill_options[selected_skill_to_edit]

        skill_row = student_skills[
            student_skills["id"].astype(int) == int(skill_id_to_edit)
        ].iloc[0]

        with st.form("edit_student_skills_form"):
            edited_listening = st.slider(
                t("listening"),
                1,
                5,
                int(skill_row["listening"]),
                key="edit_listening",
            )

            edited_reading = st.slider(
                t("reading"),
                1,
                5,
                int(skill_row["reading"]),
                key="edit_reading",
            )

            edited_speaking = st.slider(
                t("speaking"),
                1,
                5,
                int(skill_row["speaking"]),
                key="edit_speaking",
            )

            edited_writing = st.slider(
                t("writing"),
                1,
                5,
                int(skill_row["writing"]),
                key="edit_writing",
            )

            edited_grammar = st.slider(
                t("grammar"),
                1,
                5,
                int(skill_row["grammar"]),
                key="edit_grammar",
            )

            edited_vocabulary = st.slider(
                t("vocabulary"),
                1,
                5,
                int(skill_row["vocabulary"]),
                key="edit_vocabulary",
            )

            current_comments = skill_row["comments"]
            if pd.isna(current_comments):
                current_comments = ""

            edited_comments = st.text_area(
                t("comments"),
                value=current_comments,
                key="edit_skills_comments",
            )

            edit_skills_submitted = st.form_submit_button(
                t("update_skills")
            )
            
            if edit_skills_submitted:
                updated_skills = {
                    "listening": edited_listening,
                    "reading": edited_reading,
                    "speaking": edited_speaking,
                    "writing": edited_writing,
                    "grammar": edited_grammar,
                    "vocabulary": edited_vocabulary,
                    "comments": edited_comments,
                }

                supabase.table("student_skills").update(updated_skills).eq(
                    "id",
                    int(skill_row["id"])
                ).eq(
                    "user_id",
                    user_id
                ).execute()

                st.success(t("student_skills_updated_successfully"))
                st.rerun()