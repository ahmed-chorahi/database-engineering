DROP DATABASE IF EXISTS sms;
CREATE DATABASE sms;
\c sms

CREATE TABLE departments (id SERIAL PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE students (
    id SERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
    dept_id INT NOT NULL REFERENCES departments(id), enrolled_on DATE NOT NULL DEFAULT CURRENT_DATE);
CREATE TABLE courses (
    id SERIAL PRIMARY KEY, code TEXT NOT NULL UNIQUE, title TEXT NOT NULL,
    credits INT NOT NULL CHECK (credits BETWEEN 1 AND 6), dept_id INT NOT NULL REFERENCES departments(id));
CREATE TABLE enrollments (
    student_id INT REFERENCES students(id) ON DELETE CASCADE,
    course_id  INT REFERENCES courses(id),
    marks      INT CHECK (marks BETWEEN 0 AND 100),
    PRIMARY KEY (student_id, course_id));

INSERT INTO departments (name) VALUES ('Computer Science'), ('Mathematics');
INSERT INTO students (name, email, dept_id) VALUES
 ('Ayesha Khan','ayesha@uni.edu',1), ('Bilal Ahmed','bilal@uni.edu',1),
 ('Sara Malik','sara@uni.edu',2),    ('Hamza Ali','hamza@uni.edu',1),
 ('Usman Tariq','usman@uni.edu',2);   -- not enrolled anywhere, on purpose
INSERT INTO courses (code, title, credits, dept_id) VALUES
 ('CS201','Databases',4,1), ('CS202','Algorithms',3,1), ('MA101','Calculus',3,2);
INSERT INTO enrollments VALUES (1,1,91),(1,2,84),(2,1,72),(2,3,65),(3,3,88),(4,1,NULL);
