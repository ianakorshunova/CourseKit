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
    target_language = display_value(row["target_language"], "Not specified")
    level = display_value(row["level"], "Not specified")

    return f"{row['id']} — {row['name']} ({target_language} {level})"

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

st.sidebar.caption(f"Signed in as: {current_user.email}")

if st.sidebar.button("Sign out"):
    sign_out_user()
    st.rerun()

st.sidebar.title("CourseKit")
page = st.sidebar.radio(
    "Workspace",
    [
        "Dashboard",
        "Students",
        "Student Profile",
        "Courses",
        "Lessons",
        "Assignments",
        "Progress",
        "Student Skills",
    ]
)

if page == "Dashboard":

    st.subheader("Dashboard")

    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("Students", len(students))
    col2.metric("Courses", len(courses))
    col3.metric("Lessons", len(active_lessons))
    col4.metric("Assignments", len(assignments))
    col5.metric("Progress", len(progress))

    st.subheader("Assignment status overview")

    if assignments.empty:
        st.info("No assignments yet.")
    else:
        status_counts = assignments["status"].value_counts()

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Assigned", int(status_counts.get("assigned", 0)))
        col2.metric("Submitted", int(status_counts.get("submitted", 0)))
        col3.metric("Checked", int(status_counts.get("checked", 0)))
        col4.metric("Needs revision", int(status_counts.get("needs revision", 0)))
        col5.metric("Completed", int(status_counts.get("completed", 0)))
    
    st.subheader("Progress status overview")

    if progress.empty:
        st.info("No progress records yet.")
    else:
        progress_status_counts = progress["status"].value_counts()

        col1, col2, col3 = st.columns(3)

        col1.metric("Not started", int(progress_status_counts.get("not started", 0)))
        col2.metric("In progress", int(progress_status_counts.get("in progress", 0)))
        col3.metric("Completed", int(progress_status_counts.get("completed", 0)))

elif page == "Students":
    
    st.header("Students")

    st.subheader("Student list")
    
    filtered_students = students.copy()
    
    search_name = st.text_input("Search by student name", key="student_search")

    language_options = (
    students["target_language"]
    .dropna()
    .astype(str)
    .str.strip()
    )

    language_options = sorted([
        language for language in language_options.unique()
        if language != "" and language.lower() != "nan"
    ])

    language_filter = st.selectbox(
        "Filter by language",
        ["All"] + language_options,
        key="student_language_filter"
    )
    
    level_filter = st.selectbox(
        "Filter by level",
        ["All"] + sorted(students["level"].dropna().unique().tolist()),
        key="student_level_filter"
    )
    
    status_filter = st.selectbox(
        "Filter by status",
        ["All"] + sorted(students["status"].dropna().unique().tolist()),
        key="student_status_filter"
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
        lambda value: display_value(value, "Not specified")
    )

    students_view["level"] = students_view["level"].apply(
        lambda value: display_value(value, "Not specified")
    )

    students_view["status"] = students_view["status"].apply(
        lambda value: display_value(value, "Not specified")
    )

    students_view["notes"] = students_view["notes"].apply(
        lambda value: display_value(value, "No notes")
    )

    students_view = students_view[
        ["name", "target_language", "level", "status", "notes"]
    ]

    st.dataframe(
        students_view,
        width="stretch",
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn("Name", width="medium"),
            "target_language": st.column_config.TextColumn("Target language", width="medium"),
            "level": st.column_config.TextColumn("Level", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "notes": st.column_config.TextColumn("Notes", width="large"),
        }
    )
    
    st.subheader("Add a new student")
    
    with st.form("add_student_form"):
        name = st.text_input("Student name")
        language = st.selectbox("Language", ["English", "Chinese", "Russian", "German", "Spanish", "Other"])
        level = st.selectbox("Level", ["A1", "A2", "B1", "B2", "C1", "C2"])
        status = st.selectbox("Status", ["active", "paused", "completed"])
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Add student")
        
        if submitted:
            if name.strip() == "":
                st.error("Please enter the student name.")
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

                st.success("Student added successfully!")
                st.rerun()

    st.subheader("Edit student")
    
    if students.empty:
        st.info("No students to edit.")
    
    else:

        edit_student_options = {
            student_label(row): int(row["id"])
            for _, row in students.iterrows()
        }
        
        selected_student_to_edit = st.selectbox(
            "Select student to edit",
            list(edit_student_options.keys()),
            key="edit_student_select"
        )
        
        student_id_to_edit = edit_student_options[selected_student_to_edit]
        
        student_row = students[
            students["id"].astype(int) == int(student_id_to_edit)
        ].iloc[0]
        
        with st.form("edit_student_form"):
            edited_name = st.text_input(
                "Student name",
                value=student_row["name"]
            )

            student_target_language = display_value(student_row["target_language"], "Other")

            language_options = ["English", "Chinese", "Russian", "German", "Spanish", "Other"]

            edited_target_language = st.selectbox(
                "Target language",
                language_options,
                index=language_options.index(student_target_language)
                if student_target_language in language_options
                else language_options.index("Other")
            )

            edited_level = st.selectbox(
                "Level",
                ["A1", "A2", "B1", "B2", "C1", "C2"],
                index=["A1", "A2", "B1", "B2", "C1", "C2"].index(student_row["level"])
                if student_row["level"] in ["A1", "A2", "B1", "B2", "C1", "C2"]
                else 0
            )

            edited_status = st.selectbox(
                "Status",
                ["active", "paused", "completed"],
                index=["active", "paused", "completed"].index(student_row["status"])
                if student_row["status"] in ["active", "paused", "completed"]
                else 0
            )

            current_notes = student_row["notes"]

            if pd.isna(current_notes):
                current_notes = ""

            edited_notes = st.text_area(
                "Notes",
                value=current_notes
            )

            edit_student_submitted = st.form_submit_button("Save student changes")
            
            if edit_student_submitted:
                if edited_name.strip() == "":
                    st.error("Please enter the student name.")
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

                    st.success("Student updated successfully!")
                    st.rerun()

    st.subheader("Delete student")
    
    if students.empty:
        st.info("No students to delete.")
    else:

        delete_student_options = {
            student_label(row): int(row["id"])
            for _, row in students.iterrows()
        }
        
        with st.form("delete_student_form"):
            student_to_delete = st.selectbox(
                "Select student to delete",
                list(delete_student_options.keys()),
                key="delete_student_select"
            )
            
            confirm_delete_student = st.checkbox(
                "I understand that this will also delete this student's assignments, progress records, and skills."
            )
            
            delete_student_submitted = st.form_submit_button("Delete student")
            
            if delete_student_submitted:
                if not confirm_delete_student:
                    st.error("Please confirm deletion first.")
                else:
                    student_id_to_delete = delete_student_options[student_to_delete]

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

                    st.success("Student and related records deleted successfully!")
                    st.rerun()

elif page == "Student Profile":
    st.header("Student Profile")

    if students.empty:
        st.info("No students yet. Please add a student first.")
    else:

        student_options = {
            student_label(row): int(row["id"])
            for _, row in students.iterrows()
        }

        selected_student = st.selectbox(
            "Select student",
            list(student_options.keys()),
            key="profile_student_select"
        )

        selected_student_id = student_options[selected_student]

        student_row = students[
            students["id"].astype(int) == int(selected_student_id)
        ].iloc[0]

        st.subheader("Basic info")

        col1, col2, col3 = st.columns(3)

        col1.metric("Student", display_value(student_row["name"], "Unknown student"))
        col2.metric("Target language", display_value(student_row["target_language"], "Not specified"))
        col3.metric("Level", display_value(student_row["level"], "Not specified"))

        st.write(f"**Status:** {display_value(student_row['status'], 'Not specified')}")

        notes = student_row["notes"]
        if pd.isna(notes) or str(notes).strip() == "":
            notes = "No notes yet."

        st.write(f"**Notes:** {notes}")

        st.subheader("Skills summary")

        student_skill_records = student_skills[
            student_skills["student_id"].astype(int) == int(selected_student_id)
        ]

        if student_skill_records.empty:
            st.info("No skills record for this student yet.")
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

            col1.metric("Average score", f"{average_score:.1f} / 5")
            col2.metric("Strongest skill", strongest_skill)
            col3.metric("Needs focus", weakest_skill)

            with st.expander("Full skills profile"):
                st.write(f"**Listening:** {latest_skills['listening']} / 5")
                st.write(f"**Reading:** {latest_skills['reading']} / 5")
                st.write(f"**Speaking:** {latest_skills['speaking']} / 5")
                st.write(f"**Writing:** {latest_skills['writing']} / 5")
                st.write(f"**Grammar:** {latest_skills['grammar']} / 5")
                st.write(f"**Vocabulary:** {latest_skills['vocabulary']} / 5")

                skill_comments = latest_skills["comments"]
                if pd.isna(skill_comments) or str(skill_comments).strip() == "":
                    skill_comments = "No comments yet."

                st.write(f"**Comments:** {skill_comments}")

        st.subheader("Assignments")

        student_assignments = assignments[
            assignments["student_id"].astype(int) == int(selected_student_id)
        ]

        if student_assignments.empty:
            st.info("No assignments for this student yet.")
        else:
            course_titles = dict(zip(courses["id"], courses["title"]))
            lesson_titles = dict(zip(lessons["id"], lessons["title"]))

            student_assignments_view = student_assignments.copy()

            student_assignments_view["course"] = student_assignments_view["course_id"].map(course_titles)
            student_assignments_view["lesson"] = student_assignments_view["lesson_id"].map(lesson_titles)

            student_assignments_view["course"] = student_assignments_view["course"].apply(
                lambda value: display_value(value, "Unknown course")
            )

            student_assignments_view["lesson"] = student_assignments_view["lesson"].apply(
                lambda value: display_value(value, "Unknown lesson")
            )

            student_assignments_view["status"] = student_assignments_view["status"].apply(
                lambda value: display_value(value, "Not specified")
            )

            student_assignments_view["evaluation"] = student_assignments_view["evaluation"].apply(
                lambda value: display_value(value, "Not evaluated")
            )

            student_assignments_view = student_assignments_view[
                ["lesson", "status", "evaluation"]
            ]

            st.dataframe(
                student_assignments_view,
                width="stretch",
                hide_index=True,
                column_config={
                    "lesson": st.column_config.TextColumn("Lesson", width="large"),
                    "status": st.column_config.TextColumn("Status", width="medium"),
                    "evaluation": st.column_config.TextColumn("Evaluation", width="medium"),
                }
            )

            with st.expander("Assignment details"):
                for _, row in student_assignments.iterrows():
                    course_name = course_titles.get(row["course_id"], "Unknown course")
                    lesson_name = lesson_titles.get(row["lesson_id"], "Unknown lesson")

                    comments = row["comments"]
                    if pd.isna(comments) or str(comments).strip() == "":
                        comments = "No comments yet."

                    st.write(f"### {lesson_name}")
                    st.write(f"**Course:** {course_name}")
                    st.write(f"**Homework:** {row['homework']}")
                    st.write(f"**Status:** {row['status']}")
                    st.write(f"**Evaluation:** {row['evaluation']}")
                    st.write(f"**Teacher comments:** {comments}")

        st.subheader("Progress")

        student_progress = progress[
            progress["student_id"].astype(int) == int(selected_student_id)
        ]

        if student_progress.empty:
            st.info("No progress records for this student yet.")
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
    st.header("Courses")
    
    st.subheader("Course list")

    courses_view = courses.copy()

    courses_view = courses_view[
        ["title", "target_language", "instruction_language", "level"]
    ]

    st.dataframe(
        courses_view,
        width="stretch",
        hide_index=True,
        column_config={
            "title": st.column_config.TextColumn("Title", width="large"),
            "target_language": st.column_config.TextColumn("Target language", width="medium"),
            "instruction_language": st.column_config.TextColumn("Taught in", width="medium"),
            "level": st.column_config.TextColumn("Level", width="small"),
        }
    )
    
    st.subheader("Add a new course")
    
    with st.form("add_course_form"):
        title = st.text_input("Course title")

        course_language = st.selectbox(
            "Target language",
            ["English", "Chinese", "Russian", "German", "Spanish", "Other"]
        )

        instruction_language = st.selectbox(
            "Instruction language",
            ["English", "Chinese", "Russian", "German", "Spanish", "Other"]
        )
        course_level = st.selectbox(
        "Course level",
        ["A1", "A2", "B1", "B2", "C1", "C2"],
        key="course_level"
        )
        description = st.text_area("Course description")
        
        course_submitted = st.form_submit_button("Add course")
        
        if course_submitted:
            if title.strip() == "":
                st.error("Please enter the course title.")
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

                st.success("Course added successfully!")
                st.rerun()
    
    st.subheader("Edit course")

    if courses.empty:
        st.info("No courses to edit.")
    else:
        edit_course_options = {
            f"{row['id']} — {row['title']} ({row['target_language']} {row['level']} · taught in {row['instruction_language']})": int(row["id"])
            for _, row in courses.iterrows()
        }

        selected_course_to_edit = st.selectbox(
            "Select course to edit",
            list(edit_course_options.keys()),
            key="edit_course_select"
        )

        course_id_to_edit = edit_course_options[selected_course_to_edit]

        course_row = courses[
            courses["id"].astype(int) == int(course_id_to_edit)
        ].iloc[0]

        language_options = ["English", "Chinese", "Russian", "German", "Spanish", "Other"]
        level_options = ["A1", "A2", "B1", "B2", "C1", "C2"]

        with st.form("edit_course_form"):
            edited_title = st.text_input(
                "Course title",
                value=course_row["title"]
            )

            edited_target_language = st.selectbox(
                "Target language",
                language_options,
                index=language_options.index(course_row["target_language"])
                if course_row["target_language"] in language_options
                else 5
            )

            edited_instruction_language = st.selectbox(
                "Instruction language",
                language_options,
                index=language_options.index(course_row["instruction_language"])
                if course_row["instruction_language"] in language_options
                else 5
            )

            edited_level = st.selectbox(
                "Course level",
                level_options,
                index=level_options.index(course_row["level"])
                if course_row["level"] in level_options
                else 0,
                key="edit_course_level"
            )

            current_description = course_row["description"]

            if pd.isna(current_description):
                current_description = ""

            edited_description = st.text_area(
                "Course description",
                value=current_description
            )

            edit_course_submitted = st.form_submit_button("Save course changes")

            if edit_course_submitted:
                if edited_title.strip() == "":
                    st.error("Please enter the course title.")
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

                    st.success("Course updated successfully!")
                    st.rerun()

elif page == "Lessons":
    
    st.header("Lessons")
    
    st.subheader("Lesson list")

    lessons_view = active_lessons.copy()
    
    if not lessons_view.empty and not courses.empty:
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
            "course": st.column_config.TextColumn("Course", width="medium"),
            "title": st.column_config.TextColumn("Title", width="large"),
            "lesson_date": st.column_config.TextColumn("Date", width="small"),
            "start_time": st.column_config.TextColumn("Time", width="small"),
            "duration_minutes": st.column_config.NumberColumn("Min", width="small"),
        }
    )
    
    st.subheader("Lesson details")
    
    if lessons.empty:
        st.info("No lessons yet.")
    else:
        course_titles = dict(zip(courses["id"], courses["title"]))
        
        for _, row in lessons.iterrows():
            course_name = course_titles.get(row["course_id"], "Unknown course")
            
            with st.expander(f"{row['title']}"):
                st.write(f"**Course:** {course_name}")
                st.write(f"**Date:** {row['lesson_date']}")
                st.write(f"**Start time:** {row['start_time']}")
                st.write(f"**Duration:** {row['duration_minutes']} minutes")
                st.write(f"**Lesson goal:** {row['lesson_goal']}")
                st.write(f"**Skills focus:** {row['skills_focus']}")
                st.write(f"**Materials:** {row['materials']}")

                materials_url = row["materials_url"]

                if not pd.isna(materials_url) and str(materials_url).strip() != "":
                    st.markdown(f"**Materials link:** [Open resource]({materials_url})")

                st.write(f"**Homework template:** {row['homework_template']}")

                homework_url = row["homework_url"]
                if not pd.isna(homework_url) and str(homework_url).strip() != "":
                    st.markdown(f"**Homework link:** [Open resource]({homework_url})")
    
    st.subheader("Add a new lesson")
    
    if courses.empty:
        st.warning("Please add a course before creating lessons.")
    else:
        course_options = {
            f"{row['id']} — {row['title']} ({row['target_language']} {row['level']} · taught in {row['instruction_language']})": row["id"]
            for _, row in courses.iterrows()
        }
        
        with st.form("add_lesson_form"):
            selected_course = st.selectbox("Course", list(course_options.keys()))
            title = st.text_input("Lesson title")
            lesson_date = st.date_input("Lesson date")
            
            start_time = st.time_input("Start time")
            
            duration_minutes = st.number_input(
                "Duration, minutes",
                min_value=15,
                max_value=240,
                value=60,
                step=15
            )

            lesson_goal = st.text_area("Lesson goal")
            skills_focus = st.multiselect(
                "Skills focus",
                ["listening", "reading", "speaking", "writing", "grammar", "vocabulary"]
            )
            materials = st.text_area("Materials")
            materials_url = st.text_input("Materials URL")
            homework_template = st.text_area("Homework template")
            homework_url = st.text_input("Homework URL")
            
            lesson_submitted = st.form_submit_button("Add lesson")
            
            if lesson_submitted:
                if title.strip() == "":
                    st.error("Please enter the lesson title.")
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

                    st.success("Lesson added successfully!")
                    st.rerun()

    st.subheader("Edit lesson")

    if lessons.empty:
        st.info("No lessons to edit.")
    else:
        lesson_options = {
            f"{row['id']} — {row['title']}": int(row["id"])
            for _, row in lessons.iterrows()
        }

        selected_lesson_to_edit = st.selectbox(
            "Select lesson to edit",
            list(lesson_options.keys()),
            key="edit_lesson_select"
        )

        lesson_id_to_edit = lesson_options[selected_lesson_to_edit]
        lesson_row = lessons[lessons["id"].astype(int) == int(lesson_id_to_edit)].iloc[0]

        with st.form("edit_lesson_form"):
            edited_title = st.text_input(
                "Lesson title",
                value=lesson_row["title"]
            )

            current_lesson_date = lesson_row["lesson_date"]
            if pd.isna(current_lesson_date) or str(current_lesson_date).strip() == "":
                current_lesson_date = pd.Timestamp.today().date()
            else:
                current_lesson_date = pd.to_datetime(current_lesson_date).date()

            edited_lesson_date = st.date_input(
                "Lesson date",
                value=current_lesson_date
            )

            current_start_time = lesson_row["start_time"]
            if pd.isna(current_start_time) or str(current_start_time).strip() == "":
                current_start_time = pd.to_datetime("13:00").time()
            else:
                current_start_time = pd.to_datetime(str(current_start_time)).time()

            edited_start_time = st.time_input(
                "Start time",
                value=current_start_time
            )

            edited_duration_minutes = st.number_input(
                "Duration, minutes",
                min_value=15,
                max_value=240,
                value=int(lesson_row["duration_minutes"]),
                step=15
            )

            edited_lesson_goal = st.text_area(
                "Lesson goal",
                value=lesson_row["lesson_goal"]
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
                "Skills focus",
                skill_options,
                default=current_skills_focus
            )

            edited_materials = st.text_area(
                "Materials",
                value=lesson_row["materials"]
            )

            current_materials_url = lesson_row["materials_url"]
            if pd.isna(current_materials_url):
                current_materials_url = ""

            edited_materials_url = st.text_input(
                "Materials URL",
                value=current_materials_url
            )

            edited_homework_template = st.text_area(
                "Homework template",
                value=lesson_row["homework_template"]
            )

            current_homework_url = lesson_row["homework_url"]
            if pd.isna(current_homework_url):
                current_homework_url = ""

            edited_homework_url = st.text_input(
                "Homework URL",
                value=current_homework_url
            )

            edit_lesson_submitted = st.form_submit_button("Save lesson changes")

            if edit_lesson_submitted:
                if edited_title.strip() == "":
                    st.error("Please enter the lesson title.")
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

                    st.success("Lesson updated successfully!")
                    st.rerun()
                
    st.subheader("Archive lesson")

    if active_lessons.empty:
        st.info("No active lessons to archive.")
    else:
        course_titles = dict(zip(courses["id"], courses["title"]))

        archive_lesson_options = {}

        for _, row in active_lessons.iterrows():
            course_name = course_titles.get(row["course_id"], "Unknown course")
            label = f"{row['id']} — {row['title']} ({course_name})"
            archive_lesson_options[label] = int(row["id"])

        with st.form("archive_lesson_form"):
            lesson_to_archive = st.selectbox(
                "Select lesson to archive",
                list(archive_lesson_options.keys()),
                key="archive_lesson_select"
            )

            confirm_archive_lesson = st.checkbox(
                "I understand that this lesson will be archived and hidden from active lesson lists."
            )

            archive_lesson_submitted = st.form_submit_button("Archive lesson")

            if archive_lesson_submitted:
                if not confirm_archive_lesson:
                    st.error("Please confirm archiving first.")
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

                    st.success("Lesson archived successfully!")
                    st.rerun()
               
    st.subheader("Archived lessons")

    archived_lessons = lessons[lessons["is_archived"] == True].copy()

    if archived_lessons.empty:
        st.info("No archived lessons yet.")
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
                "course": st.column_config.TextColumn("Course", width="medium"),
                "title": st.column_config.TextColumn("Title", width="large"),
            }
        )
    
    st.subheader("Restore lesson")

    archived_lessons = lessons[lessons["is_archived"] == True].copy()

    if archived_lessons.empty:
        st.info("No archived lessons to restore.")
    else:
        course_titles = dict(zip(courses["id"], courses["title"]))

        restore_lesson_options = {}

        for _, row in archived_lessons.iterrows():
            course_name = course_titles.get(row["course_id"], "Unknown course")
            label = f"{row['id']} — {row['title']} ({course_name})"
            restore_lesson_options[label] = int(row["id"])

        with st.form("restore_lesson_form"):
            lesson_to_restore = st.selectbox(
                "Select lesson to restore",
                list(restore_lesson_options.keys()),
                key="restore_lesson_select"
            )

            confirm_restore_lesson = st.checkbox(
                "I understand that this lesson will be restored to active lesson lists."
            )

            restore_lesson_submitted = st.form_submit_button("Restore lesson")

            if restore_lesson_submitted:
                if not confirm_restore_lesson:
                    st.error("Please confirm restore first.")
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

                    st.success("Lesson restored successfully!")
                    st.rerun()


elif page == "Assignments":
    
    st.header("Assignments")
    
    st.subheader("Assignment list")
    
    assignments_view = assignments.copy()
    
    if not assignments_view.empty:
        student_names = dict(zip(students["id"], students["name"]))
        course_titles = dict(zip(courses["id"], courses["title"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))
        
        assignments_view["student"] = assignments_view["student_id"].map(student_names)
        assignments_view["course"] = assignments_view["course_id"].map(course_titles)
        assignments_view["lesson"] = assignments_view["lesson_id"].map(lesson_titles)
        
        assignments_view = assignments_view[
            ["student", "lesson", "status", "evaluation"]
        ]
    
    st.dataframe(
        assignments_view,
        width="stretch",
        hide_index=True,
        column_config={
            "student": st.column_config.TextColumn("Student", width="medium"),
            "lesson": st.column_config.TextColumn("Lesson", width="large"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "evaluation": st.column_config.TextColumn("Evaluation", width="medium"),
        }
    )
    
    st.subheader("Assignment details")
    
    if assignments.empty:
        st.info("No assignments yet.")
    else:
        student_names = dict(zip(students["id"], students["name"]))
        course_titles = dict(zip(courses["id"], courses["title"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))
        
        for _, row in assignments.iterrows():
            student_name = student_names.get(row["student_id"], "Unknown student")
            course_name = course_titles.get(row["course_id"], "Unknown course")
            lesson_name = lesson_titles.get(row["lesson_id"], "Unknown lesson")
            
            with st.expander(f"{student_name} — {lesson_name}"):
                st.write(f"**Student:** {student_name}")
                st.write(f"**Course:** {course_name}")
                st.write(f"**Lesson:** {lesson_name}")
                st.write(f"**Homework:** {row['homework']}")
                st.write(f"**Status:** {row['status']}")
                st.write(f"**Evaluation:** {row['evaluation']}")
                st.write(f"**Teacher comments:** {row['comments']}")
    
    st.subheader("Add a new assignment")
    
    if students.empty:
        st.warning("Please add a student before creating assignments.")
    elif courses.empty:
        st.warning("Please add a course before creating assignments.")
    elif lessons.empty:
        st.warning("Please add a lesson before creating assignments.")
    else:

        student_options = {
            student_label(row): int(row["id"])
            for _, row in students.iterrows()
        }

        course_options = {
            f"{row['id']} — {row['title']} ({row['target_language']} {row['level']} · taught in {row['instruction_language']})": int(row["id"])
            for _, row in courses.iterrows()
        }
            
        selected_student = st.selectbox(
            "Student",
            list(student_options.keys()),
            key="assignment_student"
        )
            
        selected_course = st.selectbox(
            "Course",
            list(course_options.keys()),
            key="assignment_course"
        )
            
        selected_course_id = course_options[selected_course]

        filtered_lessons = active_lessons[
            active_lessons["course_id"].astype(int) == int(selected_course_id)
        ]
            
        if filtered_lessons.empty:
            st.warning("This course has no lessons yet. Please add a lesson first.")
            selected_lesson = None
            lesson_options = {}
        else:
            lesson_options = {
                f"{row['id']} — {row['title']}": int(row["id"])
                for _, row in filtered_lessons.iterrows()
            }
                
            selected_lesson = st.selectbox(
                "Lesson",
                list(lesson_options.keys()),
                key="assignment_lesson"
            )
            
        with st.form("add_assignment_form"):
            homework = st.text_area("Homework")
            status = st.selectbox(
                "Assignment status",
                ["assigned", "submitted", "checked", "needs revision", "completed"]
            )
            evaluation = st.selectbox(
                "Evaluation",
                ["not evaluated", "excellent", "good", "satisfactory", "needs improvement"]
            )
            comments = st.text_area("Teacher comments")
                
            assignment_submitted = st.form_submit_button("Add assignment")

            if assignment_submitted:
                if selected_lesson is None:
                    st.error("Please add a lesson for this course before creating an assignment.")
                elif homework.strip() == "":
                    st.error("Please enter the homework task.")
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

                    st.success("Assignment added successfully!")
                    st.rerun()

    st.subheader("Edit assignment")

    if assignments.empty:
        st.info("No assignments to edit.")
    else:
        student_names = dict(zip(students["id"], students["name"]))
        course_titles = dict(zip(courses["id"], courses["title"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))

        edit_assignment_options = {}

        for _, row in assignments.iterrows():
            student_name = student_names.get(row["student_id"], "Unknown student")
            lesson_name = lesson_titles.get(row["lesson_id"], "Unknown lesson")

            label = f"{row['id']} — {student_name} — {lesson_name} ({row['status']})"
            edit_assignment_options[label] = int(row["id"])

        selected_assignment_to_edit = st.selectbox(
            "Select assignment to edit",
            list(edit_assignment_options.keys()),
            key="edit_assignment_select"
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
                "Homework",
                value=current_homework
            )

            assignment_statuses = ["assigned", "submitted", "checked", "needs revision", "completed"]

            edited_status = st.selectbox(
                "Assignment status",
                assignment_statuses,
                index=assignment_statuses.index(assignment_row["status"])
                if assignment_row["status"] in assignment_statuses
                else 0
            )

            evaluation_options = [
                "not evaluated",
                "excellent",
                "good",
                "satisfactory",
                "needs improvement"
            ]

            edited_evaluation = st.selectbox(
                "Evaluation",
                evaluation_options,
                index=evaluation_options.index(assignment_row["evaluation"])
                if assignment_row["evaluation"] in evaluation_options
                else 0
            )

            current_comments = assignment_row["comments"]
            if pd.isna(current_comments):
                current_comments = ""

            edited_comments = st.text_area(
                "Teacher comments",
                value=current_comments
            )

            edit_assignment_submitted = st.form_submit_button("Save assignment changes")

            if edit_assignment_submitted:
                if edited_homework.strip() == "":
                    st.error("Please enter the homework task.")
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

                    st.success("Assignment updated successfully!")
                    st.rerun()

    st.subheader("Delete assignment")

    if assignments.empty:
        st.info("No assignments to delete.")
    else:
        student_names = dict(zip(students["id"], students["name"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))

        delete_assignment_options = {}

        for _, row in assignments.iterrows():
            student_name = student_names.get(row["student_id"], "Unknown student")
            lesson_name = lesson_titles.get(row["lesson_id"], "Unknown lesson")

            label = f"{row['id']} — {student_name} — {lesson_name} ({row['status']})"
            delete_assignment_options[label] = row["id"]

        with st.form("delete_assignment_form"):
            assignment_to_delete = st.selectbox(
                "Select assignment to delete",
                list(delete_assignment_options.keys()),
                key="delete_assignment_select"
            )

            confirm_delete_assignment = st.checkbox(
                "I understand that this assignment will be permanently deleted."
            )

            delete_assignment_submitted = st.form_submit_button("Delete assignment")

            if delete_assignment_submitted:
                if not confirm_delete_assignment:
                    st.error("Please confirm deletion first.")
                else:
                    assignment_id_to_delete = delete_assignment_options[assignment_to_delete]

                    supabase.table("assignments").delete().eq(
                        "id",
                        int(assignment_id_to_delete)
                    ).eq(
                        "user_id",
                        user_id
                    ).execute()

                    st.success("Assignment deleted successfully!")
                    st.rerun()

elif page == "Progress":
    st.header("Progress")

    progress_view = progress.copy()

    if not progress_view.empty:
        student_names = dict(zip(students["id"], students["name"]))
        course_titles = dict(zip(courses["id"], courses["title"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))

        progress_view["student"] = progress_view["student_id"].map(student_names)
        progress_view["course"] = progress_view["course_id"].map(course_titles)
        progress_view["lesson"] = progress_view["lesson_id"].map(lesson_titles)

        progress_view = progress_view[
            ["student", "lesson", "status"]
        ]

    st.subheader("Progress overview")
    st.dataframe(
        progress_view,
        width="stretch",
        hide_index=True,
        column_config={
            "student": st.column_config.TextColumn("Student", width="medium"),
            "lesson": st.column_config.TextColumn("Lesson", width="large"),
            "status": st.column_config.TextColumn("Status", width="small"),
        }
    )

    st.subheader("Progress details")

    if progress.empty:
        st.info("No progress records yet.")
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
                teacher_comment = "No comments yet."

            with st.expander(f"{student_name} — {lesson_name}"):
                st.write(f"**Student:** {student_name}")
                st.write(f"**Course:** {course_name}")
                st.write(f"**Lesson:** {lesson_name}")
                st.write(f"**Status:** {row['status']}")
                st.write(f"**Teacher comment:** {teacher_comment}")

    st.subheader("Add progress record")

    if students.empty:
        st.warning("Please add a student before adding progress.")
    elif courses.empty:
        st.warning("Please add a course before adding progress.")
    elif lessons.empty:
        st.warning("Please add a lesson before adding progress.")
    else:

        student_options = {
            student_label(row): int(row["id"])
            for _, row in students.iterrows()
        }

        course_options = {
            f"{row['id']} — {row['title']} ({row['target_language']} {row['level']} · taught in {row['instruction_language']})": int(row["id"])
            for _, row in courses.iterrows()
        }

        selected_student = st.selectbox(
            "Student",
            list(student_options.keys()),
            key="progress_student"
        )

        selected_course = st.selectbox(
            "Course",
            list(course_options.keys()),
            key="progress_course"
        )

        selected_course_id = course_options[selected_course]

        filtered_lessons = active_lessons[
            active_lessons["course_id"].astype(int) == int(selected_course_id)
        ]

        if filtered_lessons.empty:
            st.warning("This course has no lessons yet. Please add a lesson first.")
            selected_lesson = None
            lesson_options = {}
        else:
            lesson_options = {
                f"{row['id']} — {row['title']}": int(row["id"])
                for _, row in filtered_lessons.iterrows()
            }

            selected_lesson = st.selectbox(
                "Lesson",
                list(lesson_options.keys()),
                key="progress_lesson"
            )

        with st.form("add_progress_form"):
            status = st.selectbox(
                "Progress status",
                ["not started", "in progress", "completed"],
                key="progress_status"
            )

            teacher_comment = st.text_area("Teacher comment")

            progress_submitted = st.form_submit_button("Add progress")

            if progress_submitted:
                if selected_lesson is None:
                    st.error("Please add a lesson for this course before adding progress.")
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

                    st.success("Progress added successfully!")
                    st.rerun()
    
    st.subheader("Edit progress record")

    if progress.empty:
        st.info("No progress records to edit.")
    else:
        student_names = dict(zip(students["id"], students["name"]))
        course_titles = dict(zip(courses["id"], courses["title"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))

        edit_progress_options = {}

        for _, row in progress.iterrows():
            student_name = student_names.get(row["student_id"], "Unknown student")
            lesson_name = lesson_titles.get(row["lesson_id"], "Unknown lesson")

            label = f"{row['id']} — {student_name} — {lesson_name} ({row['status']})"
            edit_progress_options[label] = int(row["id"])

        selected_progress_to_edit = st.selectbox(
            "Select progress record to edit",
            list(edit_progress_options.keys()),
            key="edit_progress_select"
        )

        progress_id_to_edit = edit_progress_options[selected_progress_to_edit]

        progress_row = progress[
            progress["id"].astype(int) == int(progress_id_to_edit)
        ].iloc[0]

        with st.form("edit_progress_form"):
            progress_statuses = ["not started", "in progress", "completed"]

            edited_progress_status = st.selectbox(
                "Progress status",
                progress_statuses,
                index=progress_statuses.index(progress_row["status"])
                if progress_row["status"] in progress_statuses
                else 0
            )

            current_teacher_comment = progress_row["teacher_comment"]

            if pd.isna(current_teacher_comment):
                current_teacher_comment = ""

            edited_teacher_comment = st.text_area(
                "Teacher comment",
                value=current_teacher_comment
            )

            edit_progress_submitted = st.form_submit_button("Save progress changes")

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

                st.success("Progress updated successfully!")
                st.rerun()

    st.subheader("Delete progress record")

    if progress.empty:
        st.info("No progress records to delete.")
    else:
        student_names = dict(zip(students["id"], students["name"]))
        lesson_titles = dict(zip(lessons["id"], lessons["title"]))

        delete_progress_options = {}

        for _, row in progress.iterrows():
            student_name = student_names.get(row["student_id"], "Unknown student")
            lesson_name = lesson_titles.get(row["lesson_id"], "Unknown lesson")

            label = f"{row['id']} — {student_name} — {lesson_name} ({row['status']})"
            delete_progress_options[label] = row["id"]

        with st.form("delete_progress_form"):
            progress_to_delete = st.selectbox(
                "Select progress record to delete",
                list(delete_progress_options.keys()),
                key="delete_progress_select"
            )

            confirm_delete_progress = st.checkbox(
                "I understand that this progress record will be permanently deleted."
            )

            delete_progress_submitted = st.form_submit_button("Delete progress record")

            if delete_progress_submitted:
                if not confirm_delete_progress:
                    st.error("Please confirm deletion first.")
                else:
                    progress_id_to_delete = delete_progress_options[progress_to_delete]

                    supabase.table("progress").delete().eq(
                        "id",
                        int(progress_id_to_delete)
                    ).eq(
                        "user_id",
                        user_id
                    ).execute()

                    st.success("Progress record deleted successfully!")
                    st.rerun()

elif page == "Student Skills":
    st.header("Student Skills")
    
    student_skills_view = student_skills.copy()
    
    if not student_skills_view.empty and not students.empty:
        student_names = dict(zip(students["id"], students["name"]))
        student_skills_view["student"] = student_skills_view["student_id"].map(student_names)
    
        student_skills_view = student_skills_view[
            ["student", "listening", "reading", "speaking", "writing"]
        ]
        
        st.subheader("Skills overview")
        st.dataframe(
            student_skills_view,
            width="stretch",
            hide_index=True,
            column_config={
                "student": st.column_config.TextColumn("Student", width="medium"),
                "listening": st.column_config.NumberColumn("Listening", width="small"),
                "reading": st.column_config.NumberColumn("Reading", width="small"),
                "speaking": st.column_config.NumberColumn("Speaking", width="small"),
                "writing": st.column_config.NumberColumn("Writing", width="small"),
            }
        )
        
    st.subheader("Skills details")

    if student_skills.empty:
        st.info("No skill records yet.")
    else:
        student_names = dict(zip(students["id"], students["name"]))
        skill_columns = ["listening", "reading", "speaking", "writing", "grammar", "vocabulary"]

        for _, row in student_skills.iterrows():
            student_name = student_names.get(row["student_id"], "Unknown student")

            scores = {
                skill: row[skill]
                for skill in skill_columns
            }

            average_score = sum(scores.values()) / len(scores)
            strongest_skill = max(scores, key=scores.get)
            weakest_skill = min(scores, key=scores.get)

            with st.expander(f"{student_name} — Skills profile"):
                st.write(f"**Student:** {student_name}")
                st.write(f"**Average skill score:** {average_score:.1f} / 5")
                st.write(f"**Strongest skill:** {strongest_skill} ({scores[strongest_skill]}/5)")
                st.write(f"**Needs focus:** {weakest_skill} ({scores[weakest_skill]}/5)")
                st.write(f"**Listening:** {row['listening']} / 5")
                st.write(f"**Reading:** {row['reading']} / 5")
                st.write(f"**Speaking:** {row['speaking']} / 5")
                st.write(f"**Writing:** {row['writing']} / 5")
                st.write(f"**Grammar:** {row['grammar']} / 5")
                st.write(f"**Vocabulary:** {row['vocabulary']} / 5")

                comments = row["comments"]

                if pd.isna(comments) or str(comments).strip() == "":
                    comments = "No comments yet."

                st.write(f"**Comments:** {comments}")

    st.subheader("Add student skills")

    if students.empty:
        st.warning("Please add a student before adding skills.")
    else:
        student_options = {
            student_label(row): int(row["id"])
            for _, row in students.iterrows()
        }

        with st.form("add_student_skills_form"):
            selected_student = st.selectbox(
                "Student",
                list(student_options.keys()),
                key="skills_student_select"
            )

            listening = st.slider("Listening", 1, 5, 3)
            reading = st.slider("Reading", 1, 5, 3)
            speaking = st.slider("Speaking", 1, 5, 3)
            writing = st.slider("Writing", 1, 5, 3)
            grammar = st.slider("Grammar", 1, 5, 3)
            vocabulary = st.slider("Vocabulary", 1, 5, 3)

            comments = st.text_area("Comments")

            skills_submitted = st.form_submit_button("Add skills")

            if skills_submitted:
                existing_skill = student_skills[
                    student_skills["student_id"].astype(int) == int(student_options[selected_student])
                ]

                if not existing_skill.empty:
                    st.error("This student already has a skills profile.")
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

                    st.success("Student skills added successfully!")
                    st.rerun()

    st.subheader("Edit student skills")

    if student_skills.empty:
        st.info("No skills records to edit yet.")
    else:
        student_names = dict(zip(students["id"], students["name"]))

        edit_skill_options = {}

        for _, row in student_skills.iterrows():
            student_name = student_names.get(row["student_id"], "Unknown student")
            edit_skill_options[f"{row['id']} — {student_name}"] = int(row["id"])

        selected_skill_to_edit = st.selectbox(
            "Select skills record to edit",
            list(edit_skill_options.keys()),
            key="edit_skills_select"
        )

        skill_id_to_edit = edit_skill_options[selected_skill_to_edit]

        skill_row = student_skills[
            student_skills["id"].astype(int) == int(skill_id_to_edit)
        ].iloc[0]

        with st.form("edit_student_skills_form"):
            edited_listening = st.slider(
                "Listening",
                1,
                5,
                int(skill_row["listening"]),
                key="edit_listening"
            )

            edited_reading = st.slider(
                "Reading",
                1,
                5,
                int(skill_row["reading"]),
                key="edit_reading"
            )

            edited_speaking = st.slider(
                "Speaking",
                1,
                5,
                int(skill_row["speaking"]),
                key="edit_speaking"
            )

            edited_writing = st.slider(
                "Writing",
                1,
                5,
                int(skill_row["writing"]),
                key="edit_writing"
            )

            edited_grammar = st.slider(
                "Grammar",
                1,
                5,
                int(skill_row["grammar"]),
                key="edit_grammar"
            )

            edited_vocabulary = st.slider(
                "Vocabulary",
                1,
                5,
                int(skill_row["vocabulary"]),
                key="edit_vocabulary"
            )

            current_comments = skill_row["comments"]
            if pd.isna(current_comments):
                current_comments = ""

            edited_comments = st.text_area(
                "Comments",
                value=current_comments,
                key="edit_skills_comments"
            )

            edit_skills_submitted = st.form_submit_button("Update skills")
            
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

                st.success("Student skills updated successfully!")
                st.rerun()