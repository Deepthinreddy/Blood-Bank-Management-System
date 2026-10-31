# Blood Bank Management System (BBMS)

A web-based Software Engineering project developed using Django to manage blood donors, donations, blood inventory, recipients, blood requests, and administrative operations.

The system centralizes blood-bank records and supports donation recording, inventory tracking, blood allocation, and request fulfillment.

## 1. Project Modules

| Module | Description |
|---|---|
| Donor Management | Register, view, and maintain donor information. |
| Blood Donation & Inventory Management | Record donations, track available blood, and monitor expiry dates. |
| Recipient & Blood Request Management | Manage recipients, blood requests, allocation, and fulfillment. |
| Admin & Authentication Management | Manage authentication, permissions, users, and administrative operations. |

## 2. Key Features

### Donor Management
- Register and maintain donor records.
- Store personal and blood-group information.
- Maintain donor eligibility and donation history.

### Blood Donation & Inventory Management
- Record blood donations and screening information.
- Add eligible donations to blood inventory.
- Track blood groups, quantities, and expiry dates.
- Display available, non-expired blood inventory.
- Maintain consistency between donation and inventory records using database transactions.

### Recipient & Blood Request Management
- Register and maintain recipient records.
- Create and validate blood requests.
- Track request statuses, including Pending, Approved, Rejected, Allocated, and Fulfilled.
- Allocate compatible blood units to approved requests.
- Record blood issuance and update related statuses.

### Admin & Authentication Management
- User authentication and role-based access control.
- Protected administrative operations.
- User and permission management.
- Administrative monitoring and reporting.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Django |
| API Framework | Django REST Framework |
| Default Database | SQLite |
| Environment Configuration | python-dotenv |
| PostgreSQL Adapter | psycopg |
| Version Control | Git and GitHub |

**Note:** The current default database configuration uses SQLite. Although PostgreSQL support dependencies are included, PostgreSQL is not the active database configuration.

## 4. Project Structure

```text
Blood-Bank-Management-System/
│
├── accounts/                 # Authentication and permissions
├── donors/                   # Donor management
├── inventory/                # Donations and blood inventory
│   ├── templates/
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── blood_requests/            # Blood requests and allocation
│   ├── models.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── config/                    # Main Django configuration
│   ├── health.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 5. Installation and Setup

### Prerequisites

- Python installed.
- Git installed.
- A virtual environment.
- Internet connection for installing dependencies.

### Step 1: Clone the repository

```bash
git clone https://github.com/Deepthinreddy/Blood-Bank-Management-System.git
```

Navigate into the project:

```bash
cd Blood-Bank-Management-System
```

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4: Configure environment variables

The project uses `python-dotenv` to load environment variables from a local `.env` file.

The Django secret key can be configured using:

```env
DJANGO_SECRET_KEY=your-local-development-secret-key
```

Do not commit `.env` files or expose secret values in the repository.

### Step 5: Apply database migrations

```bash
python manage.py migrate
```

The default configuration uses SQLite, so a separate database server is not required for the default local setup.

### Step 6: Create an administrator account

```bash
python manage.py createsuperuser
```

Follow the prompts to create the administrator account.

### Step 7: Run the development server

```bash
python manage.py runserver
```

Open the application at:

http://127.0.0.1:8000/

## 6. Application Routes

| Route | Purpose |
|---|---|
| `/admin/` | Django administration |
| `/accounts/` | Authentication routes |
| `/api/` | Donor and blood-request API routes |
| `/donations/new/` | Record a blood donation |
| `/inventory/` | View available blood inventory |
| `/health/` | Application and database health check |

## 7. Running Tests

Run all project tests:

```bash
python manage.py test
```

Run tests for an individual application:

```bash
python manage.py test inventory
python manage.py test blood_requests
python manage.py test donors
python manage.py test accounts
```

Check the Django project configuration:

```bash
python manage.py check
```

## 8. Code Maintainability Guidelines

The project follows these practices to improve code readability and maintainability:

- Use meaningful variable, function, and class names.
- Follow consistent Python indentation and formatting.
- Use docstrings to explain modules, classes, and functions.
- Keep application responsibilities separated into Django apps.
- Validate user input through Django forms and serializers.
- Use database transactions for operations involving multiple related records.
- Write automated tests for important application functionality.
- Store sensitive configuration in environment variables.
- Avoid committing virtual environments, local databases, generated files, and secrets.

## 9. Security Considerations

The project incorporates security practices such as:

- Django authentication and password hashing.
- Role-Based Access Control (RBAC).
- Input validation and safe database operations.
- CSRF protection through Django middleware.
- Environment-based secret configuration.
- Health monitoring through the application health endpoint.

**Deployment warning:** The current settings are intended for local development. Before production deployment, configure a secure secret key, set `DEBUG=False`, configure `ALLOWED_HOSTS`, and use an appropriate production database and HTTPS.

## 10. Non-Functional Requirements

The system is designed to address the following non-functional requirements:

- **Performance:** Common dashboard and search operations should respond within 2 seconds for 90% of requests under the defined project test load.
- **Availability:** Target at least 99% system availability, excluding planned maintenance.
- **Security:** Protect user information and application operations.
- **Usability:** Provide responsive and understandable interfaces.
- **Data consistency:** Maintain consistent records and support transaction rollback during failures.
- **Maintainability:** Follow modular coding practices and maintain appropriate technical documentation.

## 11. Project Documentation

The following supporting documents are maintained as part of the project:

- Software Requirements Specification (SRS).
- Software Architecture and Design (SAD).
- UML diagrams.
- Requirements Traceability Matrix (RTM).
- Compact Test Plan.
- Test cases and acceptance tests.

## 12. Team Members and Responsibilities

| Team Member | SRN | Responsibility |
|---|---|---|
| C Rohit Reddy | PES2UG24CS125 | Admin & Authentication Management |
| Hansika R | PES2UG24CS178 | Blood Donation & Inventory Management |
| Gurudu Guru Preetam | PES2UG24CS174 | Recipient & Blood Request Management |
| Deepthi N Reddy | PES2UG24CS149 | Donor Management |

## 13. Project Status

Currently under development as part of a Software Engineering academic project.
