import mysql.connector
from faker import Faker
import random
from datetime import datetime

# Initialize Faker
fake = Faker()

# Constants for the amounts of data to generate
NUM_USERS = 100
NUM_COURSES = 20
NUM_ENROLLMENTS_PER_USER = 2
NUM_LESSONS_PER_COURSE = 5
NUM_QUIZZES_PER_LESSON = 2
NUM_QUESTIONS_PER_QUIZ = 3
NUM_SUBMISSIONS_PER_QUIZ = 50  # Total across all users, not per user

# Connect to MySQL
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="online_learning" 
)

mycursor = mydb.cursor()

# Create tables if not exist
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255),
        role VARCHAR(255)
    )
""")
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id VARCHAR(255) PRIMARY KEY,
        title VARCHAR(255),
        description TEXT,
        instructor VARCHAR(255)
    )
""")
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS lessons (
        id VARCHAR(255) PRIMARY KEY,
        course_id VARCHAR(255),
        title VARCHAR(255),
        content TEXT,
        FOREIGN KEY (course_id) REFERENCES courses(id)
    )
""")
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id VARCHAR(255) PRIMARY KEY,
        lesson_id VARCHAR(255),
        title VARCHAR(255),
        FOREIGN KEY (lesson_id) REFERENCES lessons(id)
    )
""")
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_questions (
        id VARCHAR(255) PRIMARY KEY,
        quiz_id VARCHAR(255),
        text TEXT,
        correct_answer VARCHAR(255),
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
    )
""")
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        id VARCHAR(255) PRIMARY KEY,
        user_id VARCHAR(255),
        course_id VARCHAR(255),
        enrollment_date DATE,
        progress VARCHAR(255),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)
    )
""")
mydb.commit()

# Generate Users
for _ in range(NUM_USERS):
    sql = "INSERT INTO users (id, name, email, role) VALUES (%s, %s, %s, %s)"
    val = (fake.uuid4(), fake.name(), fake.email(), random.choice(["student", "instructor"]))
    mycursor.execute(sql, val)
    mydb.commit()

# Generate Courses
mycursor.execute("SELECT id FROM users WHERE role = 'instructor'")
instructor_ids = mycursor.fetchall()

for _ in range(NUM_COURSES):
    instructor_id = random.choice(instructor_ids)[0]
    sql = "INSERT INTO courses (id, title, description, instructor) VALUES (%s, %s, %s, %s)"
    val = (fake.uuid4(), fake.catch_phrase(), fake.text(), instructor_id)
    mycursor.execute(sql, val)
    mydb.commit()

# Generate Lessons
mycursor.execute("SELECT id FROM courses")
course_ids = mycursor.fetchall()

for course_id in course_ids:
    for _ in range(NUM_LESSONS_PER_COURSE):
        sql = "INSERT INTO lessons (id, course_id, title, content) VALUES (%s, %s, %s, %s)"
        val = (fake.uuid4(), course_id[0], fake.sentence(), fake.text())
        mycursor.execute(sql, val)
        mydb.commit()

# Generate Quizzes
mycursor.execute("SELECT id FROM lessons")
lesson_ids = mycursor.fetchall()

for lesson_id in lesson_ids:
    for _ in range(NUM_QUIZZES_PER_LESSON):
        sql = "INSERT INTO quizzes (id, lesson_id, title) VALUES (%s, %s, %s)"
        val = (fake.uuid4(), lesson_id[0], fake.sentence())
        mycursor.execute(sql, val)
        mydb.commit()

# Generate Quiz Questions
mycursor.execute("SELECT id FROM quizzes")
quiz_ids = mycursor.fetchall()

for quiz_id in quiz_ids:
    for _ in range(NUM_QUESTIONS_PER_QUIZ):
        sql = "INSERT INTO quiz_questions (id, quiz_id, text, correct_answer) VALUES (%s, %s, %s, %s)"
        val = (fake.uuid4(), quiz_id[0], fake.sentence(), fake.word())
        mycursor.execute(sql, val)
        mydb.commit()

# Generate Enrollments
mycursor.execute("SELECT id FROM users WHERE role = 'student'")
student_ids = mycursor.fetchall()

for student_id in student_ids:
    for _ in range(NUM_ENROLLMENTS_PER_USER):
        course_id = random.choice(course_ids)[0]
        sql = "INSERT INTO enrollments (id, user_id, course_id, enrollment_date, progress) VALUES (%s, %s, %s, %s, %s)"
        val = (fake.uuid4(), student_id[0], course_id, fake.past_date(), f"{random.randint(0, 100)}%")
        mycursor.execute(sql, val)
        mydb.commit()

print("Random data generated and inserted into the database.")