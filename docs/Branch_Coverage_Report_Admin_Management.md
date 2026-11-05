# Blood Bank Management System (BBMS) - Team 7
## Deliverable 2.b.iv: Branch Coverage Report
### Feature: Admin Management (`accounts` module)

---

### Document Information
- **Course**: Software Engineering (UE24CS341A)
- **Project**: Blood Bank Management System (LifeLine)
- **Subsystem**: Admin Management (`accounts`)
- **Author / Module Lead**: C Rohit Reddy (PES2UG24CS125)
- **Cross Tester**: Deepthi N Reddy (PES2UG24CS149)
- **Tool**: `Coverage.py` v7.17.1 with `--branch` Analysis
- **Date**: 5th November 2026
- **Status**: **100% BRANCH COVERAGE ACHIEVED**

---

## 1. Executive Summary

Branch (Decision) Coverage measures whether all boolean outcomes (both `True` and `False`) of every conditional branch and decision point in the program logic were executed during testing. Achieving 100% branch coverage ensures there are no hidden or untested conditional paths that could result in runtime exceptions or security bypasses.

### Summary Metrics
| Branch Metric | Value |
|---|---|
| **Total Decision Points / Conditional Branches** | 16 Branches |
| **Fully Exercised Branches** | 16 Branches |
| **Partially Exercised Branches (`BrPart`)** | 0 Branches |
| **Unexercised Branches** | 0 Branches |
| **Overall Branch Coverage** | **100.0%** |
| **Overall Module Coverage (Statement + Branch)** | **100.0%** |

---

## 2. Branch Coverage Metrics Table

| File Path | Statements | Missed Stmts | Total Branches | Partial Branches (`BrPart`) | Branch Coverage (%) |
|---|---|---|---|---|---|
| `accounts/middleware.py` | 19 | 0 | 6 | 0 | **100%** |
| `accounts/permissions.py` | 23 | 0 | 4 | 0 | **100%** |
| `accounts/signals.py` | 20 | 0 | 6 | 0 | **100%** |
| `accounts/views.py` | 29 | 0 | 0 | 0 | **100%** |
| `accounts/models.py` | 17 | 0 | 0 | 0 | **100%** |
| `accounts/admin.py` | 15 | 0 | 0 | 0 | **100%** |
| `accounts/apps.py` | 6 | 0 | 0 | 0 | **100%** |
| `accounts/urls.py` | 4 | 0 | 0 | 0 | **100%** |
| `accounts/migrations/*` | 14 | 0 | 0 | 0 | **100%** |
| `accounts/tests.py` | 239 | 0 | 0 | 0 | **100%** |
| **TOTAL** | **386** | **0** | **16** | **0** | **100%** |

---

## 3. In-Depth Conditional Decision Path Analysis

### 3.1 `accounts/middleware.py` (6 Branches Analyzed)

```python
# accounts/middleware.py lines 22-33
if request.user.is_authenticated:                      # Branch 1 & 2
    now = time.time()
    last_activity = request.session.get("last_activity")

    if last_activity is not None:                      # Branch 3 & 4
        if now - last_activity > self.timeout:         # Branch 5 & 6
            logout(request)
            return redirect(settings.LOGIN_URL)

    request.session["last_activity"] = now

response = self.get_response(request)
return response
```

#### Decision Path Trace:
- **Branch 1 (True)**: `request.user.is_authenticated == True`.
  - *Exercised by*: Tests where authenticated admin or staff makes a request (`test_admin_can_access_admin_dashboard`, `test_active_user_session_retains_access`).
- **Branch 2 (False)**: `request.user.is_authenticated == False`.
  - *Exercised by*: `test_unauthenticated_request_middleware_passthrough` and `test_anonymous_user_redirected_from_admin_dashboard`. Request safely bypasses session timestamp logic and proceeds to response handler.
- **Branch 3 (True)**: `last_activity is not None`.
  - *Exercised by*: Subsequent requests in an active session (`test_inactive_user_is_logged_out_after_timeout`, `test_active_user_session_retains_access`).
- **Branch 4 (False)**: `last_activity is None` (First request of a new session).
  - *Exercised by*: `test_valid_admin_login_success` right after authentication before any prior request timestamp was stored.
- **Branch 5 (True)**: `now - last_activity > self.timeout` (Timeout exceeded > 1800s).
  - *Exercised by*: `test_inactive_user_is_logged_out_after_timeout`. Triggers `logout(request)` and redirects to `LOGIN_URL`.
- **Branch 6 (False)**: `now - last_activity <= self.timeout` (Session still valid).
  - *Exercised by*: `test_active_user_session_retains_access`. Updates `last_activity` timestamp and continues.

---

### 3.2 `accounts/permissions.py` (4 Branches Analyzed)

```python
# Decorator 1: operational_staff_required
if not is_operational_staff(request.user):             # Branch 7 & 8
    raise PermissionDenied
return view_func(request, *args, **kwargs)

# Decorator 2: admin_required
if not is_bbms_admin(request.user):                    # Branch 9 & 10
    raise PermissionDenied
return view_func(request, *args, **kwargs)
```

#### Decision Path Trace:
- **Branch 7 (True)**: `not is_operational_staff(request.user) == True`.
  - *Exercised by*: `test_operational_staff_required_decorator` with guest user without staff privileges. Triggers `raise PermissionDenied` (HTTP 403).
- **Branch 8 (False)**: `not is_operational_staff(request.user) == False` (Authorized).
  - *Exercised by*: `test_operational_staff_required_decorator` with staff user. Successfully returns view response (HTTP 200).
- **Branch 9 (True)**: `not is_bbms_admin(request.user) == True`.
  - *Exercised by*: `test_staff_cannot_access_admin_dashboard`, `test_staff_cannot_access_admin_reports`, and `test_authorization_rejection_for_unauthorized_endpoints`. Triggers `raise PermissionDenied` (HTTP 403).
- **Branch 10 (False)**: `not is_bbms_admin(request.user) == False` (Authorized Admin).
  - *Exercised by*: `test_admin_can_access_admin_dashboard` and `test_admin_can_access_admin_reports`. Successfully dispatches to admin views (HTTP 200).

---

### 3.3 `accounts/signals.py` (6 Branches Analyzed)

```python
# Helper 1: get_client_ip
if request is None:                                    # Branch 11 & 12
    return None

forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
if forwarded_for:                                      # Branch 13 & 14
    return forwarded_for.split(",")[0].strip()

return request.META.get("REMOTE_ADDR")

# Helper 2: record_audit
if ip_address is None and request is not None:         # Branch 15 & 16
    ip_address = get_client_ip(request)
```

#### Decision Path Trace:
- **Branch 11 (True)**: `request is None`.
  - *Exercised by*: `test_get_client_ip_forwarded_for_and_remote_addr` passing `None`. Returns `None`.
- **Branch 12 (False)**: `request is not None`.
  - *Exercised by*: Normal HTTP requests containing META dictionary.
- **Branch 13 (True)**: `forwarded_for is not None` (Client behind HTTP proxy / load balancer).
  - *Exercised by*: `test_get_client_ip_forwarded_for_and_remote_addr` with header `203.0.113.195, 70.41.3.18`. Successfully parses first IP (`203.0.113.195`).
- **Branch 14 (False)**: `forwarded_for is None` (Direct socket connection).
  - *Exercised by*: Standard requests where `REMOTE_ADDR` is read directly.
- **Branch 15 (True)**: `ip_address is None and request is not None`.
  - *Exercised by*: Signal handlers `record_login` and `record_logout` which pass `request=request, ip_address=None`, dynamically resolving client IP.
- **Branch 16 (False)**: Condition not met (e.g. `ip_address` explicitly provided or `request` is None).
  - *Exercised by*: `test_record_audit_helper` where `ip_address="192.168.1.50"` was passed explicitly.

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

The **100% branch coverage** metric confirms that:
1. Every access control check reliably executes both permitted and forbidden outcomes.
2. Inactivity timing conditions handle both valid session refreshes and timeout terminations.
3. Network IP resolution operates properly across direct, proxied, and synthetic test scenarios.
4. No unverified execution branches remain in the Admin Management module.
