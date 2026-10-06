-- Students → Courses → Enrollments  (many-to-many)
-- Run: psql -U postgres -f school.sql
DROP DATABASE IF EXISTS school;
CREATE DATABASE school;
\c school

CREATE SCHEMA uni;                       -- a folder for related tables
SET search_path TO uni, public;

CREATE TABLE students (
    id      SERIAL PRIMARY KEY,
    name    TEXT NOT NULL,
    email   TEXT UNIQUE NOT NULL,
    age     INT CHECK (age >= 16),
    created TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE courses (
    id      SERIAL PRIMARY KEY,
    title   TEXT NOT NULL UNIQUE,
    credits INT NOT NULL DEFAULT 3 CHECK (credits BETWEEN 1 AND 6)
);

-- the "middle" table that makes many-to-many work
CREATE TABLE enrollments (
    student_id INT REFERENCES students(id) ON DELETE CASCADE,
    course_id  INT REFERENCES courses(id),
    grade      CHAR(1) CHECK (grade IN ('A','B','C','D','F')),
    PRIMARY KEY (student_id, course_id)  -- a student can't enrol twice
);

-- one-to-one: each student has at most one profile
CREATE TABLE student_profiles (
    student_id INT PRIMARY KEY REFERENCES students(id) ON DELETE CASCADE,
    bio        TEXT
);

INSERT INTO students (name, email, age) VALUES
 ('Ayesha Khan','ayesha@uni.edu',21), ('Bilal Ahmed','bilal@uni.edu',22), ('Sara Malik','sara@uni.edu',20);
INSERT INTO courses (title, credits) VALUES ('Databases',4), ('Algorithms',3), ('Operating Systems',3);
INSERT INTO enrollments VALUES (1,1,'A'), (1,2,'B'), (2,1,'B'), (3,3,'A');
INSERT INTO student_profiles VALUES (1,'Loves SQL');

-- VIEW: a saved query that behaves like a table
CREATE VIEW student_courses AS
SELECT s.name, c.title, e.grade
FROM students s JOIN enrollments e ON e.student_id = s.id
                JOIN courses c     ON c.id = e.course_id;

-- SEQUENCE: a counter (SERIAL creates one for you)
CREATE SEQUENCE receipt_no START 1000;

-- FUNCTION
CREATE FUNCTION gpa_points(g CHAR) RETURNS NUMERIC AS $$
    SELECT CASE g WHEN 'A' THEN 4 WHEN 'B' THEN 3 WHEN 'C' THEN 2 WHEN 'D' THEN 1 ELSE 0 END;
$$ LANGUAGE sql IMMUTABLE;

-- TRIGGER: auto-log every grade change
CREATE TABLE grade_log (student_id INT, course_id INT, old_grade CHAR(1), new_grade CHAR(1), changed_at TIMESTAMPTZ DEFAULT now());

CREATE FUNCTION log_grade_change() RETURNS trigger AS $$
BEGIN
    IF NEW.grade IS DISTINCT FROM OLD.grade THEN
        INSERT INTO grade_log VALUES (OLD.student_id, OLD.course_id, OLD.grade, NEW.grade);
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_grade_change
AFTER UPDATE ON enrollments
FOR EACH ROW EXECUTE FUNCTION log_grade_change();
