# Blood Bank Management System (LifeLine)
## Sprint-3 Deliverables: Admin Management Subsystem

---

### Team & Deliverable Details
- **Project**: Blood Bank Management System (LifeLine)
- **Course**: Software Engineering (UE24CS341A)
- **Team**: Team 7, Section C
- **Assigned Feature**: Admin Management (`accounts` module)
- **Feature Owner**: C Rohit Reddy (PES2UG24CS125)
- **Cross Tester**: Deepthi N Reddy (PES2UG24CS149)
- **Sprint Window**: 2nd November to 6th November 2026
- **Status**: **ALL DELIVERABLES COMPLETED & VERIFIED**

---

## 1. Deliverables Directory Index (`docs/`)

All required reports and documents for Mini-Project Deliverables Part-3 have been compiled and placed directly in the `docs/` folder of the repository:

| Deliverable ID | Requirement | Generated Document File | Status |
|---|---|---|---|
| **Deliverable 1** | Test Cases Updation | [`Updated_Test_Cases_Admin_Management.md`](Updated_Test_Cases_Admin_Management.md) | **Completed** |
| **Deliverable 2.b.i** | Unit Test Report | [`Unit_Test_Report_Admin_Management.md`](Unit_Test_Report_Admin_Management.md) | **Completed (32/32 Pass)** |
| **Deliverable 2.b.ii** | System Validation Report | [`System_Validation_Report_Admin_Management.md`](System_Validation_Report_Admin_Management.md) | **Completed (100% Compliant)** |
| **Deliverable 2.b.iii** | Code Coverage Report | [`Code_Coverage_Report_Admin_Management.md`](Code_Coverage_Report_Admin_Management.md) | **Completed (100% Statement Coverage)** |
| **Deliverable 2.b.iv** | Branch Coverage Report | [`Branch_Coverage_Report_Admin_Management.md`](Branch_Coverage_Report_Admin_Management.md) | **Completed (100% Branch Coverage)** |
| **Interactive HTML** | HTML Coverage Browser | [`coverage_html/index.html`](coverage_html/index.html) | **Generated** |

---

## 2. Sprint-3 Development & Spill-over Activity Summary

In accordance with Section 3 of the Mini-Project Deliverables Part-3 guidelines ("*Optional Sprint-3 - Parallel Activity: If there is another Sprint required due to spill overs then complete the development during this week and call it as Sprint-3*"), the following administrative capabilities were finalized and verified:

1. **Multi-Module Cross-System Reporting (`BBMS-F-035`)**:
   - Expanded `/accounts/admin-reports/` from basic donor counts into an integrated operational dashboard aggregating data across `donors`, `inventory`, and `blood_requests`.
   - Real-time aggregation of inventory stock by blood group, active available units vs. expired units, and blood requests organized by lifecycle status (`PENDING`, `APPROVED`, etc.).
   - Clean UI presentation with empty-state resilience, responsive metrics cards, and status badges.

2. **Unified Administrative Audit Utility (`BBMS-F-036`, `BBMS-SR-005`)**:
   - Implemented `record_audit(user, action, details, request, ip_address)` to standardize security audit recording.
   - Enhanced proxy IP resolution (`HTTP_X_FORWARDED_FOR` + `REMOTE_ADDR`) for production reverse-proxy setups.
   - Added secondary index sorting (`ordering = ['-timestamp', '-id']`) to eliminate non-deterministic race conditions during concurrent event logging.

3. **Role-Based Access Control Refinements (`BBMS-F-031`, `BBMS-SR-003`)**:
   - Adjusted `is_operational_staff` to permit users with `role='STAFF'` or `role='ADMIN'`, ensuring operational staff seamlessly access common blood-banking workflows while maintaining strict boundary separation from admin tools.
   - Verified server-side HTTP 403 Forbidden enforcement on all administrative views.

---

## 3. Testing & Verification Summary

- **Total Unit & Integration Tests**: 32 automated tests in `accounts/tests.py`.
- **Pass Rate**: **100%** (0 failures, 0 errors).
- **Statement Coverage**: **100%** (386 / 386 statements executed).
- **Branch Coverage**: **100%** (16 / 16 decision branches exercised).
- **Execution Command**:
  ```bash
  coverage run --branch --source=accounts manage.py test accounts
  coverage report -m
  ```

---

## 4. Sign-Off & Approvals
- **Developer & Author**: C Rohit Reddy (`rohit1234-spec` / PES2UG24CS125)
- **Coordinator & Cross-Tester**: Deepthi N Reddy (PES2UG24CS149)
- **Date**: 5th November 2026
