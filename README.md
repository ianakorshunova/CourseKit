# CourseKit 📚

CourseKit is a lightweight mini LMS for language teachers and course creators.

It helps manage students, courses, lessons, assignments, student skills, and learning progress in one simple Streamlit app.

## ✨ Features

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

## 🛠️ Tech Stack

- Python
- Streamlit
- Pandas
- Supabase
- Custom CSS

## 📁 Project Structure

```text
CourseKit/
├── app.py
├── style.css
├── requirements.txt
├── .gitignore
├── README.md
└── screenshots/ # planned screenshots for the deployed app
    ├── dashboard.png
    ├── courses.png
    ├── students.png
    ├── lessons.png
    ├── assignments.png
    ├── progress.png
    └── student-skills.png
```

Data is stored in Supabase tables, not in local CSV files.
````

## 🚀 How to Run Locally

Clone the repository:

```bash
git clone https://github.com/your-username/coursekit.git
cd coursekit
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

## 📊 Data Model

CourseKit uses Supabase as its database backend.

The app stores courses, students, lessons, assignments, progress records, and student skill profiles in Supabase tables.

Main tables:

- `students` — student profiles, target language, level, status, and notes
- `courses` — course information, target language, instruction language, level, and description
- `lessons` — lesson plans, dates, start times, duration, materials, homework templates, and archive status
- `assignments` — homework tasks, assignment status, evaluation, and teacher comments
- `progress` — student progress by course and lesson
- `student_skills` — skill profiles for each student: listening, reading, speaking, writing, grammar, vocabulary, and comments

The current version uses demo data. Authentication and user-specific access are planned as future improvements.

## 🧪 Example Use Case

A language teacher can use CourseKit to:

1. Add students and their target language levels.
2. Create language courses.
3. Plan lessons with goals, materials, homework, dates, and resource links.
4. Assign homework to students.
5. Track lesson progress.
6. Monitor student skills across listening, reading, speaking, writing, grammar, and vocabulary.
7. View all important information on the student profile page.

## 🖼 Screenshots

Screenshots will be added soon.

## 🌱 Future Improvements

- Student-facing homework submission
- File uploads for lesson materials
- Calendar view for scheduled lessons
- Attendance tracking
- Exportable student reports
- Authentication and user accounts

## 👩‍💻 Author

Created by Iana Korshunova as an EdTech / Python / Streamlit portfolio project.
