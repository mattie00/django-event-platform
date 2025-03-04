# Platform for event management and online ticket sales

### This platform is a comprehensive solution that enables administrators to add and edit events, while users can intuitively browse available offers, performers, and purchase tickets online. The application is modular and scalable, allowing for further development and integration of additional functionalities.

## 🚀 Features

### For Users

- Browse events with advanced filtering (name, category, tags, city)
- Purchase tickets online and generate PDF tickets and invoices
- Receive email notifications (registration, purchase, password changes)
- View detailed event and artist information
- Access purchase history and use the favorites system
- Enjoy a responsive design with search by artist/city
- Check out promotions and highlighted events

### For Administrators

- Manage events (create, edit, delete)
- Add a wide range of ticket types and manage orders
- Control ticket pools and promotions
- Access an analytics dashboard with key statistics
- Manage user accounts

---

## 🛠️ Technologies Used

- **Backend:**
  - **Django (v5.1.3)** – Advanced Python web framework for building scalable and secure applications.
  - **PyMySQL (v1.1.1)** – Library for integrating with MySQL, used by Django for database operations.
  - **python-decouple (v3.8)** – Tool for managing environment variables, enabling secure storage of settings (e.g. secret key, database credentials) in a `.env` file.

- **Frontend:**
  - **HTML, CSS, JavaScript** – Core technologies for creating the user interface.
  - **Bootstrap (v5.3.3)** – CSS/JS framework that facilitates the rapid development of responsive and modern interfaces.

- **Additional Functionality:**
  - **qrcode (v8.0)** – Library for generating QR codes, useful for ticket creation.
  - **xhtml2pdf (v0.2.16)** – Tool for converting HTML documents to PDF format, used for generating tickets and invoices.

---

## 📂 Project Structure

- **`config/`**: Core Django settings and configurations.
- **`authentication/`**: User authentication and profile management.
- **`events/`**: Models and views related to events and ticket pools.
- **`orders/`**: Checkout and ticketing logic.
- **`static/`**: CSS, JS, and image files.
- **`templates/`**: All HTML templates for the project.

---

## 📌 Installation and Configuration

1. **Clone the repository**:
```bash
https://github.com/mattie00/django-event-platform.git
```

2. **Create a `.env` file**:
In the project's root directory, create a `.env` file and fill it with the following example configuration:
```ini
# Django secret key
SECRET_KEY=django-insecure-example_key

# Database configuration
DB_NAME=database_name
DB_USER=user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306

# Email server configuration
EMAIL_USE_TLS=True
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_password
EMAIL_PORT=587
DEFAULT_FROM_EMAIL=your_email@example.com
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Apply database migrations**:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Run the development server**:
```bash
python manage.py runserver
```

The application will be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## 📜 License

This project is licensed under the [MIT License](LICENSE).
