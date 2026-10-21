# FSUUCLINIC

## Project Title
FSUUCLINIC Clinic Appointment and Management System

## Abstract
FSUUCLINIC is a Django-based web application designed to streamline clinic operations for administrators, staff, and patients. The system centralizes appointment scheduling, patient records, doctor management, inventory control, and internal messaging into a single platform. Patients can browse available doctors, view schedules, book appointments, update their profiles, and track upcoming or archived visits. Administrators and staff can manage physicians, maintain working schedules, update appointment statuses, record medical summaries, and monitor medical supplies and medications used during consultations. The project combines a role-based access model, secure authentication, validated forms, and a responsive dashboard interface built using Django, Bootstrap, and custom templates. The result is a practical healthcare management system that improves appointment efficiency, visibility into clinic workflow, and the organization of patient and operational data.

Keywords: clinic management, appointment booking, Django, healthcare, inventory tracking

## 1. Introduction

### 1.1 Background of the Study
Healthcare facilities often rely on fragmented tools and manual coordination when managing appointments, doctor availability, patient information, and stock inventory. This creates delays, inconsistent updates, and communication problems between medical staff and patients. FSUUCLINIC was developed to address these issues by providing a centralized web platform for a clinic environment. The system supports the day-to-day operations of a small to medium medical clinic by making appointment scheduling, patient communication, and staff administration easier to manage.

### 1.2 Statement of the Problem
The clinic workflow faces several recurring problems:

1. Appointments are difficult to arrange efficiently without a shared schedule system.
2. Staff members need a centralized method to manage doctor profiles and availability.
3. Patient data and appointment records are not always organized in one place.
4. Inventory of medical supplies and medications is manually tracked, leading to errors.
5. Communication between patients and clinic staff is inconsistent and can be delayed.

### 1.3 Objectives of the Study
General objective:

To develop a clinic management system that improves scheduling, patient interaction, and operational visibility for healthcare staff and patients.

Specific objectives:

- Create a role-based web application with patient, staff, and admin access.
- Allow patients to view doctor availability and book appointments online.
- Provide staff/admin users with tools to manage doctors, schedules, blocked slots, and appointment statuses.
- Enable inventory tracking for medications and clinic supplies.
- Support internal messaging for appointment updates and patient communication.
- Ensure the system follows a secure and maintainable Django architecture.

### 1.4 Scope and Limitations
Scope:

- Doctor profile management
- Appointment booking and rescheduling
- Appointment status updates and archival
- Patient profile and dashboard views
- Staff/admin dashboard analytics and inventory management
- Messaging system for appointment-related updates

Limitations:

- This is a web-based system only; no mobile application is included.
- The application is designed for a single clinic workflow and does not include multi-branch support.
- Payment processing and third-party medical integrations are not implemented in this release.
- Real-time notifications are limited to the built-in messaging and dashboard workflow.

### 1.5 Significance of the Study
This system benefits patients by simplifying appointment booking and access to relevant information. It helps clinic staff reduce scheduling issues, improve documentation, and keep stock control organized. It also supports administrators by offering a single system for managing doctors, schedules, inventory, and operational reports. Future developers can reuse the structure for expanding the clinic into more advanced modules such as electronic medical records, billing, and analytics.

## 2. System Overview

### 2.1 System Description
FSUUCLINIC is a role-based clinic management platform built with Django. Users log in to the system based on their role, then access features relevant to their responsibilities. Patients can browse doctors, choose appointment dates and time slots, and manage their personal profile. Staff and administrators can maintain clinics records and manage daily operations from dashboards tailored for their roles.

### 2.2 Users and Roles

| User Role | Description | Main Capabilities |
|---|---|---|
| Admin | Manages the clinic system overall | Manage doctors, schedules, blocked slots, appointment records, inventory, and staff access |
| Staff | Handles clinic operations support | View dashboard, update appointments, manage daily schedules, and process queued visits |
| Patient | Books and tracks clinic visits | Search doctors, book appointments, update profile, view appointments, and receive updates |

### 2.3 Features and Modules

| Module / Feature | Description | User Role(s) |
|---|---|---|
| User Authentication | Login, registration, logout, session-based access | Admin, Staff, Patient |
| Doctor Management | Add, update, archive, and restore doctor profiles | Admin, Staff |
| Schedule Management | Set weekly schedules and blocked time slots | Admin, Staff |
| Appointment Booking | Browse doctors, pick available slots, and schedule visits | Patient |
| Appointment Tracking | Confirm, check-in, complete, cancel, archive, and reschedule appointments | Admin, Staff, Patient |
| Inventory Management | Add, restock, remove, and monitor medical stock | Admin, Staff |
| Messaging | Send and view internal communication and status updates | Admin, Staff, Patient |
| Profile Management | View and edit patient and admin profile information | Admin, Staff, Patient |

### 2.4 Technology Stack

| Layer | Technology / Tool | Version | Purpose |
|---|---|---|---|
| Frontend | HTML, CSS, Bootstrap, Django templates | Bootstrap version not pinned | User interface and responsive dashboards |
| Backend | Python, Django | Django 6.1.1; Python version not pinned | Application logic, routing, authentication, and models |
| Database | SQLite; PostgreSQL supported through `DATABASE_URL` | SQLite version bundled with Python; PostgreSQL version depends on deployment | Persistent system data storage |
| Forms | Django Forms, Crispy Forms, Crispy Bootstrap 5 | django-crispy-forms 2.4; crispy-bootstrap5 2025.6 | Input validation and form styling |
| Static / Media Files | WhiteNoise, Pillow | WhiteNoise 6.9.0; Pillow 11.3.0 | Static-file serving and uploaded profile/doctor photos |
| External APIs / Services | None currently integrated | N/A | The application uses Django’s built-in authentication and database integration |
| Tools | Git, GitHub, VS Code, Django admin | Versions not pinned | Source control, development, and administrative management |
| Hosting / Deployment | Local Django development server; Render-ready database configuration | Deployment platform/version not specified | Local development and configuration for deployment using environment variables |

## 3. System Architecture and Integration

### 3.1 System Architecture Diagram
The system follows a typical Django Model-View-Template (MVT) architecture:

- Client browser sends HTTP requests to Django URLs
- Views process requests and apply role-based authorization
- Models define the database schema for users, doctors, appointments, and inventory
- Templates render dashboards and forms
- SQLite/PostgreSQL stores persistent clinic data
- Media files store uploaded patient and doctor photos

### 3.2 Integration Approach
The project is organized into separate Django apps to keep responsibilities focused and maintainable:

- `accounts` handles authentication, user profiles, and messaging
- `admin_dashboard` manages doctor records, schedules, appointments, and inventory
- `patient_dashboard` manages patient booking and dashboard features
- `clinicappoint` contains core project settings and routing

These modules integrate through shared models and commonly used user roles, enabling a single data model across the clinic workflow.

### 3.3 External APIs and Services Used
The current implementation is primarily self-contained and built around Django’s built-in services. The application uses:

- Django authentication system
- Django admin panel for administrative management
- Static/media file handling for uploaded photos
- Database URL configuration for environment-based database switching

### 3.4 Data Flow
A typical patient journey is as follows:

1. Patient logs in or registers an account.
2. Patient searches for a doctor and selects an available date.
3. A slot is validated against schedules, blocked times, and existing bookings.
4. The appointment is saved to the database with a pending or confirmed status.
5. Staff or admin reviews and updates the appointment status.
6. Messages and summaries are recorded for follow-up communication.
7. Inventory usage is updated when a consultation is completed.

## 4. Database Design

### 4.1 Entity Relationship Diagram (ERD)
Core entities include:

- `User` — stores login credentials, role, profile details, and health data
- `Doctor` — stores doctor profile, specialty, schedule, and archive metadata
- `DoctorSchedule` — stores working hours per doctor and weekday
- `BlockedSlot` — stores unavailable time blocks for a doctor
- `Appointment` — links patients and doctors to scheduled visits and statuses
- `InventoryItem` — tracks materials and supplies and current stock quantity
- `Message` — stores appointment-related communication between users

The relationships reflect a standard clinic model where one patient may have many appointments, one doctor may have many schedules and appointments, and each appointment may be associated with multiple messages.

### 4.2 Data Dictionary

| Table / Entity | Key Fields | Description |
|---|---|---|
| `User` | `username`, `role`, `email`, `phone`, `address`, `photo` | Stores system users and patient profile information |
| `Doctor` | `name`, `specialty`, `bio`, `sex`, `photo`, `is_archived` | Describes each physician within the clinic |
| `DoctorSchedule` | `doctor`, `day_of_week`, `start_time`, `end_time` | Defines weekly availability windows |
| `BlockedSlot` | `doctor`, `date`, `start_time`, `end_time`, `reason` | Prevents scheduling during unavailable periods |
| `Appointment` | `patient`, `doctor`, `date`, `time`, `status`, `notes` | Tracks patient visits and consultation data |
| `InventoryItem` | `name`, `category`, `quantity`, `unit_price` | Maintains stock and medication records |
| `Message` | `sender`, `recipient`, `subject`, `body`, `appointment` | Stores clinic communication entries |

## 5. API Documentation

### 5.1 Base URL and Conventions
The project uses Django URL routing rather than a separate REST API layer. URL endpoints are organized by application in the following pattern:

- `/` and `/home/` for landing and home pages
- `/register/`, `/login/`, `/logout/` for authentication
- `/messages/` for communication features
- `/dashboard/` for patient-specific functionality
- `/admin-dashboard/` for admin/staff management
- `/inventory/` for inventory operations
- `/admin/` for Django administration access

### 5.2 Endpoint Summary

| Endpoint | Purpose |
|---|---|
| `/` | Landing page |
| `/register/` | Patient registration |
| `/login/` | User login |
| `/logout/` | User logout |
| `/dashboard/` | Patient dashboard |
| `/dashboard/appointments/` | Display patient appointments |
| `/dashboard/appointments/book/` | Book appointment |
| `/admin-dashboard/` | Admin dashboard |
| `/admin-dashboard/doctor/new/` | Create doctor record |
| `/admin-dashboard/appointment/<pk>/status/` | Update appointment status |
| `/inventory/` | View and manage inventory |
| `/messages/` | View and send messages |

### 5.3 Endpoint Details
Each route is mapped to a Django view that performs validation, database updates, redirects, and template rendering. For example:

- `book_appointment` validates the selected doctor and date,
- `appointment_status_update` updates patient statuses and stock quantities when a visit is completed,
- `doctor_form_view` saves doctor registration and archive actions,
- `delete_or_unsend_message` handles message deletion and unsend states.

## 6. Security Measures
The application applies several security practices:

- Django authentication and session management
- Role-based access control using custom decorators
- CSRF protection on form submissions
- Form validation for user input and stock updates
- Password validation using Django’s built-in validators
- Access restrictions to admin and staff-only operations
- Media and static file configuration through project settings

## 7. User Interface and User Manual

### 7.1 Login Page
The login interface allows registered users to sign in with their username and password. The page is integrated with the main landing page and supports navigation to registration.

### 7.2 Patient Dashboard
The patient dashboard shows:

- Available doctors and specialist categories
- Upcoming appointments
- Booking interface and available time slots
- Profile summary and patient health fields
- Appointment archive and active visit tracking

### 7.3 Admin Dashboard
The admin dashboard provides:

- Doctor management forms
- Appointment filters and status updates
- Weekly schedules and blocked slot configuration
- Inventory summary and restock tools
- Clinic communication overview

## 8. Testing

### 8.1 Testing Approach
Testing for this project is primarily centered on functional validation of critical flows, including user registration, appointment booking, admin management, and inventory updates. Django forms and model validations were used to reduce input errors and testable invalid states.

### 8.2 Test Cases and Results
Representative test scenarios include:

- Registration of a new patient account
- Login as patient, staff, and admin roles
- Booking appointment with valid and invalid doctor slots
- Updating appointment status to completed
- Removing or restocking an inventory item
- Archiving and restoring a doctor profile
- Sending and deleting messages between users

### 8.3 Known Issues and Fixes
The system currently focuses on practical clinic workflow support. Known constraints include the absence of advanced multi-role permissions beyond the current app-level role checks and the limited scope of external API integrations. These can be extended in future releases with additional modules and service integrations.

## 9. Deployment and Installation Guide

### 9.1 System Requirements
- Python 3.10+
- Django 6.1.1
- Virtual environment support
- SQLite for local development or PostgreSQL-ready configuration for deployment

### 9.2 Installation Steps
1. Clone the repository.
2. Open a terminal and create a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply database migrations:

```bash
python manage.py migrate
```

5. Create a superuser:

```bash
python manage.py createsuperuser
```

6. Run the development server:

```bash
python manage.py runserver
```

7. Access the app in the browser using the local address generated by Django.

### 9.3 Source Code Repository
The project source code is located in the current repository folder and can be managed through Git and GitHub.

## 10. Team Roles and Contributions
This project is organized to reflect cooperative software development, with responsibilities divided according to the project workflow:

- System design and database planning
- Frontend layout and dashboard views
- Backend logic and route handling
- Role-based authentication and access control
- Appointment and schedule management
- Inventory and communication features
- Quality testing and deployment support

## 11. Conclusion and Recommendations

### 11.1 Conclusion
FSUUCLINIC successfully demonstrates a practical clinic management system built on Django. It combines role-based access, appointment scheduling, profile management, messaging, and inventory tracking in one platform. The implementation reflects a realistic healthcare workflow and provides a strong foundation for future expansion.

### 11.2 Recommendations
Future improvements could include:

- Appointment payment integration
- Electronic medical record (EMR) modules
- Automated WhatsApp or SMS notifications
- Data analytics dashboard for clinic performance
- Multi-clinic or branch-level operations support

## References
- Django Documentation. https://docs.djangoproject.com/
- Bootstrap Documentation. https://getbootstrap.com/docs/
- Python Software Foundation. https://www.python.org/
- W3Schools and MDN Web Docs for frontend and web standards

## Appendices
Appendix material may include screenshots of the login page, patient dashboard, admin dashboard, and appointment booking flow. These visual records support the user experience walkthrough and software demonstration.

---

Prepared for SIA 2 – Systems Integration and Architecture 2.
