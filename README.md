# 🚀 MyEventHub: Connect, Create, Conquer Events!

**MyEventHub** is a dynamic web application built with Django that revolutionizes how users explore, manage, and participate in events. Whether you're an organizer planning the next big gathering or an attendee looking for exciting activities, our platform offers a seamless, interactive experience.

---

## ✨ Features

| Feature | Description | Emoji |
|---------|-------------|-------|
| 🔐 **User Authentication** | Quick and secure registration and login via Django's built-in system. | 🔑 |
| 📝 **Event Management** | Create, edit, delete, and view events with ease. | ✍️ |
| 🔍 **Event Search & Filters** | Find events based on category, date, and location. | 🗂️ |
| 💬 **Comments & Notifications** | Interact with other users and get notified about updates. | 🛎️ |
| 👤 **User Profiles** | Personalized profiles with full details and editable information. | 🧑‍💻 |

---
## ⚙️ Architecture
![Architecture](output/Architecture.png)
- **🌐 Presentation Layer (HTML, CSS, JavaScript)
- This layer is responsible for user interaction and UI rendering.
- Built using Django templates
- Displays events, comments, and chat messages
- Sends user actions (login, join event, send message) to the backend via HTTP requests
- Contains no business logic — only data rendering and form submission

- **⚙️ Application Layer (Django Views, URLs)
- This layer acts as the request–response controller.
- Django views receive HTTP requests from the frontend
- URL routing maps requests to appropriate views
- Handles form validation, request parsing, and response generation
- Acts as the bridge between UI and business logic

-**🧠 Business Logic Layer (User App & Event App)
- This is the core of the system, where application rules are enforced.
- Split into two Django apps:
- User App: authentication, authorization, profiles
- Event App: event creation, joining, comments, chat access
- Enforces rules like:
  - Only joined users can access chat
  - Comments enabled/disabled per event
  - Keeps domain logic separate from views and templates
- **🛡️ Security Layer (Authentication, Middleware, CSRF)
- This layer ensures system safety and access control.
- Django authentication system for login/session management
- CSRF protection for all form submissions
- Middleware handles request filtering, sessions, and permissions
- Prevents unauthorized access to events and chatrooms
- **🗄️ Data Layer (MySQL via Django ORM)
- This layer manages data persistence and retrieval.
- MySQL database stores users, events, comments, and chat messages
- Django ORM abstracts raw SQL queries
- Ensures data consistency, integrity, and portability
---
## 🖼 Screenshots

### Home Page
![Home Page](output/output1.png)

### My Event Page
![Event/Profile Page](output/output2.png)

---

## ⚙️ Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/your-username/MyEventHub.git
    cd MyEventHub
    ```

2. **Create a virtual environment**
    ```bash
    python -m venv env
    # Linux/Mac
    source env/bin/activate
    # Windows
    env\Scripts\activate
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Apply migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. **Create a superuser (admin)**
    ```bash
    python manage.py createsuperuser
    ```

6. **Run the development server**
    ```bash
    python manage.py runserver
    ```

7. **Open the app**  
Visit `http://127.0.0.1:8000/` in your browser.

---
## 💡 Usage

- **📝 Register/Login**: Users must register or log in to access event features.  
- **🎉 Create Events**: Logged-in users can create events with details such as title, description, date, and category.  
- **👀 View Events**: Browse ongoing, upcoming, or completed events.  
- **💬 Interact**: Comment on events and engage with other participants.  

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

```bash
# 🍴 Fork the repository
# 🌿 Create a new branch
git checkout -b feature-name

# ✏️ Make your changes
# 💾 Commit your changes
git commit -m "Add some feature"

# 🚀 Push to the branch
git push origin feature-name

# 📩 Submit a pull request
