# CourseKit 📚

CourseKit is a lightweight mini LMS for language teachers and course creators.

It helps manage students, courses, lessons, assignments, student skills, and learning progress in one simple Streamlit app.

The app includes user authentication, so each teacher can sign in and manage their own workspace.

## ✨ Features

- User authentication with Supabase Auth
- User-specific data access with Row Level Security policies
- Student management: add, edit, delete students
- Course management: create and edit language courses
- Lesson planning: lesson goals, skills focus, materials, homework templates
- Lesson scheduling: lesson date, start time, and duration
- Resource links: add external materials and homework links
- Assignment tracking: create, update, and delete assignments
- Progress tracking: monitor lesson progress by student and course
- Student profile page: see student info, assignments, skills, and progress in one place
- Student skills tracking: listening, reading, speaking, writing, grammar, and vocabulary
- Lesson archive and restore workflow
- Dashboard with key metrics and status overviews
- Mobile-friendly layout improvements

## 🛠️ Tech Stack

- Python
- Streamlit
- Pandas
- Supabase database
- Supabase Auth
- Row Level Security policies
- Custom CSS

## 📁 Project Structure

```text
CourseKit/
├── app.py
├── style.css
├── requirements.txt
├── .gitignore
├── README.md
└── screenshots/
    ├── dashboard.png
    ├── courses.png
    ├── students.png
    ├── lessons.png
    ├── assignments.png
    ├── progress.png
    └── student-skills.png
```

Data is stored in Supabase tables, not in local CSV files.

## 🚀 How to Run Locally

Clone the repository:

```bash
git clone https://github.com/ianakorshunova/CourseKit.git
cd CourseKit
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local Streamlit secrets file:

```bash
mkdir -p .streamlit
touch .streamlit/secrets.toml
```

Add your Supabase credentials to `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "your-supabase-project-url"
SUPABASE_ANON_KEY = "your-supabase-publishable-key"
```

Run the app:

```bash
streamlit run app.py
```

## 📊 Data Model

CourseKit uses Supabase as its database backend.

The app stores courses, students, lessons, assignments, progress records, and student skill profiles in Supabase tables.

Main tables:

- `students` — student profiles, target language, level, status, notes, and owner user ID
- `courses` — course information, target language, instruction language, level, description, and owner user ID
- `lessons` — lesson plans, dates, start times, duration, materials, homework templates, archive status, and owner user ID
- `assignments` — homework tasks, assignment status, evaluation, teacher comments, and owner user ID
- `progress` — student progress by course and lesson, linked to the owner user ID
- `student_skills` — skill profiles for each student: listening, reading, speaking, writing, grammar, vocabulary, comments, and owner user ID

Each record is linked to a Supabase Auth user. Row Level Security policies restrict access so users can manage only their own data.

## 🧪 Example Use Case

A language teacher can use CourseKit to:

1. Create an account and sign in.
2. Add students and their target language levels.
3. Create language courses.
4. Plan lessons with goals, materials, homework, dates, and resource links.
5. Assign homework to students.
6. Track lesson progress.
7. Monitor student skills across listening, reading, speaking, writing, grammar, and vocabulary.
8. View all important information on the student profile page.

## 🖼 Screenshots

Screenshots will be added soon.

## 🌱 Future Improvements

- Student-facing homework submission
- File uploads for lesson materials
- Calendar view for scheduled lessons
- Attendance tracking
- Exportable student reports
- Teacher onboarding flow and sample demo workspace

## 👩‍💻 Author

Created by Iana Korshunova as an EdTech / Python / Streamlit / Supabase portfolio project.
