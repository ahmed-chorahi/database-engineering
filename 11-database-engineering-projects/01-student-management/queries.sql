\c sms
-- CRUD
INSERT INTO students (name, email, dept_id) VALUES ('Zainab Noor','zainab@uni.edu',2) RETURNING id;
UPDATE students SET email = 'zainab.n@uni.edu' WHERE name = 'Zainab Noor';
DELETE FROM students WHERE name = 'Zainab Noor';

-- 1. Students and their department
SELECT s.name, d.name AS department FROM students s JOIN departments d ON d.id = s.dept_id ORDER BY s.name;

-- 2. Average marks per course
SELECT c.code, c.title, ROUND(AVG(e.marks),1) AS avg_marks, COUNT(e.marks) AS graded
FROM courses c LEFT JOIN enrollments e ON e.course_id = c.id GROUP BY c.id ORDER BY c.code;

-- 3. Top student per course (window function)
SELECT code, name, marks FROM (
  SELECT c.code, s.name, e.marks, RANK() OVER (PARTITION BY c.id ORDER BY e.marks DESC) AS r
  FROM enrollments e JOIN students s ON s.id=e.student_id JOIN courses c ON c.id=e.course_id
  WHERE e.marks IS NOT NULL) t WHERE r = 1 ORDER BY code;

-- 4. Students not enrolled in any course
SELECT name FROM students s WHERE NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.student_id = s.id);

-- 5. Weighted GPA-style score
SELECT s.name, ROUND(SUM(e.marks * c.credits)::numeric / SUM(c.credits), 1) AS weighted_avg
FROM students s JOIN enrollments e ON e.student_id=s.id JOIN courses c ON c.id=e.course_id
WHERE e.marks IS NOT NULL GROUP BY s.name ORDER BY weighted_avg DESC;
