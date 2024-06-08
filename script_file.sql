-- Drop existing tables
DROP TABLE IF EXISTS users, theory, practical, theorycourse, practicalcourse, project, departmentclasses, dept_duty;

-- Create Users table
CREATE TABLE users (
    faculty_id VARCHAR(50) PRIMARY KEY,
    f_name VARCHAR(100),
    password VARCHAR(100),
    entity VARCHAR(100),
    role_in_dept VARCHAR(100),
    CONSTRAINT entity_check CHECK (entity IN ('user', 'admin')),
    CONSTRAINT role_check CHECK (role_in_dept IN ('faculty', 'hod', 'non_teaching_staff')),
    Status VARCHAR(10) CHECK (Status IN ('Active', 'Inactive')),
    Designation VARCHAR(100) CHECK (Designation IN ('Assistant Professor', 'Associate Professor', 'HOD', 'Technician'))
);

-- Create TheoryCourse table
CREATE TABLE theorycourse (
    course_code VARCHAR(10) PRIMARY KEY,
    course_name VARCHAR(100)
);

-- Create PracticalCourse table
CREATE TABLE practicalcourse (
    course_code VARCHAR(10) PRIMARY KEY,
    course_name VARCHAR(100),
    hours INT
);

-- Create Theory table
CREATE TABLE theory (
    faculty_id VARCHAR(50),
    course_code VARCHAR(10),
    handled_duration VARCHAR(100),
    hours_per_week INT,
    FOREIGN KEY (faculty_id) REFERENCES users(faculty_id),
    FOREIGN KEY (course_code) REFERENCES theorycourse(course_code)
);

-- Create Practical table
CREATE TABLE practical (
    faculty_id VARCHAR(50),
    course_code VARCHAR(10),
    handled_duration VARCHAR(100),
    FOREIGN KEY (faculty_id) REFERENCES users(faculty_id),
    FOREIGN KEY (course_code) REFERENCES practicalcourse(course_code)
);

-- Create Project table
CREATE TABLE project (
    faculty_id VARCHAR(50),
    course_code VARCHAR(10),
    project_name VARCHAR(100),
    handled_duration VARCHAR(100),
    FOREIGN KEY (faculty_id) REFERENCES users(faculty_id),
    FOREIGN KEY (course_code) REFERENCES practicalcourse(course_code)
);

-- Create DepartmentClasses table
CREATE TABLE departmentclasses (
    section VARCHAR(10),
    batch VARCHAR(50),
    strength INT,
    PRIMARY KEY (section, batch)
);

-- Create Dept_duty table
CREATE TABLE dept_duty (
    faculty_id VARCHAR(50),
    Responsibilities VARCHAR(100),
    FOREIGN KEY (faculty_id) REFERENCES users(faculty_id)
);

CREATE TABLE duty (
    duty VARCHAR(500)
);








    









