login_query = \
"""
SELECT * FROM user_info 
WHERE user_email=(%s) AND user_password=(%s)
"""

user_details_query = \
"""
SELECT * FROM user_info 
WHERE user_id=(%s)
"""

admin_details = \
"""
SELECT * FROM admin 
WHERE user_id=(%s)
"""

prof_details = \
"""
SELECT * FROM professor 
WHERE user_id=(%s)
"""

student_details = \
"""
SELECT * FROM student 
WHERE user_id=(%s)
"""

university_details_query = \
"""
SELECT * FROM university 
WHERE university_id=(%s)
"""

registered_courses_student = \
"""
SELECT course_id, course_name FROM Course 
WHERE course_id in 
(
SELECT course_id FROM registered 
WHERE user_id=(%s)
)
AND
is_active=(%s)
"""

update_course_status = \
"""
"""

courses_prof = \
"""
SELECT course_id, course_name FROM Course 
WHERE course_id in 
(
SELECT course_id FROM course_prof 
WHERE user_id=(%s)
)
AND
is_active=(%s)
"""

courses_ta = \
"""
SELECT course_id, course_name FROM Course 
WHERE course_id in 
(
SELECT course_id FROM assists 
WHERE user_id=(%s)
)
AND
is_active=(%s)
"""

prof_of_course = \
"""
SELECT * FROM course_prof 
WHERE course_id=(%s)
AND user_id=(%s)
"""

ta_of_course = \
"""
SELECT * FROM assists 
WHERE course_id=(%s)
AND user_id=(%s)
"""

student_of_course = \
"""
SELECT * FROM registered 
WHERE course_id=(%s)
AND user_id=(%s)
"""

prof_of_course_details = \
"""
SELECT * FROM (
SELECT * FROM course_prof 
WHERE course_id=(%s)) P
JOIN (SELECT * FROM user_info) U
ON (P.user_id=U.user_id)
"""

ta_of_course_details = \
"""
SELECT * FROM (
SELECT * FROM assists 
WHERE course_id=(%s)) T
JOIN (SELECT * FROM user_info) U
ON (T.user_id=U.user_id)
"""

student_of_course_details = \
"""
SELECT * FROM (
SELECT * FROM registered 
WHERE course_id=(%s)) S
JOIN (SELECT * FROM user_info) U
ON (S.user_id=U.user_id)
"""

get_course_details = \
"""
SELECT 
course_id, course_name, user_description,
course_credits, course_year, course_semester,
venue_id, course_time_slot, is_course_online, is_active, university_id
FROM Course
WHERE course_id=(%s)
"""

get_course_details_all = \
"""
SELECT * FROM Course
WHERE university_id=(%s)
"""

get_student_details_all = \
"""
SELECT * FROM 
(SELECT * FROM Student) S JOIN (
    SELECT * FROM user_info
    WHERE university_id=(%s)
) U ON (S.user_id=U.user_id)
"""

get_professor_details_all = \
"""
SELECT * FROM 
(SELECT * FROM Professor) S JOIN (
    SELECT * FROM user_info
    WHERE university_id=(%s)
) U ON (S.user_id=U.user_id)
"""

get_student_details_all_not_registered_and_not_ta_in_course = \
"""
SELECT * FROM 
(SELECT * FROM Student WHERE user_id NOT IN (SELECT user_id FROM registered WHERE course_id=(%s)) AND user_id NOT IN (SELECT user_id FROM assists WHERE course_id=(%s))) S JOIN (
    SELECT * FROM user_info
    WHERE university_id=(%s)
) U ON (S.user_id=U.user_id)
"""

get_professor_details_all_not_in_course = \
"""
SELECT * FROM 
(SELECT * FROM Professor WHERE user_id NOT IN (SELECT user_id FROM course_prof WHERE course_id=(%s))) S JOIN (
    SELECT * FROM user_info
    WHERE university_id=(%s)
) U ON (S.user_id=U.user_id)
"""

get_venue_details_all = \
"""
SELECT * FROM venue
WHERE university_id=(%s)
"""

get_course_assignments = \
"""
SELECT
assignment_id, assignment_name, 
TO_CHAR(assignment_posted_date, 'DD MON, HH:MI') assignment_posted_date, 
TO_CHAR(assignment_due_date, 'DD MON, HH:MI') assignment_due_date,
total_marks
FROM Assignment
WHERE course_id=(%s)
"""

get_assignment_data = \
"""
SELECT * FROM Assignment
WHERE assignment_id=(%s)
"""

get_venue = \
"""
SELECT * FROM Venue
WHERE university_id=(%s)
"""

get_venue_by_venue_id = \
"""
SELECT * FROM Venue
WHERE venue_id=(%s)
"""


get_assignment_submission_data = \
"""
SELECT * FROM(
SELECT * FROM Submits
WHERE assignment_id = (%s)
AND user_id = (%s)
) S JOIN (
SELECT * FROM Assignment
) A
ON S.assignment_id=A.assignment_id
"""

get_assignment_submission_statistics = \
"""
SELECT MAX(S.marks_obtained) AS max, MIN(S.marks_obtained) AS min, AVG(S.marks_obtained) AS avg FROM(
(SELECT * FROM Registered WHERE
course_id IN (
SELECT course_id FROM Assignment
WHERE assignment_id = (%s))) R JOIN (SELECT * from submits WHERE assignment_id = (%s)) S ON (R.user_id=S.user_id)
)
"""

get_assignment_submission_data_all = \
"""
SELECT *, R.user_id as user_id FROM(
SELECT * FROM Registered WHERE
course_id IN (
SELECT course_id FROM Assignment
WHERE assignment_id = (%s)
)) R JOIN (
SELECT * FROM user_info
) U
ON R.user_id=U.user_id LEFT JOIN (
    SELECT * FROM submits
    WHERE assignment_id=(%s)
) S ON (R.user_id=S.user_id)
"""

create_assignment_query = \
"""
INSERT INTO Assignment VALUES ((%s), (%s), (%s), (%s), (%s), (%s));
"""

create_admin_query = \
"""
INSERT INTO user_info VALUES ((%s), (%s), (%s), (%s), (%s), (%s));
INSERT INTO admin VALUES ((%s), (%s));
"""

create_uni_query = \
"""
INSERT INTO university VALUES ((%s), (%s), (%s), (%s), (%s), (%s), (%s));
"""

create_course_query = \
"""
INSERT INTO course VALUES ((%s), (%s), (%s), (%s), (%s), (%s), (%s), (%s), (%s), (%s), (%s))
"""

create_student_query = \
"""
INSERT INTO user_info VALUES ((%s), (%s), (%s), (%s), (%s), (%s));
INSERT INTO student VALUES ((%s), (%s), (%s));
"""

create_professor_query = \
"""
INSERT INTO user_info VALUES ((%s), (%s), (%s), (%s), (%s), (%s));
INSERT INTO professor VALUES ((%s), (%s));
"""

create_venue_query = \
"""
INSERT INTO venue VALUES ((%s), (%s), (%s), (%s));
"""

delete_assignment_query = \
"""
DELETE FROM Assignment WHERE assignment_id=(%s);
"""

delete_course_query = \
"""
DELETE FROM Course WHERE course_id=(%s);
"""

delete_university_query = \
"""
DELETE FROM university WHERE university_id=(%s);
"""

delete_user_query = \
"""
DELETE FROM user_info WHERE user_id=(%s);
"""

delete_venue_query = \
"""
DELETE FROM venue WHERE venue_id=(%s);
"""

submit_assignment_material_first = \
"""
INSERT INTO Submits VALUES ((%s), (%s), (%s));
"""

submit_assignment_material_update = \
"""
UPDATE Submits SET
submitted_material = (%s)
WHERE assignment_id = (%s)
AND user_id = (%s);
"""

give_assignment_marks_first = \
"""
INSERT INTO Submits VALUES ((%s), (%s), (%s), (%s));
"""

add_course_profs = \
"""
INSERT INTO course_prof VALUES ((%s), (%s));
"""

add_course_students = \
"""
INSERT INTO registered VALUES ((%s), (%s));
"""

add_course_tas = \
"""
INSERT INTO assists VALUES ((%s), (%s));
"""

remove_course_profs = \
"""
DELETE FROM course_prof WHERE course_id=(%s) AND user_id= (%s);
"""

remove_course_students = \
"""
DELETE FROM registered WHERE course_id=(%s) AND user_id= (%s);
"""

remove_course_tas = \
"""
DELETE FROM assists WHERE course_id=(%s) AND user_id= (%s);
"""

give_assignment_marks_update = \
"""
UPDATE Submits SET
marks_obtained = (%s)
WHERE assignment_id = (%s)
AND user_id = (%s);
"""

update_user_query = \
"""
UPDATE user_info SET
(user_first_name, user_last_name, user_password) = ((%s), (%s), (%s))
WHERE user_id = (%s);
"""

update_course_query = \
"""
UPDATE course SET 
(course_name, user_description, course_credits, is_active, course_year, course_semester, venue_id, course_time_slot, is_course_online)=((%s), (%s), (%s), (%s), (%s), (%s), (%s), (%s), (%s))  
WHERE course_id=(%s);
"""

update_university_query = \
"""
UPDATE university SET
(university_city, university_state, university_address, university_pincode, university_establishment_date) = ((%s), (%s), (%s), (%s), (%s))
WHERE university_id = (%s);
"""

update_venue_query = \
"""
UPDATE venue SET 
(venue_building, venue_class_number)=((%s), (%s))  
WHERE venue_id=(%s);
"""

update_assignment_query = \
"""
UPDATE assignment SET 
(assignment_name, assignment_posted_date, assignment_due_date, total_marks)=((%s), (%s), (%s), (%s))  
WHERE assignment_id=(%s);
"""

get_current_credits_per_sem = \
"""
SELECT SUM(course_credits) AS credits_already_registered FROM course WHERE (course_semester, course_year) in
(SELECT course_semester, course_year FROM course 
WHERE course_id='418757') AND course_id IN (SELECT course_id FROM registered WHERE user_id='23980')
"""

