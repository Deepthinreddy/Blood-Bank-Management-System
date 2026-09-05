# Software Requirements Specification (SRS)

## Project: Blood Bank Management System

**Version:** 1.0\
**Software Engineering - UE24CS341A**\
**Team:** 7\
**Date:** 05-09-2026

## Authors

  Name                  SRN             Section
  --------------------- --------------- ---------
  Deepthi N Reddy       PES2UG24CS149   C
  Hansika.R             PES2UG24CS178   C
  Gurudu Guru Preetam   PES2UG24CS174   C
  C Rohit Reddy         PES2UG24CS125   C

## Revision History

  Version   Date         Author   Change Summary
  --------- ------------ -------- ---------------------------
  1.0       05-09-2026   Team 7   Initial SRS with diagrams

## Approvals

  Role                 Name                  Signature / Email   Date
  -------------------- --------------------- ------------------- ------
  Course Coordinator   Pradeep Kumar Kenny                       

## Table of Contents

1.  [Introduction](#1-introduction)
2.  [Overall Description](#2-overall-description)
3.  [External Interface
    Requirements](#3-external-interface-requirements)
4.  [System Features (Detailed)](#4-system-features-detailed)
5.  [Non-Functional Requirements
    (Detailed)](#5-non-functional-requirements-detailed)
6.  [Quality Attributes & Acceptance
    Tests](#6-quality-attributes--acceptance-tests)
7.  [UML Use-Case Diagram](#7-uml-use-case-diagram)
8.  [Requirements Traceability Matrix
    (RTM)](#8-requirements-traceability-matrix-rtm)

# 1. Introduction

## 1.1 Purpose

This document is a Software Requirements Specification (SRS) for a Blood
Bank Management System (BBMS). It defines functional and non-functional
requirements, interfaces, and verification criteria for a web-based
blood-bank management application. The document is intended to provide a
common reference for instructors, students, developers, testers, and
project stakeholders.

## 1.2 Scope

The Blood Bank Management System covers the management of donors, blood
donations, blood inventory, recipients, blood requests, allocation and
issue of blood, authentication, and administrative operations. It
provides a centralized interface for maintaining records and supporting
day-to-day blood-bank workflows. It excludes clinical diagnosis,
treatment decisions, and internal implementation of external hospital
systems.

## 1.3 Audience

Developers, QA Engineers, Project Stakeholders, Blood-bank Staff,
Administrators, and Assessment Evaluators.

## 1.4 Definitions

  -----------------------------------------------------------------------
  Term                    Full Form               Definition
  ----------------------- ----------------------- -----------------------
  BBMS                    Blood Bank Management   The software system
                          System                  used to manage donors,
                                                  blood inventory,
                                                  recipients, blood
                                                  requests, and related
                                                  blood-bank operations.

  SRS                     Software Requirements   A document that defines
                          Specification           the functional and
                                                  non-functional
                                                  requirements of the
                                                  software system.

  UI                      User Interface          The screens and
                                                  controls through which
                                                  users interact with the
                                                  system.

  API                     Application Programming A set of interfaces
                          Interface               that allows different
                                                  software components to
                                                  communicate with each
                                                  other.

  RBAC                    Role-Based Access       A security mechanism
                          Control                 that restricts system
                                                  functions based on the
                                                  user's assigned role.

  CRUD                    Create, Read, Update,   The basic operations
                          Delete                  used to manage records
                                                  in the system.

  NFR                     Non-Functional          A requirement
                          Requirement             describing system
                                                  qualities such as
                                                  performance, security,
                                                  reliability, or
                                                  usability.

  FR                      Functional Requirement  A requirement
                                                  describing a specific
                                                  function or behaviour
                                                  the system shall
                                                  provide.

  RTM                     Requirements            A table that maps
                          Traceability Matrix     requirements to their
                                                  corresponding design
                                                  references and test
                                                  cases.

  HTTPS                   Hypertext Transfer      A secure version of
                          Protocol Secure         HTTP used to protect
                                                  communication between
                                                  the user and the web
                                                  application.

  TLS                     Transport Layer         A security protocol
                          Security                used to encrypt data
                                                  transmitted over a
                                                  network.
  -----------------------------------------------------------------------

# 2. Overall Description

## 2.1 Product Perspective

The BBMS is a standalone web application for organizing blood-bank
records and operational workflows. It provides a user interface,
application/business logic, authentication and authorization services,
and persistent storage. The system maintains relationships between
donors, donations, blood units, recipients, requests, allocations, and
issue records.

## 2.2 Major Product Functions (Detailed)

-   Donor registration, profile management, eligibility information, and
    donation history.
-   Blood donation recording and blood inventory management.
-   Inventory search, availability/status tracking, and expiry tracking.
-   Recipient registration and recipient record management.
-   Blood request creation, validation, processing, and status tracking.
-   Blood allocation and issue/fulfillment of approved requests.
-   Secure authentication and role-based access control.
-   Administrative user management, reports, and audit monitoring.

## 2.3 User Roles and Characteristics (Expanded)

-   **Staff:** authenticated operational users who manage donors,
    donations, inventory, recipients, and blood requests according to
    assigned permissions.
-   **Admin:** privileged user responsible for user management,
    configuration, reports, and audit information.

## 2.4 Operating Environment

The system will run in a standard web-server or local development
environment. Clients will access the application through modern browsers
such as Chrome, Firefox, Edge, or Safari. A relational database such as
MySQL or PostgreSQL, or an equivalent approved database, may be used for
persistent data storage.

## 2.5 Constraints

-   Protected blood-bank information shall be accessible only to
    authorized users.
-   Only authorized users shall perform approval, allocation, and issue
    operations.
-   The project is designed for a small-to-medium student-project
    workload.
-   Business rules for donor eligibility and blood compatibility shall
    be confirmed by the project team before implementation.
-   The system does not make clinical diagnosis or treatment decisions.
-   The final technology stack may constrain deployment and performance.

# 3. External Interface Requirements

## 3.1 User Interfaces

**Primary UI:** responsive web pages with clear navigation and
role-based menus.

-   Dashboard: summaries of blood inventory, pending requests,
    donors/recipients, and recent activity.
-   Donor pages: registration, search, profile, eligibility, and
    donation history.
-   Inventory pages: blood group, quantity/unit, collection date, expiry
    date, and status.
-   Recipient pages: registration, search, and profile management.
-   Blood Request pages: request creation, review, processing, and
    status.
-   Allocation/Issue pages: assignment of available blood and
    issue/fulfillment recording.
-   Login page and Admin panel for authorized users.
-   User-friendly validation and error messages.

## 3.2 Hardware Interfaces

No special hardware interface is required. Users may access the system
using ordinary computers, laptops, tablets, or smartphones. The server
requires hardware sufficient for the expected project workload.

## 3.3 Software Interfaces

-   Database interface for persistent storage of users, donors,
    donations, inventory, recipients, requests, allocations, and logs.
-   Backend/API interface between the UI and application logic where a
    separated architecture is used.
-   Authentication and authorization components for secure access
    control.
-   Modern web browser interface for client-side interaction.

## 3.4 Communications

-   HTTPS/TLS shall be used for deployed communication carrying
    credentials or sensitive information.
-   JSON may be used for API data exchange if REST-style APIs are
    implemented.
-   HTTP status codes shall distinguish successful requests, validation
    errors, authorization failures, and server errors.
-   Communication or service failures shall be handled without exposing
    sensitive implementation details.

# 4. System Features (Detailed)

Each requirement below includes acceptance criteria and a reference test
case. IDs follow **BBMS-F-###**.

## 4.1 Donor Management

  -------------------------------------------------------------------------------------------------------
  Req ID       Requirement    Type         Priority   Source/Stakeholder   Acceptance     Comments /
               (shall...)                                                  Criteria /     Dependencies
                                                                           Test Case Ref  
  ------------ -------------- ------------ ---------- -------------------- -------------- ---------------
  BBMS-F-001   The system     Functional   High       Blood-bank Staff     Valid data     Database
               shall register                                              creates a      required
               a donor with                                                unique donor   
               required                                                    record. Test:  
               personal and                                                TC-Donor-01    
               blood-group                                                                
               information.                                                               

  BBMS-F-002   The system     Functional   High       Blood-bank Staff     Updated        Authorization
               shall allow                                                 details are    required
               authorized                                                  saved and      
               staff to view                                               displayed.     
               and update                                                  Test:          
               permitted                                                   TC-Donor-02    
               donor details.                                                             

  BBMS-F-003   The system     Functional   High       Blood-bank Staff     Eligibility    Eligibility
               shall record                                                information is rules to be
               donor                                                       stored and     confirmed
               eligibility                                                 retrievable.   
               information                                                 Test:          
               required by                                                 TC-Donor-03    
               the project                                                                
               workflow.                                                                  

  BBMS-F-004   The system     Functional   Medium     Blood-bank Staff     Donor history  Donation module
               shall maintain                                              shows linked   dependency
               donation                                                    valid          
               history                                                     donations.     
               associated                                                  Test:          
               with the                                                    TC-Donor-04    
               correct donor.                                                             
  -------------------------------------------------------------------------------------------------------

## 4.2 Blood Inventory Management

  ------------------------------------------------------------------------------------------------------
  Req ID       Requirement      Type         Priority   Source/Stakeholder   Acceptance   Comments /
               (shall...)                                                    Criteria /   Dependencies
                                                                             Test Case    
                                                                             Ref          
  ------------ ---------------- ------------ ---------- -------------------- ------------ --------------
  BBMS-F-010   The system shall Functional   High       Blood-bank Staff     Valid        Donor record
               record a blood                                                donation is  required
               donation with                                                 stored with  
               donor, date,                                                  mandatory    
               blood group,                                                  fields.      
               quantity/unit,                                                Test:        
               and required                                                  TC-Inv-01    
               status                                                                     
               information.                                                               

  BBMS-F-011   The system shall Functional   High       Blood-bank Staff     Inventory    Inventory
               create or update                                              reflects the database
               corresponding                                                 recorded     required
               blood inventory                                               donation.    
               information from                                              Test:        
               a valid                                                       TC-Inv-02    
               donation.                                                                  

  BBMS-F-012   The system shall Functional   High       Blood-bank Staff     Displayed    Inventory data
               display                                                       stock        required
               available blood                                               matches      
               inventory by                                                  stored       
               blood group and                                               records.     
               status.                                                       Test:        
                                                                             TC-Inv-03    

  BBMS-F-013   The system shall Functional   Medium     Blood-bank Staff     Correct      UI dependency
               allow authorized                                              filtered     
               users to                                                      units are    
               search/filter                                                 displayed.   
               inventory using                                               Test:        
               supported                                                     TC-Inv-04    
               attributes.                                                                

  BBMS-F-014   The system shall Functional   High       Blood-bank Staff     Expired      Expiry rule
               track expiry                                                  units are    required
               information and                                               not treated  
               identify expired                                              as           
               blood units.                                                  available.   
                                                                             Test:        
                                                                             TC-Inv-05    
  ------------------------------------------------------------------------------------------------------

## 4.3 Recipient & Blood Request Management

  ---------------------------------------------------------------------------------------------------------------------------
  Req ID       Requirement         Type         Priority   Source/Stakeholder   Acceptance Criteria Comments / Dependencies
               (shall...)                                                       / Test Case Ref     
  ------------ ------------------- ------------ ---------- -------------------- ------------------- -------------------------
  BBMS-F-020   The system shall    Functional   High       Blood-bank Staff     Valid recipient     Database required
               register recipients                                              receives a unique   
               with required                                                    record. Test:       
               identification and                                               TC-Rec-01           
               request-related                                                                      
               information.                                                                         

  BBMS-F-021   The system shall    Functional   High       Blood-bank Staff     Permitted           Authorization required
               allow authorized                                                 operations work     
               staff to view,                                                   correctly. Test:    
               update, and search                                               TC-Rec-02           
               recipient records.                                                                   

  BBMS-F-022   The system shall    Functional   High       Blood-bank Staff     Valid request       Recipient record required
               create a blood                                                   receives a unique   
               request containing                                               ID. Test: TC-Req-01 
               recipient, blood                                                                     
               group, quantity,                                                                     
               priority, and                                                                        
               required details.                                                                    

  BBMS-F-023   The system shall    Functional   High       Blood-bank Staff     Invalid request is  Rules to be confirmed
               validate mandatory                                               rejected with       
               request fields and                                               feedback. Test:     
               applicable project                                               TC-Req-02           
               business rules.                                                                      

  BBMS-F-024   The system shall    Functional   High       Blood-bank Staff     Valid status        Workflow dependency
               track request                                                    transitions are     
               states such as                                                   displayed. Test:    
               Pending, Approved,                                               TC-Req-03           
               Rejected,                                                                            
               Allocated,                                                                           
               Fulfilled, or                                                                        
               Cancelled.                                                                           

  BBMS-F-025   The system shall    Functional   High       Blood-bank Staff     Only authorized     RBAC dependency
               allow authorized                                                 users can process   
               staff to process                                                 requests. Test:     
               blood requests                                                   TC-Req-04           
               according to                                                                         
               assigned                                                                             
               permissions.                                                                         

  BBMS-F-026   The system shall    Functional   High       Blood-bank Staff     Allocation does not Inventory/compatibility
               allocate available                                               exceed available    rules required
               compatible                                                       stock. Test:        
               inventory to an                                                  TC-Alloc-01         
               approved request.                                                                    

  BBMS-F-027   The system shall    Functional   High       Blood-bank Staff     Issue is recorded   Allocation required
               record                                                           and                 
               issue/fulfillment                                                inventory/request   
               of allocated blood                                               statuses update.    
               and update related                                               Test: TC-Issue-01   
               statuses.                                                                            
  ---------------------------------------------------------------------------------------------------------------------------

## 4.4 Admin & Authentication

  ----------------------------------------------------------------------------------------------------------------
  Req ID       Requirement          Type         Priority   Source/Stakeholder   Acceptance       Comments /
               (shall...)                                                        Criteria / Test  Dependencies
                                                                                 Case Ref         
  ------------ -------------------- ------------ ---------- -------------------- ---------------- ----------------
  BBMS-F-030   The system shall     Functional   High       Admin/Staff          Valid            Authentication
               authenticate                                                      credentials      service required
               registered users                                                  establish a      
               using valid                                                       session; invalid 
               credentials.                                                      credentials are  
                                                                                 denied. Test:    
                                                                                 TC-Auth-01       

  BBMS-F-031   The system shall     Functional   High       Admin                Unauthorized     RBAC required
               enforce role-based                                                roles are        
               access to protected                                               blocked. Test:   
               functions.                                                        TC-Auth-02       

  BBMS-F-032   The system shall     Functional   Medium     Admin/Staff          Expired session  Session
               prevent expired or                                                is denied        management
               invalid sessions                                                  access. Test:    required
               from accessing                                                    TC-Auth-03       
               protected resources.                                                               

  BBMS-F-033   The system shall     Functional   High       Admin                Non-admin access RBAC dependency
               provide an admin                                                  is blocked.      
               interface accessible                                              Test:            
               only to authorized                                                TC-Admin-01      
               administrators.                                                                    

  BBMS-F-034   The system shall     Functional   Medium     Admin                User/role        Admin
               allow authorized                                                  changes take     authorization
               administrators to                                                 effect           required
               manage user accounts                                              correctly. Test: 
               and roles.                                                        TC-Admin-02      

  BBMS-F-035   The system shall     Functional   Medium     Admin                Report values    Reporting
               provide basic                                                     match stored     depends on
               reports for                                                       records. Test:   stored data
               donations,                                                        TC-Admin-03      
               inventory, requests,                                                               
               and                                                                                
               issue/fulfillment.                                                                 

  BBMS-F-036   The system shall     Functional   Medium     Admin                Representative   Audit storage
               record significant                                                actions appear   required
               administrative                                                    with user and    
               actions for audit                                                 timestamp. Test: 
               purposes.                                                         TC-Admin-04      
  ----------------------------------------------------------------------------------------------------------------

# 5. Non-Functional Requirements (Detailed)

NFRs below are measurable and tied to test plans. IDs follow
**BBMS-NF-###**.

  --------------------------------------------------------------------------------------------
  Req ID         Requirement      Category                  Priority       Acceptance Criteria
                                                                           / Measurement
  -------------- ---------------- ------------------------- -------------- -------------------
  BBMS-NF-001    Dashboard and    Performance               High           90th percentile
                 common search                                             response ≤2s. Test:
                 operations shall                                          TC-Perf-01
                 respond within 2                                          
                 seconds for 90%                                           
                 of requests                                               
                 under the                                                 
                 defined project                                           
                 test load.                                                

  BBMS-NF-002    The system shall Performance               Medium         Load/stress test
                 support the                                               completed
                 expected project                                          successfully. Test:
                 workload without                                          TC-Perf-02
                 unacceptable                                              
                 degradation or                                            
                 data corruption.                                          

  BBMS-NF-003    The system shall Reliability               Medium         Availability
                 target at least                                           monitoring meets
                 99% availability                                          target. Test:
                 during planned                                            TC-Reliab-01
                 operational                                               
                 periods,                                                  
                 excluding                                                 
                 maintenance.                                              

  BBMS-NF-004    Protected        Security                  High           Security review
                 communication                                             confirms TLS and
                 shall use                                                 protected
                 HTTPS/TLS and                                             authentication
                 sensitive                                                 traffic. Test:
                 credentials                                               TC-Sec-01
                 shall not be                                              
                 transmitted in                                            
                 plaintext.                                                

  BBMS-NF-005    The application  Usability/Accessibility   Medium         Representative UI
                 shall provide                                             tasks completed on
                 responsive and                                            desktop and mobile.
                 understandable                                            Test: TC-UX-01
                 interfaces on                                             
                 supported modern                                          
                 browsers.                                                 

  BBMS-NF-006    The application  Reliability               High           Failure tests show
                 shall maintain                                            no inconsistent
                 recoverable,                                              request/inventory
                 consistent                                                state. Test:
                 records when                                              TC-Reliab-02
                 validation or                                             
                 transaction                                               
                 errors occur.                                             

  BBMS-NF-007    Core code shall  Maintainability           Medium         Code review
                 be modular and                                            confirms clear
                 documented                                                module boundaries
                 sufficiently for                                          and setup
                 maintenance and                                           documentation.
                 team                                                      Test: TC-Maint-01
                 development.                                              
  --------------------------------------------------------------------------------------------

## 5.1 Security

### 5.1.1 Security Objectives

**SO-001 Confidentiality:** Protect donor, recipient, user-account, and
operational information from unauthorized access or disclosure.

**SO-002 Integrity & Accountability:** Ensure that inventory, requests,
allocations, issues, and administrative actions can only be changed by
authorized users and that significant actions are traceable.

### 5.1.2 Security Requirements

  -----------------------------------------------------------------------------------
  Req ID         Requirement        Type           Priority       Acceptance Criteria
                 (shall...)                                       / Test Case Ref
  -------------- ------------------ -------------- -------------- -------------------
  BBMS-SR-001    The system shall   Security       High           No protected
                 use HTTPS/TLS for                                endpoint uses
                 deployed                                         plaintext HTTP.
                 communication                                    Test: TC-Sec-01
                 involving                                        
                 credentials or                                   
                 sensitive data.                                  

  BBMS-SR-002    The system shall   Security       High           Database/code
                 store user                                       review confirms
                 passwords using a                                secure password
                 secure one-way                                   storage. Test:
                 password-hashing                                 TC-Sec-02
                 mechanism and                                    
                 shall not store                                  
                 plaintext                                        
                 passwords.                                       

  BBMS-SR-003    The system shall   Security       High           Unauthorized role
                 enforce role-based                               access is rejected.
                 authorization for                                Test: TC-Sec-03
                 administrative,                                  
                 inventory,                                       
                 approval,                                        
                 allocation, and                                  
                 issue operations.                                

  BBMS-SR-004    The system shall   Security       High           Security tests
                 validate user                                    reject
                 input and use safe                               malicious/invalid
                 database                                         input. Test:
                 operations to                                    TC-Sec-04
                 reduce injection                                 
                 and                                              
                 malformed-input                                  
                 risks.                                           

  BBMS-SR-005    The system shall   Security       Medium         Audit trail
                 record significant                               contains
                 administrative and                               representative
                 operational                                      events. Test:
                 actions with user                                TC-Sec-05
                 identity and                                     
                 timestamp where                                  
                 applicable.                                      
  -----------------------------------------------------------------------------------

# 6. Quality Attributes & Acceptance Tests

-   **Exit criteria for acceptance:** All high-priority functional
    requirements implemented and verified, no critical NFR failures, and
    the RTM shows all required test cases.
-   **Acceptance test suites:** Authentication, Donor Management,
    Inventory, Recipient/Request, Allocation/Issue, Performance,
    Security, and Usability tests.
-   **Correctness:** Required workflows shall produce the expected
    records and status changes.
-   **Usability:** Common tasks shall be understandable and navigable
    without extensive guidance.
-   **Reliability:** Errors shall be handled without corrupting request
    or inventory state.
-   **Maintainability:** The implementation shall remain modular and
    documented.

# 7. UML Use-Case Diagram

## 7.1 Blood Request & Administration Use-Case Diagram

![Blood Request & Administration Use-Case
Diagram](page_11_image_1.png)

## 7.2 Donor & Blood Bank Staff Use-Case Diagram

![Donor & Blood Bank Staff Use-Case
Diagram](page_12_image_1.png)

# 8. Requirements Traceability Matrix (RTM)

  --------------------------------------------------------------------------------------------------
  Req ID        Requirement     Section Ref Module           Test Case(s)   Status     Comments
                Short           / Design                                    (N/P/A)    
                                Spec                                                   
  ------------- --------------- ----------- ---------------- -------------- ---------- -------------
  BBMS-F-001    Register donor  4.1         Donor Management TC-Donor-01    N          

  BBMS-F-010    Record donation 4.2         Blood Inventory  TC-Inv-01      N          

  BBMS-F-012    View inventory  4.2         Blood Inventory  TC-Inv-03      N          

  BBMS-F-020    Register        4.3         Recipient &      TC-Rec-01      N          
                recipient                   Blood Request                              

  BBMS-F-022    Create blood    4.3         Recipient &      TC-Req-01      N          
                request                     Blood Request                              

  BBMS-F-026    Allocate blood  4.3         Recipient &      TC-Alloc-01    N          
                                            Blood Request                              

  BBMS-F-027    Issue blood     4.3         Recipient &      TC-Issue-01    N          
                                            Blood Request                              

  BBMS-F-030    Authenticate    4.4         Admin &          TC-Auth-01     N          
                user                        Authentication                             

  BBMS-F-031    Role-based      4.4         Admin &          TC-Auth-02     N          
                access                      Authentication                             

  BBMS-F-033    Admin panel     4.4         Admin &          TC-Admin-01    N          
                access                      Authentication                             

  BBMS-F-035    Reports         4.4         Admin &          TC-Admin-03    N          
                                            Authentication                             

  BBMS-NF-001   Response time   5 / Perf-01 All modules      TC-Perf-01     N          Performance
                target                                                                 target

  BBMS-NF-003   Availability    5 /         All modules      TC-Reliab-01   N          Uptime
                ≥99%            Reliab-01                                              monitoring

  BBMS-SR-001   TLS for         5.1.2 /     Admin &          TC-Sec-01      N          
                protected       Sec-01      Authentication                             
                traffic                                                                

  BBMS-SR-002   Password        5.1.2 /     Admin &          TC-Sec-02      N          
                hashing         Sec-02      Authentication                             

  BBMS-SR-003   Authorization   5.1.2 /     All modules      TC-Sec-03      N          
                                Sec-03                                                 

  BBMS-SR-005   Audit trail     5.1.2 /     Admin &          TC-Sec-05      N          
                                Sec-05      Authentication                             
  --------------------------------------------------------------------------------------------------
