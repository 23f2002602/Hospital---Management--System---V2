Hospital Management System V2A comprehensive, full-stack web application designed to streamline hospital operations. This system facilitates interaction between Administrators, Doctors, and Patients, managing everything from user authentication and appointment booking to medical records and analytical reporting.🚀 Features🏥 GeneralRole-Based Access Control (RBAC): Distinct dashboards and permissions for Admins, Doctors, and Patients.Secure Authentication: JWT-based login and registration system.PWA Support: Installable as a Progressive Web App.Responsive Design: Built with Bootstrap 5 for mobile and desktop compatibility.👤 Patient ModuleDoctor Search: Advanced search by name, specialization, or department.Appointment Management: Book, reschedule, and cancel appointments efficiently.Medical History: View past diagnoses, prescriptions, and doctor notes.Profile Management: Update personal details and contact information.👨‍⚕️ Doctor ModuleDashboard: Real-time view of upcoming schedules and daily statistics.Schedule Management: Define weekly availability and specific date overrides.Patient Treatment: Record diagnoses, prescriptions, and private notes for appointments.Data Export: Export appointment history to CSV.🛠 Admin ModuleUser Management: Create and manage Doctors and Departments.System Oversight: View all patients and system-wide activities.Reporting: Generate and download monthly analytical reports (PDF/CSV) regarding appointments and diagnoses.🛠️ Tech StackBackendLanguage: Python 3Framework: FlaskDatabase: SQLite (SQLAlchemy ORM)Async Tasks: Celery with Redis (for emails and reports)Caching: Redis (Flask-Caching)Authentication: Flask-JWT-ExtendedFrontendFramework: Vue.js 3 (Composition API)Build Tool: ViteRouting: Vue RouterHTTP Client: AxiosUI Library: Bootstrap 5Charting: Chart.js⚙️ PrerequisitesBefore you begin, ensure you have the following installed:Python 3.8+Node.js 16+ & npmRedis Server (Running on default port 6379)wkhtmltopdf (Required for generating PDF reports)📥 Installation & Setup1. Clone the RepositoryBashgit clone <repository-url>
cd hospital-management-system-v2
2. Backend SetupNavigate to the backend directory and set up the Python environment.Bashcd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
Database Seeding:Populate the database with initial data (Admin, Doctors, Departments, Patients).Bash# Must be run from the backend directory with venv activated
python seed/seed_admin.py
python seed/seed_doctors.py
python seed/seed_patients.py
3. Frontend SetupNavigate to the frontend directory and install node modules.Bashcd ../frontend
npm install
🚀 Running the ApplicationYou need to run three separate processes (terminals) for the full system to work.Terminal 1: Redis & Celery WorkerEnsure your Redis server is running. Then, start the Celery worker for background tasks (emails, exports).Bashcd backend
# Make sure venv is activated
celery -A worker.celery worker --loglevel=info
(Optional) To enable scheduled tasks like daily reminders, run the Celery Beat scheduler in another terminal:Bashcelery -A worker.celery beat --loglevel=info
Terminal 2: Flask API ServerStart the backend API.Bashcd backend
# Make sure venv is activated
python app.py
The API will run at http://127.0.0.1:5000Terminal 3: Vue FrontendStart the frontend development server.Bashcd frontend
npm run dev
The frontend will typically run at http://localhost:5173🧪 Default CredentialsAfter running the seeding scripts, you can use the following credentials to log in:RoleEmailPasswordAdminadmin@hms.comadmin123Doctormeredith@example.compassword123Patientjohn@example.compassword123📂 Project Structure.
├── backend/
│   ├── app.py              # Application factory and entry point
│   ├── celery_app.py       # Celery configuration
│   ├── config.py           # App configuration (DB, Redis, Mail)
│   ├── database.py         # DB instance
│   ├── models.py           # SQLAlchemy Database Models
│   ├── tasks.py            # Celery tasks (Email, CSV/PDF generation)
│   ├── routes/             # API Route Blueprints
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   └── reports.py
│   └── seed/               # Data seeding scripts
│
└── frontend/
    ├── src/
    │   ├── api/            # Axios setup
    │   ├── components/     # Reusable Vue components & Dashboards
    │   ├── pages/          # Main Views (Login, Home, Profile)
    │   ├── router/         # Vue Router configuration
    │   └── styles.css      # Global styles and theming
    ├── public/             # Static assets (manifest, icons)
    └── vite.config.js      # Vite configuration
