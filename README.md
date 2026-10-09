# TaskFlow — Django REST Framework Workflow & Task Engine

[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.18-red.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready task and workflow management REST API engineered with **Django**, **Django REST Framework (DRF)**, **SimpleJWT**, and **PostgreSQL**. Features strict MVT/MVC separation, email-based authentication with a custom user model, fine-grained object permissions, composite database indexing, N+1 query prevention, automated OpenAPI 3.0 Swagger documentation, and a 100% passing test suite.

---

## 🏛️ System Architecture

TaskFlow adopts clean **MVT (Model-View-Template) / MVC** architecture for clear separation of concerns:

```
taskflow-django/
├── config/              # Root project configuration, routing, and environment settings
│   ├── settings.py      # Dual-database configuration, DRF settings, JWT and Swagger config
│   └── urls.py          # Master route registry (v1 API + OpenAPI Docs + Django Admin)
├── accounts/            # Authentication & Identity Subsystem
│   ├── models.py        # Custom User model (AbstractUser, email login, role metadata)
│   ├── serializers.py   # JWT registration, password validation, user detail serializers
│   ├── views.py         # Registration, profile management, and password change views
│   └── tests.py         # Automated auth and JWT verification test suite
├── tasks/               # Workflow & Task Management Domain
│   ├── models.py        # Project, Task, and TaskComment with composite indexing
│   ├── serializers.py   # Nested & list serializers with validation
│   ├── views.py         # ModelViewSets with select_related / prefetch_related
│   ├── permissions.py   # IsOwnerOrReadOnly object-level permission enforcement
│   └── tests.py         # Comprehensive CRUD, filter, and transition test suite
├── docker-compose.yml   # Multi-container orchestration (Django + PostgreSQL)
└── Dockerfile           # Optimized Python container build
```

---

## ⚡ Core Engineering Highlights

- **Custom User Model & JWT Authentication:** Extended `AbstractUser` with unique email authentication, role-based metadata (`DEVELOPER`, `LEAD`, `MANAGER`), and stateless token lifecycle management via `djangorestframework-simplejwt`.
- **Query Optimization & Zero N+1 Problem:** All list and detail queries use `select_related` on foreign keys (`owner`, `project`, `creator`, `assignee`) and `prefetch_related` on many-to-one reverse relations (`tasks`, `comments__author`), maintaining $O(1)$ database hits.
- **Composite Database Indexing:** Defined indexes across `['status', 'priority']` and `['project', 'status']` on relational models for high-speed filter queries under scale.
- **Custom ViewSet Actions:** Built a dedicated `@action(detail=True, methods=['post'], url_path='status')` endpoint to enforce auditable state transitions across task workflows (`BACKLOG` $\rightarrow$ `TODO` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `IN_REVIEW` $\rightarrow$ `DONE`).
- **Interactive OpenAPI 3.0 Specs:** Real-time interactive documentation generated via `drf-spectacular` accessible on Swagger UI and Redoc.
- **Dual Database Resilience:** Instant out-of-the-box local operation using SQLite, with seamless switch to PostgreSQL in staging/production via `.env` or Docker Compose.

---

## 📡 API Endpoints Directory

### 🔐 Authentication (`/api/v1/auth/`)
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/api/v1/auth/register/` | Register new account & return JWT pair | Public |
| `POST` | `/api/v1/auth/token/` | Obtain Access and Refresh JWT | Public |
| `POST` | `/api/v1/auth/token/refresh/` | Refresh access token | Public |
| `GET` | `/api/v1/auth/profile/` | Retrieve current user profile | Authenticated |
| `PUT/PATCH` | `/api/v1/auth/profile/` | Update profile details | Authenticated |
| `POST` | `/api/v1/auth/change-password/` | Change account password | Authenticated |

### 📋 Projects & Tasks (`/api/v1/`)
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/api/v1/projects/` | List projects (with search & ordering) | Authenticated |
| `POST` | `/api/v1/projects/` | Create a new project (auto-slugified) | Authenticated |
| `GET` | `/api/v1/projects/{id}/` | Get project detail | Authenticated |
| `PUT/PATCH` | `/api/v1/projects/{id}/` | Update project | Owner Only |
| `DELETE` | `/api/v1/projects/{id}/` | Delete project | Owner Only |
| `GET` | `/api/v1/tasks/` | List tasks (filter by status, priority, project) | Authenticated |
| `POST` | `/api/v1/tasks/` | Create a new task | Authenticated |
| `GET` | `/api/v1/tasks/{id}/` | Get full task detail + comments | Authenticated |
| `POST` | `/api/v1/tasks/{id}/status/` | Custom transition action for task status | Authenticated |
| `GET` | `/api/v1/comments/?task={id}` | List comments for a task | Authenticated |
| `POST` | `/api/v1/comments/` | Add comment to a task | Authenticated |

### 📖 Documentation & Schema
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/schema/` | Raw OpenAPI 3.0 YAML/JSON Schema |
| `GET` | `/api/docs/swagger/` | Interactive Swagger UI Dashboard |
| `GET` | `/api/docs/redoc/` | Redoc Technical API Documentation |

---

## 🛠️ Quickstart Guide

### Option 1: Local Setup (SQLite / PostgreSQL)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rahulxgit/taskflow-django.git
   cd taskflow-django
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux / macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start development server:**
   ```bash
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000/api/docs/swagger/` in your browser.

---

### Option 2: Run with Docker Compose (PostgreSQL)

```bash
docker-compose up --build
```
This spins up PostgreSQL 16 and the Django REST service on `http://localhost:8000`.

---

## 🧪 Running Automated Tests

Execute the comprehensive test suite verifying authentication, permission boundaries, and REST CRUD flows:

```bash
python manage.py test
```

Expected output:
```text
Found 11 test(s).
Creating test database for alias 'default'...
...........
----------------------------------------------------------------------
Ran 11 tests in 1.2s

OK
Destroying test database for alias 'default'...
```

---

## 👨‍💻 Author

**Rahul Kumar**  
- **GitHub:** [@rahulxgit](https://github.com/rahulxgit)  
- **LinkedIn:** [linkedin.com/in/rahulxnit](https://www.linkedin.com/in/rahulxnit/)  
- **Portfolio:** [rahul-portfolio](https://rahul-portfolio-eight-eta.vercel.app/)  
