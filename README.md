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

## 🖼 Screenshots

### Home Page
![Home Page](output/output1.png)

### Event Details / Profile Page
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

## Usage

- **Register/Login**: Users must register or log in to access event features.
- **Create Events**: Logged-in users can create events with details such as title, description, date, and category.
- **View Events**: Browse ongoing, upcoming, or completed events.
- **Interact**: Comment on events and engage with other participants.

---

## Contributing

Contributions are welcome! Please follow these steps:

```bash
# Fork the repository
# Create a new branch
git checkout -b feature-name

# Make your changes
# Commit your changes
git commit -m "Add some feature"

# Push to the branch
git push origin feature-name

# Submit a pull request
