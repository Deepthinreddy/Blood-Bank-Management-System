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
