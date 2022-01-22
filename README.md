# CourseManagementWebsite
Application Name: Coursework
 
Application Description: A web-application imitating ‘Canvas’, containing details about the courses for each university. The details are:
1. List the courses that a University offers
2. Details of the course
3. List and Details of Professors specific to each university
4. List of students belonging to a University
5. The courses taken by the student (A student can only take a course provided by it’s University)
6. Course material, assignments, grades

##Data Plan: 
Scrape “http://www.columbia.edu/cu/bulletin/uwb/” to get details of courses offered by the university and details such as Professor, Venue, Time, Credits. Extract similar information from the course directory website of a total of 3 universities. Extract Student details from ‘Columbia University’ student directory. Fabricate Assignment Entity Data.

## Actions
Users have following available actions:
1. Allow User to View Listed Courses
2. Allow User = Student to Submit Assignment
3. Allow User = Professor to Add Assignment
4. Allow User = Professor or Assistant to Grade Assignment
5. Allow User = Professor to Add Course_Assistant
6. Allow User = Admin to Add Users
7. Allow User = Professor to Add Courses
8. Allow User = Professor to Add Student to Courses
9. Allow User to View Course Assignments and Grades
10. Allow User = Admin to Add Venues

