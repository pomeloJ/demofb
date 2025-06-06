# 📘 Simple Facebook DEMO Application

A simple social media demo application that mimics basic Facebook functionality. Users can register, login, create posts, view others' posts, and leave comments.

## 🧭 Project Overview

This project is a lightweight social media demo that demonstrates:
- User registration and authentication
- User post creation
- Comment functionality
- Server-side rendering with Jinja2 templates
- HTMX for interactive UI without JavaScript
- Session management for user authentication
- In-memory data storage (no database required)

## 🛠 Technology Stack

* **Frontend**: HTML, CSS, HTMX
* **Backend**: Python (FastAPI)
* **Template Engine**: Jinja2
* **Data Storage**: In-memory (Python dictionaries)

## 📦 Project Structure

```
project_root/
├── main.py                # FastAPI application
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base template with layout
│   ├── posts.html         # Posts page template
│   ├── posts_content.html # Posts content for HTMX requests
│   ├── post_item.html     # Single post template
│   ├── comment_item.html  # Single comment template
│   ├── comment_list.html  # Comments list template
│   ├── login.html         # User login form
│   └── register.html      # User registration form
├── static/                # Static assets
│   └── styles.css         # CSS styles
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## 🔧 Installation & Setup

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:

- Windows:
```bash
venv\Scripts\activate
```

- macOS/Linux:
```bash
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Additional dependency for session management:

```bash
pip install itsdangerous
```

## 🚀 Running the Application

Start the application with:

```bash
uvicorn main:app --reload
```

The application will be accessible at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 🌟 Features

1. **User Authentication**
   - User registration with username and password
   - User login/logout functionality
   - Session management for persistent login

2. **Post Creation**
   - Authenticated users can create posts
   - Posts display author name and creation time

3. **Comment System**
   - Authenticated users can comment on any post
   - Comments are loaded dynamically with HTMX
   - Real-time comment display

4. **Responsive Design**
   - Clean, Facebook-inspired interface
   - Works on mobile and desktop
   
5. **Security**
   - Protected routes requiring authentication
   - Session-based authentication

## 📝 Future Enhancements

- Add persistent data storage with a database
- Add like/reaction functionality
- Support for image/media uploads
- User profiles and friend connections
- Password hashing for secure authentication
- Email verification for user registration
