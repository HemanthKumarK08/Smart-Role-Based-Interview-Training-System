A modern desktop-based interview preparation application built using **Python**, **CustomTkinter**, and **SQLite** that helps students prepare for role-specific interviews through realistic interview simulations, automated evaluation, performance analytics, and detailed reports.

---

## 📌 Overview

The **Smart Role-Based Interview Training System** is designed to simulate real-world technical interviews. Students can practice interviews based on their selected **job role** and **difficulty level**, while administrators can efficiently manage question banks, students, interview analytics, and reports.

The system provides a structured interview experience with multiple interview rounds and instant performance evaluation.

---

## ✨ Key Features

### 👨‍🎓 Student Module

- Student Registration & Login
- Profile Management
- Role Selection
- Difficulty Selection
- Random Question Selection
- MCQ Round
- Technical Interview Round
- HR Interview Round
- Coding Output Round
- Instant Evaluation
- Performance Reports
- Perfect Answer Review
- Export Results (CSV)
- Interview History

---

### 👨‍💼 Admin Module

- Secure Admin Login
- Dashboard
- Role Management
- Manual Question Creation
- Bulk Question Upload
- CSV Upload Support
- DOCX Upload Support
- Download Question Templates
- Question Search & Filters
- Student Management
- Performance Analytics
- Export Results
- Admin Profile Management

---

## 🎯 Interview Workflow

<img width="1440" height="1932" alt="image" src="https://github.com/user-attachments/assets/fed4ca94-7f3e-450b-8041-5f7a3b706e9d" />


---

## 🧠 Interview Rounds

### 📘 MCQ Round

- Random multiple-choice questions
- Automatic evaluation

---

### 💻 Technical Round

- Descriptive technical questions
- Keyword-based evaluation
- Automatic scoring

---

### 👨‍💼 HR Round

- Behavioral and HR questions
- Confidence analysis
- Keyword matching
- Feedback generation

---

### 👨‍💻 Coding Output Round

Students **do not write code**.

Instead, they:

- Read a code snippet
- Analyze its logic
- Select the correct output

This evaluates logical thinking and programming concepts without requiring a compiler.

---

## 📊 Performance Evaluation

The system automatically evaluates students based on:

- MCQ Score
- Technical Score
- Coding Score
- HR Score
- Overall Percentage
- Personalized Feedback

---

## 📂 Bulk Question Upload

The administrator can upload questions in bulk using:

- ✅ CSV
- ✅ DOCX

Supported Question Types:

- MCQ
- Technical
- Coding
- HR

Features:

- Duplicate Detection
- Validation
- Role Assignment
- Difficulty Assignment
- Template Download

---

## 🎲 Random Question Selection

The system supports large question banks.

Example:

Software Developer

MCQ        : 80 Questions
Technical  : 60 Questions
Coding     : 50 Questions
HR          : 40 Questions

Each interview randomly selects questions, ensuring a unique interview experience every time.

---

## 🛠 Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3.11 | Core Programming |
| CustomTkinter | Modern Desktop GUI |
| SQLite | Database |
| python-docx | DOCX Processing |
| CSV Module | Bulk Upload |
| Hashlib | Password Security |
| Regex | Validation |
| Git | Version Control |

---

## 📁 Project Structure

Smart-Role-Based-Interview-Training-System/

├── assets/
├── database/
│   └── interview.db
├── admin.py
├── auth.py
├── database.py
├── feedback_engine.py
├── interview_engine.py
├── main.py
├── student.py
├── utils.py
├── requirements.txt
└── README.md

---

## 🔒 Security Features

- SHA-256 Password Hashing
- Secure Authentication
- Email Validation
- Session Management
- Input Validation
- Duplicate Question Prevention

---

## 📈 Admin Dashboard

The administrator can monitor:

- Total Students
- Total Roles
- Total Questions
- Interview Statistics
- Question Distribution
- Student Performance
- Recent Activities
- Exportable Reports

---

## 🚀 Getting Started

### Clone the Repository

bash
https://github.com/HemanthKumarK08/Smart-Role-Based-Interview-Training-System

### Navigate to Project

bash
cd Smart-Role-Based-Interview-Training-System


### Install Dependencies

bash
pip install -r requirements.txt


### Run the Application

bash
python main.py

or

bash
python3.11 main.py

---

## 🔮 Future Enhancements

- AI-based Answer Evaluation
- Voice Interview Simulation
- Resume Analysis
- Company-specific Interview Sets
- Online Interview Mode
- Certificate Generation
- Cloud Database Support
- Multi-language Support

---

## 👨‍💻 Author

**Hemanth Kumar K**

MCA Student | Bangalore Institue Of Technology, Bengaluru

---
