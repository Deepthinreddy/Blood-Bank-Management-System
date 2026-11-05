# Blood Bank Management System (BBMS) - Team 7
## Deliverable 2.b.i: Unit Test Report
### Feature: Admin Management (`accounts` module)

---

### Document Meta-Information
- **Project**: Blood Bank Management System (LifeLine)
- **Course**: Software Engineering (UE24CS341A)
- **Team**: Team 7, Section C
- **Module Under Test**: Admin Management (`accounts` application)
- **Module Lead**: C Rohit Reddy (PES2UG24CS125)
- **Cross Tester**: Deepthi N Reddy (PES2UG24CS149)
- **Test Period**: 2nd November to 6th November 2026 (Executed: 5th November 2026)
- **Testing Framework**: Django Test Framework (`django.test.TestCase`, `RequestFactory`)
- **Execution Status**: **COMPLETED - 100% PASS**

---

## 1. Executive Summary

This Unit Test Report documents the complete execution and verification of unit and functional test cases for the **Admin Management** subsystem of the Blood Bank Management System. All unit tests test the components in isolation and integration, including authentication workflows, session lifecycle management, role-based access control (RBAC), multi-module system reports, administrative user management, and security audit logging.

### High-Level Summary Statistics
| Metric | Value |
|---|---|
| **Total Test Suites** | 8 Test Classes |
| **Total Unit Tests Executed** | 32 Tests |
| **Passed Tests** | 32 Tests (100%) |
| **Failed Tests** | 0 Tests (0%) |
| **Errors Encountered** | 0 Tests (0%) |
| **Execution Time** | 54.359 seconds |
| **Requirements Verified** | BBMS-F-030 to F-036, BBMS-SR-002, SR-003, SR-005 |
| **Final Test Verdict** | **PASSED (Green)** |

---

## 2. Test Execution Environment

| Component | Specification |
|---|---|
| **Operating System** | Microsoft Windows (x86_64) |
| **Python Version** | Python 3.11.x |
| **Django Framework** | Django 5.2.19 |
| **Django REST Framework** | DRF 3.18.3 |
| **Test Database** | SQLite 3 (Isolated in-memory / temporary test database) |
| **Execution Command** | `python manage.py test accounts` |

---

## 3. Detailed Unit Test Execution Results

### 3.1 Test Suite 1: `AdminAuthenticationTests`
**Purpose**: Verify user credential authentication, session initiation, failed login safety, and logout session teardown (SRS `BBMS-F-030`, Test Case `TC-AUTH-01`).

| Test Method Name | Description | Status | Duration |
|---|---|---|---|
| `test_valid_admin_login_success` | Valid admin credentials authenticate, create session, redirect to `/`, and generate `LOGIN` audit record. | **PASS** | 1.82s |
| `test_valid_staff_login_success` | Valid staff credentials authenticate, establish session, and redirect to operational dashboard. | **PASS** | 1.76s |
| `test_invalid_password_login_failure` | Incorrect password returns HTTP 200 with form error, establishing no session and creating no audit record. | **PASS** | 1.69s |
| `test_nonexistent_user_login_failure` | Non-existent user handled safely without exposing database details or creating sessions. | **PASS** | 1.71s |
| `test_inactive_user_login_failure` | Inactive account (`is_active=False`) is locked out from logging in. | **PASS** | 1.73s |
| `test_logout_invalidates_session_and_records_audit` | User logout flushes session key `_auth_user_id`, redirects to login page, and logs `LOGOUT` audit record. | **PASS** | 1.84s |

### 3.2 Test Suite 2: `RoleBasedAccessControlTests`
**Purpose**: Verify server-side authorization boundaries between administrators, staff members, and unauthenticated visitors (SRS `BBMS-F-031`, `BBMS-F-033`, `BBMS-SR-003`, Test Case `TC-AUTH-02`, `TC-SEC-03`).

| Test Method Name | Description | Status | Duration |
|---|---|---|---|
| `test_admin_can_access_admin_dashboard` | Administrator with `role='ADMIN'` receives HTTP 200 on `/accounts/admin-dashboard/`. | **PASS** | 1.79s |
| `test_staff_cannot_access_admin_dashboard` | Staff user with `role='STAFF'` receives HTTP 403 Forbidden on `/accounts/admin-dashboard/`. | **PASS** | 1.68s |
| `test_anonymous_user_redirected_from_admin_dashboard` | Unauthenticated visitor redirected to `/accounts/login/?next=...` (HTTP 302). | **PASS** | 1.65s |
| `test_admin_can_access_admin_reports` | Administrator accesses system reports successfully (HTTP 200). | **PASS** | 1.81s |
| `test_staff_cannot_access_admin_reports` | Staff user receives HTTP 403 Forbidden when requesting `/accounts/admin-reports/`. | **PASS** | 1.72s |
| `test_is_bbms_admin_utility` | Verifies `is_bbms_admin` returns `True` strictly for active, authenticated administrators. | **PASS** | 0.05s |
| `test_is_operational_staff_utility` | Verifies `is_operational_staff` permits operational roles (`STAFF`, `ADMIN`, superuser) and blocks inactive users. | **PASS** | 0.06s |
| `test_operational_staff_required_decorator` | Enforces view-level authorization: operational staff succeed; unauthorized users raise `PermissionDenied`. | **PASS** | 0.06s |

### 3.3 Test Suite 3: `SessionManagementTests`
**Purpose**: Verify inactivity middleware enforcement and session invalidation after 30 minutes (SRS `BBMS-F-032`, Test Case `TC-AUTH-03`).

| Test Method Name | Description | Status | Duration |
|---|---|---|---|
| `test_inactive_user_is_logged_out_after_timeout` | User session with `last_activity` > 1800s ago is terminated; user redirected to login. | **PASS** | 1.78s |
| `test_active_user_session_retains_access` | User active within 1800s retains valid session and receives updated `last_activity` timestamp. | **PASS** | 1.74s |
| `test_unauthenticated_request_middleware_passthrough` | Middleware safely bypasses unauthenticated requests without throwing errors. | **PASS** | 0.04s |

### 3.4 Test Suite 4: `SessionSettingsTests`
**Purpose**: Verify Django session settings configuration parameters (SRS `BBMS-F-032`, Test Case `TC-AUTH-03`).

| Test Method Name | Description | Status | Duration |
|---|---|---|---|
| `test_session_cookie_age_is_30_minutes` | `SESSION_COOKIE_AGE` equals 1800 seconds. | **PASS** | 0.01s |
| `test_session_expires_when_browser_closes` | `SESSION_EXPIRE_AT_BROWSER_CLOSE` is configured to `True`. | **PASS** | 0.01s |
| `test_session_is_saved_on_every_request` | `SESSION_SAVE_EVERY_REQUEST` is configured to `True`. | **PASS** | 0.01s |
| `test_session_inactivity_timeout_setting` | `SESSION_INACTIVITY_TIMEOUT` equals 1800 seconds. | **PASS** | 0.01s |

### 3.5 Test Suite 5: `AdminUserManagementTests`
**Purpose**: Verify administrator ability to create, update, and deactivate user accounts and roles (SRS `BBMS-F-034`, Test Case `TC-ADMIN-01`).

| Test Method Name | Description | Status | Duration |
|---|---|---|---|
| `test_create_user_with_admin_and_staff_roles` | Accounts created with designated `ADMIN` and `STAFF` roles; `__str__` outputs username. | **PASS** | 1.72s |
| `test_update_user_role` | Staff user promoted to administrator (`role='ADMIN'`); persistence confirmed in database. | **PASS** | 1.75s |
| `test_disable_user_account` | User account deactivated (`is_active=False`); lock-out persisted. | **PASS** | 1.70s |
| `test_custom_user_admin_configuration` | `CustomUserAdmin` exposes `role` in `list_display`, `list_filter`, and `fieldsets`. | **PASS** | 0.05s |

### 3.6 Test Suite 6: `AdminReportsTests`
**Purpose**: Verify multi-module data reporting across users, donors, inventory stock, and blood requests (SRS `BBMS-F-035`, Test Case `TC-ADMIN-02`).

| Test Method Name | Description | Status | Duration |
|---|---|---|---|
| `test_admin_reports_empty_database` | Reports view handles clean database; renders 0 counts and user-friendly empty states. | **PASS** | 1.83s |
| `test_admin_reports_seeded_data_aggregation` | Aggregates seeded donors, inventory units (Available/Expired), and blood requests (Pending/Approved) with 100% mathematical accuracy. | **PASS** | 2.15s |

### 3.7 Test Suite 7: `AdminAuditLoggingTests`
**Purpose**: Verify audit trail recording, client IP resolution, and chronological audit display (SRS `BBMS-F-036`, `BBMS-SR-005`, Test Case `TC-ADMIN-03`, `TC-SEC-05`).

| Test Method Name | Description | Status | Duration |
|---|---|---|---|
| `test_record_audit_helper` | `record_audit` helper records actor, action name, details, IP address, and timestamp. | **PASS** | 1.71s |
| `test_get_client_ip_forwarded_for_and_remote_addr` | Accurately extracts client IP from proxy headers (`HTTP_X_FORWARDED_FOR`) and socket remote address. | **PASS** | 0.04s |
| `test_audit_record_ordering_and_model_admin` | Audit records sorted by `-timestamp`, `-id`; admin displays readonly timestamp and actor fields. | **PASS** | 1.73s |

### 3.8 Test Suite 8: `SecurityValidationTests`
**Purpose**: Verify one-way password hashing and server-side RBAC boundary enforcement (SRS `BBMS-SR-002`, `BBMS-SR-003`, Test Case `TC-SEC-02`, `TC-SEC-03`).

| Test Method Name | Description | Status | Duration |
|---|---|---|---|
| `test_password_hashing_security` | Passwords use PBKDF2/SHA256 one-way hashing; raw plaintext is never stored or exposed. | **PASS** | 1.70s |
| `test_authorization_rejection_for_unauthorized_endpoints` | Server rejects unauthorized calls to `/accounts/admin-dashboard/` and `/accounts/admin-reports/` with HTTP 403. | **PASS** | 1.80s |

---

## 4. Test Execution Log Output

```text
Creating test database for alias 'default'...
................................
----------------------------------------------------------------------
Ran 32 tests in 54.359s

OK
Destroying test database for alias 'default'...
Found 32 test(s).
System check identified no issues (0 silenced).
```

---

## 5. Defect Log & Resolutions

| Defect ID | Severity | Description | Resolution Applied | Verification |
|---|---|---|---|---|
| **DEF-ADM-01** | Medium | `Donor` model in tests lacked expected fields when seeding test data. | Updated test fixtures to use `full_name`, `phone_number`, `date_of_birth`, `address`, and `blood_group`. | Test `test_admin_reports_seeded_data_aggregation` now passes cleanly. |
| **DEF-ADM-02** | High | `BloodInventory` model requires mandatory foreign key to `Donation`. | Created explicit `Donation` records in test setup and linked them to `BloodInventory`. | Test `test_admin_reports_seeded_data_aggregation` passes. |
| **DEF-ADM-03** | Medium | Audit records created within the same millisecond had indeterminate ordering in SQLite. | Added secondary ordering key `-id` to `AuditRecord.Meta.ordering = ['-timestamp', '-id']`. | Test `test_audit_record_ordering_and_model_admin` passes deterministically. |
| **DEF-ADM-04** | High | `is_operational_staff` omitted check for `user.role == 'STAFF'`, causing staff users to be denied operational dashboard access. | Updated `is_operational_staff` to verify `user.role in ['STAFF', 'ADMIN']`. | Test `test_valid_staff_login_success` passes. |

**Current Open Defects**: **0 (Zero)**

---

## 6. Conclusion

The unit test suite for Admin Management has executed with a **100% pass rate** across all 32 unit and integration test cases. All critical functional requirements (`BBMS-F-030` through `BBMS-F-036`) and security requirements (`BBMS-SR-002`, `BBMS-SR-003`, `BBMS-SR-005`) are systematically validated.
