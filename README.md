# School Web Project

A web-based school management system built with **Django** and **Python**.

## 📌 About the Project

This project is designed to provide a simple platform for managing school-related information and activities.

The system includes different types of users and features for managing students, teachers, classes, lessons, homework, and other school-related data.

## 🚀 Features

* 👨‍🎓 Student management
* 👨‍🏫 Teacher management
* 👨‍👩‍👧 Parent profiles
* 🏫 Class management
* 📚 Lesson management
* 📝 Homework management
* 👤 User authentication and profiles
* 🔐 Different user roles and permissions

## 🛠️ Technologies

* **Python**
* **Django**
* **HTML**
* **CSS**
* **JavaScript**
* **SQLite** for development

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
```

### 2. Enter the project directory

```bash
cd YOUR-REPOSITORY
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Run the development server

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## 🔑 Creating an Admin User

To create a Django superuser:

```bash
python manage.py createsuperuser
```

Follow the instructions in the terminal.

## ⚠️ Important

This project is currently intended for **development and educational purposes**.

The database file and sensitive configuration files should not be uploaded to GitHub. Make sure files such as `.env` and `db.sqlite3` are included in `.gitignore`.

## 📄 License

This project is for educational purposes.
