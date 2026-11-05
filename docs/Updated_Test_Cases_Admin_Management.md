# Blood Bank Management System (BBMS) - Team 7
## Mini-Project Deliverables Part-3: Updated Test Cases Document
### Subsystem / Module: Admin Management (`accounts`)

---

### Document Information
- **Course**: Software Engineering (UE24CS341A)
- **Project**: Blood Bank Management System (LifeLine)
- **Team**: Team 7, Section C
- **Module Focus**: Admin Management, Authentication, Session Management, Reports, and Audit Trail
- **Primary Owner**: C Rohit Reddy (PES2UG24CS125)
- **Cross Tester**: Deepthi N Reddy (PES2UG24CS149)
- **Sprint**: Sprint 3 (2nd Nov – 6th Nov 2026)
- **Date**: 5th November 2026
- **Status**: Updated & Approved (All Test Cases Verified and Passing)

---

## 1. Context and Test Case Evolution Across Sprints

During Sprints 1, 2, and 3, the Admin Management module expanded from baseline authentication setup to a full-featured role-based administrative core:
1. **Sprint 1 Changes**: Custom `User` model inheriting from `AbstractUser` with role differentiation (`ADMIN`, `STAFF`); Django Admin integration via `CustomUserAdmin` with role-aware fieldsets and filters.
2. **Sprint 2 Changes**: Introduction of the `AuditRecord` model, signal handlers (`record_login`, `record_logout`) for tracking events with client IP addresses, session timeout enforcement middleware (`SessionInactivityMiddleware` with 30-minute inactivity limit and browser closure expiration), permission decorators (`admin_required`, `operational_staff_required`), initial Admin Dashboard, and donor summary reports.
3. **Sprint 3 (Spill-over & Enhancements)**: Multi-module system reporting (`admin_reports`) integrating inventory stock by blood group and status (`BloodInventory`) and blood requests by status (`BloodRequest`); unified audit logging utility (`record_audit`); strict RBAC verification across staff, admin, and unauthenticated endpoints.

The initial test cases from the Compact Test Plan (`TC-AUTH-01` to `TC-AUTH-03`, `TC-ADMIN-01` to `TC-ADMIN-03`, and `TC-SEC-02` to `TC-SEC-05`) have been refined, updated, and broken down into rigorous, executable unit and integration test specifications below.

---

## 2. Updated Test Cases Specification Table

| Test Case ID | SRS Req ID | Feature / Component | Test Scenario & Objective | Pre-conditions | Test Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|---|---|
| **TC-AUTH-01.1** | BBMS-F-030 | Admin Authentication | Verify valid administrator credentials authenticate and establish session | Active Admin user exists (`role='ADMIN'`) | 1. POST valid credentials to `/accounts/login/`<br>2. Check response status and session<br>3. Inspect audit trail | User session created (`_auth_user_id` set), HTTP 302 redirect to `/`, `AuditRecord` created with action `LOGIN` | Session established, redirected to `/`, login audit logged | **PASS** |
| **TC-AUTH-01.2** | BBMS-F-030 | Staff Authentication | Verify valid staff credentials authenticate and establish session | Active Staff user exists (`role='STAFF'`) | 1. POST valid credentials to `/accounts/login/`<br>2. Verify redirect and session | User authenticated, redirected to `/`, session active | Authenticated successfully and redirected | **PASS** |
| **TC-AUTH-01.3** | BBMS-F-030 | Authentication Validation | Reject login attempt with incorrect password | Existing user record | 1. POST invalid password to `/accounts/login/`<br>2. Check session and response | Login denied (HTTP 200 re-render with error), no session established, no successful audit log | Access denied, error rendered, session empty | **PASS** |
| **TC-AUTH-01.4** | BBMS-F-030 | Authentication Validation | Reject login attempt with non-existent username | No user with username `ghost_user` | 1. POST non-existent credentials to `/accounts/login/` | Request rejected safely without database error or account enumeration leakage | Rejected with invalid credentials prompt | **PASS** |
| **TC-AUTH-01.5** | BBMS-F-030 | Account State Check | Reject login attempt for deactivated user account | User exists with `is_active=False` | 1. POST credentials of inactive user to `/accounts/login/` | Inactive account denied authentication, no session created | Login denied, account remains locked out | **PASS** |
| **TC-AUTH-01.6** | BBMS-F-030 | Session Termination | Verify user logout terminates session and records audit event | Authenticated admin user | 1. POST to `/accounts/logout/`<br>2. Verify session key removal<br>3. Inspect audit records | Session invalidated (`_auth_user_id` removed), redirected to `/accounts/login/`, `AuditRecord` logged with `LOGOUT` | Session cleared, redirected to login, audit logged | **PASS** |
| **TC-AUTH-02.1** | BBMS-F-031, BBMS-F-033 | RBAC - Admin Dashboard | Allow authorized administrator to view Admin Dashboard | Authenticated user with `role='ADMIN'` | 1. GET `/accounts/admin-dashboard/` | HTTP 200 OK, admin controls, account statistics, and audit activity rendered | HTTP 200 OK, full dashboard accessible | **PASS** |
| **TC-AUTH-02.2** | BBMS-F-031, BBMS-F-033 | RBAC - Admin Dashboard | Deny non-admin staff access to Admin Dashboard | Authenticated user with `role='STAFF'` | 1. GET `/accounts/admin-dashboard/` | HTTP 403 Forbidden raised via `admin_required` decorator | HTTP 403 Forbidden returned | **PASS** |
| **TC-AUTH-02.3** | BBMS-F-031, BBMS-F-033 | RBAC - Anonymous Access | Redirect unauthenticated requests to login page | Unauthenticated user | 1. GET `/accounts/admin-dashboard/` | HTTP 302 Redirect to `/accounts/login/?next=/accounts/admin-dashboard/` | Redirected to login with next parameter | **PASS** |
| **TC-AUTH-02.4** | BBMS-F-031, BBMS-F-035 | RBAC - Admin Reports | Allow authorized administrator to access System Reports | Authenticated user with `role='ADMIN'` | 1. GET `/accounts/admin-reports/` | HTTP 200 OK, system reports rendered | HTTP 200 OK, reports page accessible | **PASS** |
| **TC-AUTH-02.5** | BBMS-F-031, BBMS-F-035 | RBAC - Admin Reports | Deny non-admin staff access to System Reports | Authenticated user with `role='STAFF'` | 1. GET `/accounts/admin-reports/` | HTTP 403 Forbidden raised | HTTP 403 Forbidden returned | **PASS** |
| **TC-AUTH-02.6** | BBMS-F-031 | RBAC Helpers | Verify `is_bbms_admin` classification helper | Users with various roles and statuses | 1. Evaluate `is_bbms_admin()` on admin, staff, and inactive users | Returns `True` only for active, authenticated `ADMIN` role | Correct boolean flags returned | **PASS** |
| **TC-AUTH-02.7** | BBMS-F-031 | RBAC Helpers | Verify `is_operational_staff` classification helper | Admin, staff, superuser, inactive users | 1. Evaluate `is_operational_staff()` on all user variants | Returns `True` for staff, admin, and superuser; `False` for inactive | Correct permissions granted | **PASS** |
| **TC-AUTH-02.8** | BBMS-F-031 | Decorator Boundary | Verify `operational_staff_required` enforces access restrictions | Users with authorized and unauthorized roles | 1. Invoke decorated endpoint with staff user<br>2. Invoke with guest user | Staff permitted (HTTP 200); unauthorized raises `PermissionDenied` | Decorator enforces permission boundary | **PASS** |
| **TC-AUTH-03.1** | BBMS-F-032 | Session Inactivity | Terminate session when inactivity exceeds 1800 seconds (30 mins) | Authenticated session with `last_activity` > 1800s ago | 1. Set `last_activity = now - 1801`<br>2. Make request to protected view | User logged out, redirected to `/accounts/login/`, session token invalidated | Session terminated, redirected to login | **PASS** |
| **TC-AUTH-03.2** | BBMS-F-032 | Session Renewal | Retain session and update timestamp when activity is within 1800s | Authenticated session with `last_activity` < 1800s ago | 1. Set `last_activity = now - 100`<br>2. Make request to protected view | Request succeeds (HTTP 200), `last_activity` refreshed to current timestamp | Request allowed, session renewed | **PASS** |
| **TC-AUTH-03.3** | BBMS-F-032 | Middleware Safety | Verify middleware handles anonymous requests without error | Anonymous client | 1. Send request without session | Request passes through to next handler cleanly without exceptions | Handled cleanly, HTTP 200 returned | **PASS** |
| **TC-AUTH-03.4** | BBMS-F-032 | Session Configuration | Verify Django session security settings | Application configuration | 1. Inspect `SESSION_COOKIE_AGE`<br>2. Inspect `SESSION_EXPIRE_AT_BROWSER_CLOSE`<br>3. Inspect `SESSION_SAVE_EVERY_REQUEST` | Age = 1800s (30m), Expire on close = `True`, Save every request = `True` | Settings conform exactly to specification | **PASS** |
| **TC-ADMIN-01.1** | BBMS-F-034 | User Administration | Verify creation of user accounts with designated roles | Database available | 1. Create user with `role='ADMIN'`<br>2. Create user with `role='STAFF'`<br>3. Check `__str__` | Roles stored accurately; `str()` returns username | Accounts created with correct roles | **PASS** |
| **TC-ADMIN-01.2** | BBMS-F-034 | Role Modification | Modify user role from `STAFF` to `ADMIN` | Existing staff user | 1. Update `user.role = 'ADMIN'`<br>2. Save and query database | User role updated to `ADMIN` persistently in DB | Role change persisted correctly | **PASS** |
| **TC-ADMIN-01.3** | BBMS-F-034 | User Deactivation | Deactivate user account via `is_active` flag | Existing active user | 1. Set `user.is_active = False`<br>2. Save and query database | Account marked inactive; subsequent auth checks fail | Account disabled successfully | **PASS** |
| **TC-ADMIN-01.4** | BBMS-F-034 | Admin Model Config | Validate `CustomUserAdmin` registration and fieldsets | Django admin site | 1. Inspect `CustomUserAdmin.list_display`<br>2. Inspect `list_filter`<br>3. Inspect `fieldsets` and `add_fieldsets` | `role` included in `list_display`, `list_filter`, and fieldsets | Role fields exposed for admin management | **PASS** |
| **TC-ADMIN-02.1** | BBMS-F-035 | System Reports | Verify system reports render gracefully with empty tables | Clean database with zero records | 1. Admin navigates to `/accounts/admin-reports/`<br>2. Check context and HTML | All counts equal 0; friendly empty state messages displayed | Counts equal 0; empty state rendered | **PASS** |
| **TC-ADMIN-02.2** | BBMS-F-035 | System Reports | Verify multi-module data aggregation from seeded records | Database seeded with donors, donations, inventory units, and blood requests | 1. Seed 2 donors (A+, O+)<br>2. Seed 3 inventory items (2 Available, 1 Expired)<br>3. Seed 2 blood requests (Pending, Approved)<br>4. GET `/accounts/admin-reports/` | Context contains exact counts: donors=2, inventory=3, available=2, expired=1, requests=2; HTML renders badges and stat cards | All counts and aggregations match source data | **PASS** |
| **TC-ADMIN-03.1** | BBMS-F-036, BBMS-SR-005 | Audit Logging | Verify `record_audit` helper creates structured audit records | Authenticated user | 1. Call `record_audit(user, action, details, ip_address)`<br>2. Query `AuditRecord` | Record created with user, action name, details, IP address, and auto timestamp | Audit record created and verifiable | **PASS** |
| **TC-ADMIN-03.2** | BBMS-F-036, BBMS-SR-005 | Client IP Extraction | Verify `get_client_ip` extracts IP from forwarded proxy header and remote addr | Mock requests | 1. Request with `HTTP_X_FORWARDED_FOR`<br>2. Request with `REMOTE_ADDR`<br>3. None request | Returns primary client IP; fallback to remote address; None for empty request | IP extracted accurately in all scenarios | **PASS** |
| **TC-ADMIN-03.3** | BBMS-F-036, BBMS-SR-005 | Audit Trail Display | Verify `AuditRecord` chronological ordering and admin registration | Multiple audit records created | 1. Check QuerySet ordering<br>2. Inspect `AuditRecordAdmin` | Ordered by `['-timestamp', '-id']`; readonly fields configured for immutability | Chronological ordering and admin UI verified | **PASS** |
| **TC-SEC-02.1** | BBMS-SR-002 | Password Security | Verify passwords use one-way hashing and are never stored in plaintext | User creation | 1. Create user with plaintext password<br>2. Inspect `user.password`<br>3. Test `check_password()` | Password hashed with `pbkdf2_sha256`; raw password never matches stored string | Secure one-way hashing confirmed | **PASS** |
| **TC-SEC-03.1** | BBMS-SR-003 | Authorization Bounds | Verify server-side rejection of unauthorized admin endpoint calls | Authenticated non-admin staff | 1. Staff calls `/accounts/admin-dashboard/`<br>2. Staff calls `/accounts/admin-reports/` | Both requests rejected with HTTP 403 Forbidden | Both endpoints strictly blocked (403) | **PASS** |

---

## 3. Traceability to Requirements Specification (SRS)

| SRS Requirement | Description | Mapped Test Cases | Execution Result |
|---|---|---|---|
| **BBMS-F-030** | Authenticate registered users using valid credentials | TC-AUTH-01.1, TC-AUTH-01.2, TC-AUTH-01.3, TC-AUTH-01.4, TC-AUTH-01.5, TC-AUTH-01.6 | **100% Passed** |
| **BBMS-F-031** | Enforce role-based access control to protected functions | TC-AUTH-02.1, TC-AUTH-02.2, TC-AUTH-02.4, TC-AUTH-02.5, TC-AUTH-02.6, TC-AUTH-02.7, TC-AUTH-02.8 | **100% Passed** |
| **BBMS-F-032** | Prevent expired or invalid sessions from accessing protected resources | TC-AUTH-03.1, TC-AUTH-03.2, TC-AUTH-03.3, TC-AUTH-03.4 | **100% Passed** |
| **BBMS-F-033** | Provide admin interface accessible only to authorized administrators | TC-AUTH-02.1, TC-AUTH-02.2, TC-AUTH-02.3, TC-SEC-03.1 | **100% Passed** |
| **BBMS-F-034** | Allow authorized administrators to manage user accounts and roles | TC-ADMIN-01.1, TC-ADMIN-01.2, TC-ADMIN-01.3, TC-ADMIN-01.4 | **100% Passed** |
| **BBMS-F-035** | Provide basic reports for donations, inventory, requests, and issue/fulfillment | TC-ADMIN-02.1, TC-ADMIN-02.2 | **100% Passed** |
| **BBMS-F-036** | Record significant administrative actions for audit purposes | TC-ADMIN-03.1, TC-ADMIN-03.2, TC-ADMIN-03.3 | **100% Passed** |
| **BBMS-SR-002** | Password hashing (PBKDF2/SHA256, no plaintext) | TC-SEC-02.1 | **100% Passed** |
| **BBMS-SR-003** | Server-side authorization verification | TC-AUTH-02.2, TC-AUTH-02.5, TC-SEC-03.1 | **100% Passed** |
| **BBMS-SR-005** | Audit trail capturing user identity, action, timestamp, and IP address | TC-AUTH-01.1, TC-AUTH-01.6, TC-ADMIN-03.1, TC-ADMIN-03.2 | **100% Passed** |

---

## 4. Verification and Sign-Off

- **Prepared by**: C Rohit Reddy (PES2UG24CS125) - Admin Management Module Lead
- **Cross-Tested by**: Deepthi N Reddy (PES2UG24CS149) - Project Coordinator & Cross-Tester
- **Execution Date**: 5th November 2026
- **Test Verdict**: **ALL 32 TESTS PASSED (100% PASS RATE)**
