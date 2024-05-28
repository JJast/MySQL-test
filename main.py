import mysql.connector
from faker import Faker
import random
import time

# Initialize Faker
fake = Faker()

# Constants for the amounts of data to generate
NUM_USERS = 1000
NUM_COURSES = 200
NUM_ENROLLMENTS_PER_USER = 20
NUM_LESSONS_PER_COURSE = 50
NUM_QUIZZES_PER_LESSON = 20
NUM_QUESTIONS_PER_QUIZ = 30

# Connect to MySQL
mydb = mysql.connector.connect(
  host="localhost",
  port='3306',
  user="root",
  password="password",
  database="mysql"
)

mycursor = mydb.cursor()

def measure_time(operation_name, func):
    start_time = time.time()
    func()
    end_time = time.time()
    duration = end_time - start_time
    print(f"{operation_name} took {duration:.2f} seconds")

def drop_tables():
    tables = ["quiz_questions", "quizzes", "lessons", "enrollments", "courses", "users"]
    for table in tables:
        mycursor.execute(f"DROP TABLE IF EXISTS {table}")
    mydb.commit()
    print("Tables dropped successfully")

def create_tables():
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
            instructor VARCHAR(255),
            FOREIGN KEY (instructor) REFERENCES users(id)
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
    print("Tables created successfully")

def batch_insert(sql, values):
    try:
        mycursor.executemany(sql, values)
        mydb.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        mydb.rollback()

def insert_users():
    users = [(fake.uuid4(), fake.name(), fake.email(), random.choice(["student", "instructor"])) for _ in range(NUM_USERS)]
    batch_insert("INSERT INTO users (id, name, email, role) VALUES (%s, %s, %s, %s)", users)
    print("Users inserted successfully")

def retrieve_users():
    mycursor.execute("SELECT * FROM users")
    users = mycursor.fetchall()
    print(f"{len(users)} users retrieved successfully")
    return users

def insert_courses(users):
    instructors = [user[0] for user in users if user[3] == "instructor"]
    courses = [(fake.uuid4(), fake.catch_phrase(), fake.text(), random.choice(instructors)) for _ in range(NUM_COURSES)]
    batch_insert("INSERT INTO courses (id, title, description, instructor) VALUES (%s, %s, %s, %s)", courses)
    
    lessons = []
    quizzes = []
    questions = []
    
    mycursor.execute("SELECT id FROM courses")
    course_ids = [row[0] for row in mycursor.fetchall()]
    
    for course_id in course_ids:
        for _ in range(NUM_LESSONS_PER_COURSE):
            lesson_id = fake.uuid4()
            lessons.append((lesson_id, course_id, fake.sentence(), fake.text()))
            
            for _ in range(NUM_QUIZZES_PER_LESSON):
                quiz_id = fake.uuid4()
                quizzes.append((quiz_id, lesson_id, fake.sentence()))
                
                for _ in range(NUM_QUESTIONS_PER_QUIZ):
                    question_id = fake.uuid4()
                    questions.append((question_id, quiz_id, fake.sentence(), fake.word()))

    batch_insert("INSERT INTO lessons (id, course_id, title, content) VALUES (%s, %s, %s, %s)", lessons)
    batch_insert("INSERT INTO quizzes (id, lesson_id, title) VALUES (%s, %s, %s)", quizzes)
    batch_insert("INSERT INTO quiz_questions (id, quiz_id, text, correct_answer) VALUES (%s, %s, %s, %s)", questions)
    
    print("Courses, lessons, quizzes, and questions inserted successfully")

def generate_enrollments(users):
    students = [user for user in users if user[3] == "student"]
    mycursor.execute("SELECT id FROM courses")
    course_ids = [row[0] for row in mycursor.fetchall()]

    enrollments = []
    for student in students:
        enrolled_courses = random.sample(course_ids, NUM_ENROLLMENTS_PER_USER)
        for course_id in enrolled_courses:
            enrollments.append((fake.uuid4(), student[0], course_id, fake.date_between(start_date='-2y', end_date='today'), f"{random.randint(0, 100)}%"))
    
    batch_insert("INSERT INTO enrollments (id, user_id, course_id, enrollment_date, progress) VALUES (%s, %s, %s, %s, %s)", enrollments)
    print("Enrollments generated successfully")

def retrieve_courses():
    mycursor.execute("SELECT * FROM courses")
    courses = mycursor.fetchall()
    print(f"{len(courses)} courses retrieved successfully")
    return courses

def main():
    measure_time("Drop Tables", drop_tables)
    measure_time("Create Tables", create_tables)
    measure_time("Insert Users", insert_users)
    users = []
    measure_time("Retrieve Users", lambda: users.extend(retrieve_users()))
    measure_time("Insert Courses, Lessons, Quizzes, and Questions", lambda: insert_courses(users))
    measure_time("Generate Enrollments", lambda: generate_enrollments(users))
    measure_time("Retrieve Courses", retrieve_courses)
    print('Performance test completed')

if __name__ == '__main__':
    main()
