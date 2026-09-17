# Careline Hospital Management System

A Django REST Framework foundation for a production hospital management system, aligned with the existing Careline Medical Centre demo direction. The local workspace started empty, so the frontend shell and backend are new implementations based on the supplied reference site.

## Current implementation

- Django 5 + Django REST Framework
- MySQL configuration through environment variables
- Custom user model with all requested staff roles
- Secure Django password hashing
- Token and session authentication
- Login, logout, registration, and current-user endpoints
- Audit logging for authentication and core CRUD actions
- Departments, patients, doctors, and nurses with relational models
- Administrator-only writes and authenticated reads
- Search, filtering, ordering, and pagination on core API endpoints
- Database-backed dashboard counts
- Responsive Careline-aligned frontend shell connected to the API
- Appointments, admissions, wards/rooms/beds, medical records, prescriptions, and vital signs
- Pharmacy medicines and stock movements with low-stock-ready data
- Laboratory tests, invoices/items, payments, insurance providers/claims, and inventory
- User-scoped notifications and a reports summary endpoint

The remaining production hardening includes automated notification generation, password-reset email delivery, richer report export/printing, and end-to-end tests against a configured MySQL instance.

## Setup

1. Install Python 3.12+ and MySQL 8+.
2. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
```

3. Create a MySQL database and user, then copy `.env.example` to `.env` and fill in the values. Never commit `.env`.
4. Generate and apply migrations:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

5. Serve the frontend from a second terminal so browser requests work cleanly:

```powershell
python -m http.server 5500 --directory frontend
```

Open `http://127.0.0.1:5500`. The API is at `http://127.0.0.1:8000/api/` and Django admin is at `/admin/`.

## API

- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `POST /api/auth/register/`
- `GET /api/auth/me/`
- `GET /api/dashboard/`
- `/api/departments/`
- `/api/patients/`
- `/api/doctors/`
- `/api/nurses/`

Use `Authorization: Token <token>` for API requests. DRF browsable API and Django admin provide development inspection tools.

## Production checklist

Set `DJANGO_DEBUG=False`, use a strong generated `DJANGO_SECRET_KEY`, configure explicit hosts and CORS origins, serve static assets through a web server, use HTTPS, rotate tokens, configure backups and monitoring, and run migrations as a deployment step. MySQL credentials must only exist in the deployment environment.

For Render, set `DJANGO_ALLOWED_HOSTS` to `hospital-management-1-tm09.onrender.com` and set `CORS_ALLOWED_ORIGINS` to the exact origin serving the frontend, separated by commas. For the local frontend server, use `http://localhost:5500,http://127.0.0.1:5500`. After changing Render environment variables or deploying this settings change, redeploy the service so Django reloads the configuration.
