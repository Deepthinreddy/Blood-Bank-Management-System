# Blood Bank Management System (BBMS) - Team 7
## Deliverable 2.b.iii: Code Coverage Report (Statement Coverage)
### Feature: Admin Management (`accounts` module)

---

### Document Information
- **Course**: Software Engineering (UE24CS341A)
- **Project**: Blood Bank Management System (LifeLine)
- **Subsystem**: Admin Management (`accounts`)
- **Author / Module Lead**: C Rohit Reddy (PES2UG24CS125)
- **Cross Tester**: Deepthi N Reddy (PES2UG24CS149)
- **Measurement Tool**: `Coverage.py` v7.17.1
- **Command Executed**: `coverage run --branch --source=accounts manage.py test accounts && coverage report -m`
- **Date**: 5th November 2026
- **Status**: **100% CODE COVERAGE ACHIEVED**

---

## 1. Executive Summary

This Code Coverage Report measures the line and statement coverage achieved during the execution of the automated test suite on the **Admin Management** subsystem. Every executable statement across models, views, templates backend logic, authentication middleware, permission wrappers, signal handlers, and admin configurations was exercised by the unit test suite.

### Global Coverage Highlights
- **Total Executable Statements**: 386
- **Total Statements Executed**: 386
- **Statements Missed**: 0
- **Overall Statement Coverage**: **100.0%**
- **HTML Artifact**: Available at [`docs/coverage_html/index.html`](coverage_html/index.html)

---

## 2. Statement Coverage Summary Table

| Module File | Total Statements | Missed Statements | Statement Coverage (%) | Missing Lines |
|---|---|---|---|---|
| `accounts/__init__.py` | 0 | 0 | **100%** | None |
| `accounts/admin.py` | 15 | 0 | **100%** | None |
| `accounts/apps.py` | 6 | 0 | **100%** | None |
| `accounts/middleware.py` | 19 | 0 | **100%** | None |
| `accounts/migrations/0001_initial.py` | 8 | 0 | **100%** | None |
| `accounts/migrations/0002_auditrecord.py` | 6 | 0 | **100%** | None |
| `accounts/migrations/__init__.py` | 0 | 0 | **100%** | None |
| `accounts/models.py` | 17 | 0 | **100%** | None |
| `accounts/permissions.py` | 23 | 0 | **100%** | None |
| `accounts/signals.py` | 20 | 0 | **100%** | None |
| `accounts/urls.py` | 4 | 0 | **100%** | None |
| `accounts/views.py` | 29 | 0 | **100%** | None |
| `accounts/tests.py` | 239 | 0 | **100%** | None |
| **TOTAL (Admin Management Module)** | **386** | **0** | **100%** | **None** |

---

## 3. Detailed Component Statement Analysis

### 3.1 Views Layer (`accounts/views.py`) — 29/29 Statements (100%)
- **`admin_dashboard` View**:
  - Tested for authenticated administrators (`role='ADMIN'`) rendering statistics for accounts, active users, donors, recent activity, and user management capabilities.
  - Tested for unauthorized staff users triggering `PermissionDenied` (HTTP 403).
  - Tested for anonymous users redirecting to `/accounts/login/?next=...`.
- **`admin_reports` View**:
  - Tested for empty database states (rendering zero counts and fallback empty-state cards).
  - Tested for seeded multi-module database states calculating aggregates across `User`, `Donor`, `BloodInventory`, and `BloodRequest`.
  - All aggregation queries, queryset mappings, and context assignments executed completely.

### 3.2 Security & Permissions Layer (`accounts/permissions.py`) — 23/23 Statements (100%)
- **`is_bbms_admin(user)`**: Evaluated with active admins (`True`), active staff (`False`), and inactive admins (`False`).
- **`is_operational_staff(user)`**: Evaluated with staff users (`True`), superusers (`True`), admin users (`True`), and inactive users (`False`).
- **`operational_staff_required(view_func)`**: Tested allowing operational staff and raising `PermissionDenied` on non-staff accounts.
- **`admin_required(view_func)`**: Tested allowing admin users and raising `PermissionDenied` on staff accounts.

### 3.3 Middleware Layer (`accounts/middleware.py`) — 19/19 Statements (100%)
- **`SessionInactivityMiddleware`**:
  - `__init__` initializes default timeout (1800s).
  - `__call__` checks `request.user.is_authenticated`.
  - Evaluates both cases where `last_activity is None` (initial request in session) and `last_activity is not None`.
  - Exercises timeout expiration branch (`now - last_activity > self.timeout`) executing `logout(request)` and redirect to `settings.LOGIN_URL`.
  - Exercises active session branch updating `request.session['last_activity'] = now`.
  - Exercises unauthenticated passthrough branch directly calling `get_response(request)`.

### 3.4 Signals & Audit Trail (`accounts/signals.py`) — 20/20 Statements (100%)
- **`get_client_ip(request)`**:
  - Tested when `request is None` (returns `None`).
  - Tested when `HTTP_X_FORWARDED_FOR` is set with comma-separated proxy IPs (extracts first IP).
  - Tested when `HTTP_X_FORWARDED_FOR` is absent and `REMOTE_ADDR` is used.
- **`record_audit(user, action, details, request, ip_address)`**:
  - Tested with direct IP input and automatic extraction from request.
- **`record_login` & `record_logout`**:
  - Fired and verified during actual user login and logout sequences.

### 3.5 Models Layer (`accounts/models.py`) — 17/17 Statements (100%)
- **`User` Model**:
  - Custom `role` choices (`ADMIN`, `STAFF`) stored and validated.
  - `__str__` method executed and verified.
- **`AuditRecord` Model**:
  - All model attributes (`user`, `action`, `details`, `timestamp`, `ip_address`) populated and stored.
  - Meta ordering `['-timestamp', '-id']` exercised.
  - `__str__` method tested returning `f"{action} - {timestamp}"`.

### 3.6 Administration Configuration (`accounts/admin.py`) — 15/15 Statements (100%)
- `CustomUserAdmin` registration and fieldset declarations verified.
- `AuditRecordAdmin` registration, `readonly_fields`, `search_fields`, and `list_display` tested.

---

## 4. Verification Command Output Log

```text
Name                                      Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------------------------
accounts\__init__.py                          0      0      0      0   100%
accounts\admin.py                            15      0      0      0   100%
accounts\apps.py                              6      0      0      0   100%
accounts\middleware.py                       19      0      6      0   100%
accounts\migrations\0001_initial.py           8      0      0      0   100%
accounts\migrations\0002_auditrecord.py       6      0      0      0   100%
accounts\migrations\__init__.py               0      0      0      0   100%
accounts\models.py                           17      0      0      0   100%
accounts\permissions.py                      23      0      4      0   100%
accounts\signals.py                          20      0      6      0   100%
accounts\tests.py                           239      0      0      0   100%
accounts\urls.py                              4      0      0      0   100%
accounts\views.py                            29      0      0      0   100%
-------------------------------------------------------------------------------------
TOTAL                                       386      0     16      0   100%
```

---

## 5. Conclusion

The Admin Management module achieved **100% statement coverage**. There are no untested lines of code, orphaned logic, or unexercised error handling blocks.
