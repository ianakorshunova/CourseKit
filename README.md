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

## 🛠 Tech Stack

- Python
- Streamlit
- Pandas
- CSV-based data storage
- Custom CSS

## 📁 Project Structure

```text
CourseKit/
├── app.py
├── style.css
├── requirements.txt
├── .gitignore
├── README.md
└── data/
    ├── students.csv
    ├── courses.csv
    ├── lessons.csv
    ├── assignments.csv
    ├── progress.csv
    └── student_skills.csv
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

CourseKit uses CSV files as a lightweight database.

Main entities:

* `students.csv` — student profiles
* `courses.csv` — course information
* `lessons.csv` — lesson plans, dates, resources, archive status
* `assignments.csv` — homework and assignment tracking
* `progress.csv` — student progress by course and lesson
* `student_skills.csv` — skill profiles for each student

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

Screenshots will be added after deployment.

## 🌱 Future Improvements

* Student-facing homework submission
* File uploads for lesson materials
* Calendar view for scheduled lessons
* Attendance tracking
* Exportable student reports
* Authentication and user accounts
* Database migration from CSV to SQLite

## 👩‍💻 Author

Created by Iana Korshunova as an EdTech / Python / Streamlit portfolio project.
