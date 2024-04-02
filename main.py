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
  user="yourusername",
  password="yourpassword",
  database="online_learning"
)

mycursor = mydb.cursor()

# Generate Users
for _ in range(NUM_USERS):
    sql = "INSERT INTO users (id, name, email, role) VALUES (%s, %s, %s, %s)"
    val = (fake.uuid4(), fake.name(), fake.email(), random.choice(["student", "instructor"]))
    mycursor.execute(sql, val)
    mydb.commit()

# Generate Courses
for _ in range(NUM_COURSES):
    sql = "INSERT INTO courses (id, title, description, instructor) VALUES (%s, %s, %s, %s)"
    val = (fake.uuid4(), fake.catch_phrase(), fake.text(), random.choice([user[0] for user in users if user[3] == "instructor"]))
    mycursor.execute(sql, val)
    mydb.commit()

    course_id = mycursor.lastrowid

    # Generate Lessons
    for _ in range(NUM_LESSONS_PER_COURSE):
        sql = "INSERT INTO lessons (id, course_id, title, content) VALUES (%s, %s, %s, %s)"
        val = (fake.uuid4(), course_id, fake.sentence(), fake.text())
        mycursor.execute(sql, val)
        mydb.commit()

        lesson_id = mycursor.lastrowid

        # Generate Quizzes
        for _ in range(NUM_QUIZZES_PER_LESSON):
            sql = "INSERT INTO quizzes (id, lesson_id, title) VALUES (%s, %s, %s)"
            val = (fake.uuid4(), lesson_id, fake.sentence())
            mycursor.execute(sql, val)
            mydb.commit()

            quiz_id = mycursor.lastrowid

            # Generate Questions
            for _ in range(NUM_QUESTIONS_PER_QUIZ):
                sql = "INSERT INTO quiz_questions (id, quiz_id, text, correct_answer) VALUES (%s, %s, %s, %s)"
                val = (fake.uuid4(), quiz_id, fake.sentence(), fake.word())
                mycursor.execute(sql, val)
                mydb.commit()

# Generate Enrollments
mycursor.execute("SELECT id, role FROM users")
users = mycursor.fetchall()

for user in users:
    if user[1] == "student":
        enrolled_courses = random.sample(range(1, NUM_COURSES + 1), NUM_ENROLLMENTS_PER_USER)
        for course_id in enrolled_courses:
            sql = "INSERT INTO enrollments (id, user_id, course_id, enrollment_date, progress) VALUES (%s, %s, %s, %s, %s)"
            val = (fake.uuid4(), user[0], course_id, fake.past_date(), f"{random.randint(0, 100)}%")
            mycursor.execute(sql, val)
            mydb.commit()

print("Random data generated and inserted into the database.")
