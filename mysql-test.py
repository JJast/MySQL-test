import mysql.connector
from faker import Faker
import random
import time
import matplotlib.pyplot as plt
import pandas as pd

# Initialize Faker
fake = Faker()

# Constants for the amounts of data to generate
NUM_USERS = 10
NUM_COURSES = 20
NUM_LESSONS_PER_COURSE = 5
NUM_QUIZZES_PER_LESSON = 2
NUM_QUESTIONS_PER_QUIZ = 3
NUM_ENROLLMENTS_PER_USER = 2

# Connect to MySQL
mydb = mysql.connector.connect(
    host="localhost",
    port='3306',
    user="root",
    password="password",
    database="mysql"
)

mycursor = mydb.cursor()

timings = []

def edit_number_of_operations(multiplication=1):
    global NUM_USERS, NUM_COURSES, NUM_ENROLLMENTS_PER_USER, NUM_LESSONS_PER_COURSE, NUM_QUIZZES_PER_LESSON, NUM_QUESTIONS_PER_QUIZ

    NUM_USERS = NUM_USERS * multiplication
    NUM_COURSES = NUM_COURSES * multiplication
    # NUM_ENROLLMENTS_PER_USER = NUM_ENROLLMENTS_PER_USER * multiplication
    # NUM_LESSONS_PER_COURSE = NUM_LESSONS_PER_COURSE * multiplication
    # NUM_QUIZZES_PER_LESSON = NUM_QUIZZES_PER_LESSON * multiplication
    # NUM_QUESTIONS_PER_QUIZ = NUM_QUESTIONS_PER_QUIZ * multiplication

def measure_time(operation_name, func):
    start_time = time.time()
    func()
    end_time = time.time()
    duration = end_time - start_time
    timings.append((operation_name, duration))
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

def insert_all_data():
    # Insert users
    users = [(fake.uuid4(), fake.name(), fake.email(), random.choice(["student", "instructor"])) for _ in range(NUM_USERS)]
    batch_insert("INSERT INTO users (id, name, email, role) VALUES (%s, %s, %s, %s)", users)
    print("Users inserted successfully")
    
    # Retrieve users to get instructors
    mycursor.execute("SELECT * FROM users")
    users = mycursor.fetchall()
    instructors = [user[0] for user in users if user[3] == "instructor"]

    # Insert courses in chunks to avoid memory issues
    courses = [(fake.uuid4(), fake.catch_phrase(), fake.text(), random.choice(instructors)) for _ in range(NUM_COURSES)]
    chunk_size = 1000
    for i in range(0, len(courses), chunk_size):
        batch_insert("INSERT INTO courses (id, title, description, instructor) VALUES (%s, %s, %s, %s)", courses[i:i+chunk_size])
    
    lessons = []
    quizzes = []
    questions = []
    
    # Retrieve courses to get course IDs
    mycursor.execute("SELECT id FROM courses")
    course_ids = [row[0] for row in mycursor.fetchall()]
    
    # Generate lessons, quizzes, and questions
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

    # Insert lessons, quizzes, and questions in chunks
    for i in range(0, len(lessons), chunk_size):
        batch_insert("INSERT INTO lessons (id, course_id, title, content) VALUES (%s, %s, %s, %s)", lessons[i:i+chunk_size])
    for i in range(0, len(quizzes), chunk_size):
        batch_insert("INSERT INTO quizzes (id, lesson_id, title) VALUES (%s, %s, %s)", quizzes[i:i+chunk_size])
    for i in range(0, len(questions), chunk_size):
        batch_insert("INSERT INTO quiz_questions (id, quiz_id, text, correct_answer) VALUES (%s, %s, %s, %s)", questions[i:i+chunk_size])
    
    print("Courses, lessons, quizzes, and questions inserted successfully")
    
    # Generate enrollments
    students = [user for user in users if user[3] == "student"]
    enrollments = []
    for student in students:
        enrolled_courses = random.sample(course_ids, NUM_ENROLLMENTS_PER_USER)
        for course_id in enrolled_courses:
            enrollments.append((fake.uuid4(), student[0], course_id, fake.date_between(start_date='-2y', end_date='today'), f"{random.randint(0, 100)}%"))
    
    # Insert enrollments in chunks
    for i in range(0, len(enrollments), chunk_size):
        batch_insert("INSERT INTO enrollments (id, user_id, course_id, enrollment_date, progress) VALUES (%s, %s, %s, %s, %s)", enrollments[i:i+chunk_size])
    
    print("Enrollments generated successfully")

def read_all_data():
    mycursor.execute("SELECT * FROM users")
    users = mycursor.fetchall()
    
    mycursor.execute("SELECT * FROM courses")
    courses = mycursor.fetchall()
    
    mycursor.execute("SELECT * FROM lessons")
    lessons = mycursor.fetchall()
    
    mycursor.execute("SELECT * FROM quizzes")
    quizzes = mycursor.fetchall()
    
    mycursor.execute("SELECT * FROM quiz_questions")
    quiz_questions = mycursor.fetchall()
    
    mycursor.execute("SELECT * FROM enrollments")
    enrollments = mycursor.fetchall()
    
    print("All data read successfully")

def update_all_data():
    mycursor.execute("UPDATE users SET name = CONCAT(name, '_updated')")
    mycursor.execute("UPDATE courses SET title = CONCAT(title, '_updated')")
    mycursor.execute("UPDATE lessons SET title = CONCAT(title, '_updated')")
    mycursor.execute("UPDATE quizzes SET title = CONCAT(title, '_updated')")
    mycursor.execute("UPDATE quiz_questions SET text = CONCAT(text, '_updated')")
    mycursor.execute("UPDATE enrollments SET progress = CONCAT(progress, '_updated')")
    mydb.commit()
    print("All data updated successfully")

def delete_all_data():
    mycursor.execute("DELETE FROM enrollments")
    mycursor.execute("DELETE FROM quiz_questions")
    mycursor.execute("DELETE FROM quizzes")
    mycursor.execute("DELETE FROM lessons")
    mycursor.execute("DELETE FROM courses")
    mycursor.execute("DELETE FROM users")
    mydb.commit()
    print("All data deleted successfully")

def plot_timings():
    operations, durations = zip(*timings)

    plt.figure(figsize=(12, 6))
    plt.barh(operations, durations, color='skyblue')
    plt.xlabel('Time (seconds)')
    plt.title('Performance of MySQL Database Operations')
    plt.grid(axis='x')
    plt.show()

def save_timings_to_excel(filename="timings_.xlsx"):
    timings_df = pd.DataFrame(timings, columns=["Operation", "Duration (seconds)"])
    timings_df.to_excel(filename, index=False)
    print(f"Timings saved to {filename} successfully")

def main():
    multiplication = input("Enter how many times to multiply the amount of data: ")
    try:
        multiplication = int(multiplication)
    except:
        print("Intiger not provided")
    if not isinstance(multiplication, int):
        print("Provided multiplication factor is not an integer. Defaulting to 1.")
        multiplication = 1
    edit_number_of_operations(multiplication)

    measure_time("Drop Tables", drop_tables)
    measure_time("Create Tables", create_tables)
    measure_time("Insert All Data", insert_all_data)
    measure_time("Read All Data", read_all_data)
    measure_time("Update All Data", update_all_data)
    measure_time("Delete All Data", delete_all_data)
    
    print('Performance test completed')

    save_timings_to_excel("timings_MySQL_{}.xlsx".format(multiplication))
    plot_timings()

if __name__ == '__main__':
    main()
