# 🎓 Scholarship Management Portal

A web-based Scholarship Management Portal developed using Python Flask, HTML, CSS, JavaScript, and SQLite. This application helps students explore scholarships, check sample eligibility criteria, submit applications, upload required documents, and track application status.

## 🚀 Features

- **Home Dashboard:** View portal overview and statistics.
- **Scholarship Information:** Explore available scholarship options.
- **Eligibility Checker:** Check sample eligibility based on academic marks and family income.
- **Student Registration:** Register student details, including name, email, course, and college.
- **Document Upload:** Upload required supporting documents.
- **Scholarship Application:** Submit scholarship applications with academic and income details.
- **Application Status:** Track submitted applications and view their current status.
- **Student Profile:** View student and application information.

## 🛠️ Technologies Used

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Database:** SQLite
- **Development Tools:** Visual Studio Code, Git, GitHub

## 📂 Project Structure

```text
Scholarship-Management-Portal/
│
├── app.py
├── .gitignore
│
├── static/
│   ├── style.css
│   └── script.js
│
└── templates/
    ├── index.html
    ├── scholarships.html
    ├── eligibility.html
    ├── profile.html
    ├── documents.html
    ├── application.html
    ├── status.html
    └── student_profile.html
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/gowthamimurakonda2928/Scholarship-Management-Portal.git
```

### 2. Navigate to the Project Folder

```bash
cd Scholarship-Management-Portal
```

### 3. Install Dependencies

```bash
pip install flask
```

### 4. Run the Application

```bash
python app.py
```

### 5. Open in Browser

Visit the following URL in your browser:

```text
http://127.0.0.1:5000
```

## 🔮 Future Enhancements

- Student and administrator authentication
- Integration with official scholarship databases
- Email notifications for application updates
- Improved application verification and approval workflow
- Secure document storage and persistent database
