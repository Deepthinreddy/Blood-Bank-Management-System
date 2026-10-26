# Blood Bank Management System

A Software Engineering project for managing blood donors, blood donations, blood inventory, blood requests, recipients, and administrative operations.

The Blood Bank Management System (BBMS) is a web-based application designed to centralize blood-bank records and support day-to-day blood-bank workflows such as donor management, blood donation recording, inventory tracking, blood requests, allocation, and issue/fulfillment.

## Project Modules

- Donor Management
- Blood Donation & Inventory Management
- Recipient & Blood Request Management
- Admin & Authentication Management

## Key Features

### 1. Donor Management
- Register new donors with personal and blood-group information
- View and update donor details
- Maintain donor eligibility information
- Maintain donation history associated with each donor

### 2. Blood Donation & Inventory Management
- Record blood donations with donor, date, blood group, quantity/unit, and status
- Create or update blood inventory from valid donations
- View available blood units by blood group and status
- Search and filter blood inventory
- Track blood expiry dates
- Identify expired blood units and prevent them from being treated as available

### 3. Recipient & Blood Request Management
- Register recipients and maintain recipient records
- Create blood requests with blood group, quantity, priority, and required details
- Validate blood request information
- Track request status such as Pending, Approved, Rejected, Allocated, Fulfilled, and Cancelled
- Allocate compatible available blood units to approved requests
- Record blood issue/fulfillment and update related statuses

### 4. Admin & Authentication Management
- Secure user authentication
- Role-Based Access Control (RBAC)
- Protected administrative functions
- Manage user accounts and roles
- Generate basic reports for donations, inventory, requests, and issue/fulfillment
- Maintain audit information for significant administrative and operational actions

## Team Members & Responsibilities

| Team Member | SRN | Module / Responsibility |
|---|---|---|
| `C Rohit Reddy` | `PES2UG24CS125` | Donor Management |
| `Hansika R` | `PES2UG24CS178` | Blood Donation & Inventory Management |
| `Gurudu Guru Preetam` | `PES2UG24CS174` | Recipient & Blood Request Management |
| `Deepthi N Reddy` | `PES2UG24CS149` | Admin & Authentication Management |

Each team member is responsible for developing and maintaining their assigned module in a separate Git branch before integration into the main project.

## Technology Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python / Django
- Database: MySQL / PostgreSQL
- Version Control: Git & GitHub

## Security

The system follows security requirements including:

- HTTPS/TLS for protected communication
- Secure password hashing
- Role-Based Access Control (RBAC)
- Input validation and safe database operations
- Audit logging of significant administrative and operational actions

## Non-Functional Requirements

The system is designed with the following requirements:

- Common dashboard and search operations should respond within 2 seconds for 90% of requests under the defined project test load
- Target availability of at least 99% during planned operational periods
- Responsive and understandable interfaces on supported modern browsers
- Consistent and recoverable records during validation or transaction errors
- Modular and maintainable code structure

## Project Documentation

- Software Requirements Specification (SRS)
- UML Use-Case Diagrams
- Requirements Traceability Matrix (RTM)
- Test Cases and Acceptance Tests

## Project Status

🚧 Currently under development.
