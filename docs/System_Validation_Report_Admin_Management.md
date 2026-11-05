# Blood Bank Management System (BBMS) - Team 7
## Deliverable 2.b.ii: System Validation Report
### Feature: Admin Management (`accounts` module)

---

### Document Information
- **Course**: Software Engineering (UE24CS341A)
- **Project**: Blood Bank Management System (LifeLine)
- **Subsystem**: Admin Management & Security Core
- **Author / Module Lead**: C Rohit Reddy (PES2UG24CS125)
- **Reviewer / Coordinator**: Deepthi N Reddy (PES2UG24CS149)
- **Course Reviewer**: Pradeep Kumar Kenny
- **Validation Period**: 2nd November to 6th November 2026
- **Status**: **VERIFIED & ACCEPTED**

---

## 1. System Validation Overview

System Validation assesses whether the Admin Management subsystem satisfies all stakeholder requirements, functional specifications, and security policies outlined in the **BBMS Software Requirements Specification (SRS v1.0)**. 

Unlike unit tests that test functions in isolation, system validation evaluates end-to-end user workflows, permission boundary enforcement, session lifecycle behaviors, multi-module data aggregation, and tamper-resistant audit trails.

---

## 2. Requirements Compliance Matrix

| Requirement ID | Requirement Statement (Shall...) | Acceptance Criteria | Validation Method | Result | Compliance |
|---|---|---|---|---|---|
| **BBMS-F-030** | The system shall authenticate registered users using valid credentials. | Valid credentials establish authenticated session; invalid credentials rejected without information leakage. | End-to-end credential testing with valid admin, valid staff, invalid passwords, nonexistent accounts, and deactivated accounts. | Session established for valid logins; invalid logins safely rejected; `LOGIN` and `LOGOUT` audit events created. | **COMPLIANT** |
| **BBMS-F-031** | The system shall enforce role-based access to protected functions. | Unauthorized roles are strictly blocked from sensitive admin functions. | Attempted access by staff users and anonymous visitors to `/accounts/admin-dashboard/` and `/accounts/admin-reports/`. | HTTP 403 Forbidden returned for staff; HTTP 302 redirect to login with `?next=` for anonymous visitors. | **COMPLIANT** |
| **BBMS-F-032** | The system shall prevent expired or invalid sessions from accessing protected resources. | Sessions inactive for >30 minutes or terminated upon browser closure are invalidated. | Inactivity middleware testing with timestamps simulated beyond 1800s threshold; settings verification (`SESSION_COOKIE_AGE=1800`). | Inactive session automatically terminated, user redirected to login, session token purged. | **COMPLIANT** |
| **BBMS-F-033** | The system shall provide an admin interface accessible only to authorized administrators. | Dedicated administrative interface is blocked to non-administrators. | View-level and template-level RBAC evaluation on `/accounts/admin-dashboard/`. | Admin dashboard rendered only when user has `role='ADMIN'`. | **COMPLIANT** |
| **BBMS-F-034** | The system shall allow authorized administrators to manage user accounts and roles. | User/role changes take effect correctly in persistent database. | User creation, role update (`STAFF` to `ADMIN`), and deactivation (`is_active=False`) tested through model and admin configuration. | User modifications persist immediately; disabled accounts locked out from authentication. | **COMPLIANT** |
| **BBMS-F-035** | The system shall provide basic reports for donations, inventory, requests, and issue/fulfillment. | Report values match stored records across all connected modules. | Multi-module seeded data query execution on `/accounts/admin-reports/` integrating `Donor`, `BloodInventory`, and `BloodRequest`. | Aggregate counts for donors by group, inventory units by group and status, and requests by status match 100%. | **COMPLIANT** |
| **BBMS-F-036** | The system shall record significant administrative actions for audit purposes. | Representative actions appear in audit log with user identity, action, and timestamp. | Verification of `AuditRecord` creation during authentication, user modifications, and custom admin actions via `record_audit()`. | Records contain actor, action, timestamp, IP address, and details in chronological descending order. | **COMPLIANT** |
| **BBMS-SR-002** | The system shall store user credentials using strong one-way cryptographic hashing. | Plaintext passwords never stored in database or logs. | Inspection of stored `password` field in `User` model; validation against PBKDF2/SHA256 standard. | Password strings hashed with `pbkdf2_sha256$`; `check_password` validates raw input. | **COMPLIANT** |
| **BBMS-SR-003** | The system shall verify server-side authorization on all protected administrative endpoints. | Client-side bypass or URL tampering rejected by server. | Direct HTTP GET/POST invocation of administrative views using unprivileged session cookies. | Server intercepts request at decorator/middleware level and returns HTTP 403 Forbidden. | **COMPLIANT** |
| **BBMS-SR-005** | The system shall maintain an operational audit trail with user identity and timestamp. | Significant operational actions are traceable to authenticated actors. | Verification of `AuditRecordAdmin` model admin interface and database records. | Immutable audit records capture user, IP address, timestamp, and details with readonly protection. | **COMPLIANT** |

---

## 3. End-to-End Workflow Validation Scenarios

### Workflow 1: User Authentication & Session Security Lifecycle
- **Scenario**: An administrator logs into the system, performs administrative tasks, remains idle for 31 minutes, attempts a new request, and is required to re-authenticate.
- **Validation Outcome**:
  1. POST `/accounts/login/` with valid credentials authenticates successfully and sets session cookie.
  2. Middleware records `last_activity` timestamp.
  3. When request occurs after 1801 seconds of inactivity, `SessionInactivityMiddleware` intercepts the request, flushes the session, and redirects to `/accounts/login/`.
  4. Calling `/accounts/logout/` invalidates the session immediately and records `AuditRecord(action='LOGOUT')`.
- **Verdict**: **VERIFIED**

### Workflow 2: Role-Based Access Control & Privilege Boundary
- **Scenario**: A user with the `STAFF` role attempts to access `/accounts/admin-dashboard/` and `/accounts/admin-reports/`.
- **Validation Outcome**:
  1. Unauthenticated users are redirected to `/accounts/login/?next=...`.
  2. Authenticated `STAFF` users receive an explicit HTTP 403 Forbidden response.
  3. Authenticated `ADMIN` users receive HTTP 200 OK with full administrative controls and audit logs.
- **Verdict**: **VERIFIED**

### Workflow 3: Cross-Module System Reports Validation
- **Scenario**: Administrator navigates to `/accounts/admin-reports/` to inspect cross-subsystem metrics across donor registrations, blood stock inventory, and blood requests.
- **Validation Outcome**:
  1. Donors categorized by blood groups (e.g. A+, B+, AB+, O-) displayed with precise counts.
  2. Blood inventory stock summarized into total units, available units, expired units, and breakdowns by blood group.
  3. Blood requests summarized by operational status (`PENDING`, `APPROVED`, `FULFILLED`, `REJECTED`).
  4. Empty states display helpful fallback messages when no records exist.
- **Verdict**: **VERIFIED**

### Workflow 4: Administrative User Management
- **Scenario**: System administrator creates accounts, modifies user privileges, and deactivates compromised or retired staff accounts.
- **Validation Outcome**:
  1. New accounts created with assigned roles (`ADMIN` or `STAFF`).
  2. Role modifications (promoting staff to admin) take effect immediately on session permissions.
  3. Deactivated accounts (`is_active=False`) are blocked from authentication on subsequent login attempts.
- **Verdict**: **VERIFIED**

### Workflow 5: Audit Trail & Security Traceability
- **Scenario**: Critical administrative and authentication events are logged for security compliance.
- **Validation Outcome**:
  1. Login and logout automatically generate audit records with client IP address (supporting proxy forwarded IPs).
  2. Administrative actions recorded via `record_audit` helper function.
  3. Audit records in database and admin interface are chronologically ordered by `-timestamp, -id`.
  4. Audit logs are readonly in Django admin to prevent administrative tampering.
- **Verdict**: **VERIFIED**

---

## 4. Acceptance Criteria & Final Sign-Off

| Acceptance Check | Target Specification | Actual Measured Result | Result |
|---|---|---|---|
| **Authentication Pass Rate** | 100% on valid; 0% on invalid | 100% valid pass; 0% invalid pass | **PASS** |
| **RBAC Enforcement** | 100% non-admin access blocked | 100% blocked with HTTP 403 | **PASS** |
| **Session Inactivity Timeout** | 1800 seconds (30 minutes) | Exactly 1800s enforced | **PASS** |
| **Report Data Accuracy** | 100% match with DB counts | 100% match with DB counts | **PASS** |
| **Audit Log Completeness** | Captures User, Action, Time, IP | All 4 attributes captured | **PASS** |
| **Password Hashing** | Cryptographic one-way hash | PBKDF2/SHA256 verified | **PASS** |

### Formal Recommendation
The **Admin Management** subsystem has completed all testing according to the Test Plan, satisfies all mapped SRS requirements, and is **APPROVED** for Sprint-3 milestone release and final project integration.
