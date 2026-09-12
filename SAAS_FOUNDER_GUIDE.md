# Frappe LMS SaaS: Master Founder & Technical Playbook

Welcome to the **Frappe LMS SaaS Engine**. This comprehensive playbook is created specifically for launching, operating, monetizing, and scaling a multi-tenant or standalone Learning Management System (LMS) business based on **Frappe Learning** ([frappe.io/learning](https://frappe.io/learning)).

---

## Table of Contents
1. [Platform Architecture & Core Capabilities](#1-platform-architecture--core-capabilities)
2. [SaaS Business Models (B2B Multi-Tenant vs. B2C Academy)](#2-saas-business-models)
3. [Native Multi-Tenancy Architecture](#3-native-multi-tenancy-architecture)
4. [Instant Local Preview & Cloudflare Tunnel Sharing](#4-instant-local-preview--cloudflare-tunnel-sharing)
5. [Production Cloud VPS Deployment ($6–$12/mo)](#5-production-cloud-vps-deployment)
6. [Payment Gateway & Monetization Setup](#6-payment-gateway--monetization-setup)
7. [White-Labeling & Custom Branding](#7-white-labeling--custom-branding)
8. [Automated Provisioning Workflow](#8-automated-provisioning-workflow)
9. [Certifications, Quizzes & Student Engagement](#9-certifications-quizzes--student-engagement)
10. [Day-2 Operations: Backups, Maintenance & Scaling](#10-day-2-operations)

---

## 1. Platform Architecture & Core Capabilities

Frappe LMS is built on the enterprise-grade **Frappe Framework (v15)**:
* **Frontend**: Responsive Vue 3 Single-Page Application (Frappe UI) delivering an ultra-clean, modern student/instructor experience at `/lms`.
* **Administrative Desk**: Enterprise back-office at `/app` for deep permissions, reporting, custom workflows, DocType customization, and user role management.
* **Backend Stack**: Python 3.11/3.12 + Gunicorn WSGI + Asynchronous background task workers (Redis Queue) + Real-time notifications and chat (Node.js SocketIO).
* **Database**: MariaDB 10.8+ with native `utf8mb4` multilingual support.

### Key Out-of-the-Box Features:
* **Course Structure**: 3-tier hierarchy: Course -> Chapters -> Lessons.
* **Multi-Media Content**: HTML5 video streaming, YouTube/Vimeo embeds, downloadable attachments, PDF readers, rich markdown articles.
* **Assessments**: Timed quizzes, multiple-choice, open-ended evaluations, and automated server-side auto-grading.
* **Certificates**: Instant verifiable PDF certificate generation with embedded verification QR codes.
* **Live Classes**: Zoom integration and scheduled cohort batches.
* **Community**: Discussion forums per lesson, student progress tracking, and batch leaderboards.

---

## 2. SaaS Business Models

With Frappe LMS, your friend can operate two lucrative business models:

### Model A: B2B Multi-Tenant LMS SaaS (The "Shopify for Academies")
* **Concept**: Sell independent, white-labeled LMS portals to schools, training institutes, universities, and enterprise HR departments.
* **Pricing**: Monthly recurring subscription (e.g., $49/mo for Starter, $199/mo for Pro, $499/mo for Enterprise).
* **Isolation**: Each customer receives their own subdomain (e.g., `oxford.yourlmssaas.com`) or custom domain (`learn.oxford.org`), with their own private database, instructors, and branding.

### Model B: B2C / Creator Course Marketplace (The "Udemy / MasterClass" Model)
* **Concept**: Host a flagship academy where creators and instructors sell courses directly to students.
* **Revenue**: Charge course purchase fees (e.g. $99 per course) or monthly membership passes, with platform revenue share.

---

## 3. Native Multi-Tenancy Architecture

Frappe Framework possesses one of the most mature multi-tenant engines in the open-source world.

```
                  Internet (Students & Instructors)
                                 │
                                 ▼
                     Nginx Reverse Proxy (80/443)
                      (Route by HTTP Host header)
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
  client1.lmssaas.com    client2.lmssaas.com    academy.customdomain.org
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 ▼
                   Gunicorn WSGI / Frappe Bench
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
    MariaDB Database       MariaDB Database       MariaDB Database
      (_client1_db)          (_client2_db)          (_academy_db)
```

* **No Code Duplication**: All tenants share the same containerized Frappe bench code.
* **Total Data Isolation**: Each tenant has an independent database and private upload folder. A failure or query in Tenant A can never compromise Tenant B.

---

## 4. Instant Local Preview & Cloudflare Tunnel Sharing

If you are running the project on your Windows machine and want to show your friend a fully interactive live demo **today**:

### Step 1: Launch the Containers
Ensure Docker Desktop is installed and running, then execute:
```powershell
powershell -File windows\setup-windows.ps1
```

### Step 2: Create the Instant Public Link
Run the tunnel launcher:
```powershell
powershell -File windows\share-tunnel.ps1
```
This script automatically acquires `cloudflared.exe` and gives you an instant, secure HTTPS URL (e.g., `https://learning-preview-xyz.trycloudflare.com`).
* Send this link to your friend!
* They can access the full LMS portal from their laptop or phone anywhere in the world.

---

## 5. Production Cloud VPS Deployment ($6–$12/mo)

When your friend is ready to launch the 24/7 commercial SaaS:

### Recommended VPS Providers:
* **Hetzner Cloud**: CPX21 (3 vCPU, 4GB RAM) ~ €7/month (Exceptional price-performance).
* **DigitalOcean**: Basic Droplet (2 vCPU, 4GB RAM) ~ $24/month.
* **Linode / Akamai**: Shared 4GB ~ $20/month.
* **OS**: Clean **Ubuntu 22.04 LTS** or **Ubuntu 24.04 LTS**.

### 1-Command Automated Deployment:
1. SSH into your VPS:
   ```bash
   ssh root@<YOUR_SERVER_IP>
   ```
2. Clone this repository onto the server:
   ```bash
   git clone <REPO_URL> /opt/frappe_lms_saas
   cd /opt/frappe_lms_saas
   ```
3. Run the automated installer:
   ```bash
   bash cloud/deploy-vps.sh lms.yourdomain.com
   ```
The script automatically:
* Installs Docker & Compose.
* Hardens the firewall (UFW).
* Generates secure, random database and admin credentials.
* Deploys the multi-container cluster.
* Configures systemd for automated recovery on reboot.

---

## 6. Payment Gateway & Monetization Setup

The platform includes **Frappe Payments** (`frappe/payments`), supporting:
* **Stripe** (Credit/Debit Cards, Apple Pay, Google Pay)
* **PayPal**
* **Razorpay**
* **Paystack**

### To Enable Paid Courses:
1. Navigate to the Desk: `http://<your-domain>/app`
2. Search in awesome bar: **Payment Gateway Account**
3. Click **New**:
   * Gateway: `Stripe`
   * Enter your Stripe Secret Key & Publishable Key.
4. Go to **LMS Settings** -> Check **Enable Payments**.
5. When creating/editing a course, check **Paid Course** and set the price (e.g., `$149.00 USD`).
6. Students will now see a seamless checkout modal when clicking "Enroll Now".

---

## 7. White-Labeling & Custom Branding

To tailor a tenant's look and feel for a university or corporate client:
1. **LMS Settings**:
   * Upload Institution Logo & Favicon.
   * Customize Banner Headings, Subheadings, and Call-to-Action buttons.
2. **Website Settings**:
   * Set brand primary color and navigation links.
3. **Custom CSS / Branding**:
   * Add custom styles under `Website Settings -> Custom CSS` to match any corporate guidelines.

---

## 8. Automated Provisioning Workflow

To provision a new client in under 60 seconds:

### On Linux VPS:
```bash
cd /opt/frappe_lms_saas
bash saas/create-tenant.sh <client-slug> [optional-custom-domain]
```
Example:
```bash
bash saas/create-tenant.sh harvard learn.harvard-prep.org
```

### On Windows Container:
```powershell
powershell -File saas\create-tenant.ps1 -TenantSlug "techacademy"
```
The script automatically creates the isolated MariaDB database, installs the apps, sets passwords, and generates a formatted credentials card in `saas/tenants/<tenant-slug>_credentials.txt`.

---

## 9. Certifications, Quizzes & Student Engagement

### Automated PDF Certificates
* Frappe LMS automatically issues digital certificates once a student completes 100% of the lessons and passes required quizzes.
* Each certificate has a unique cryptographically generated verification hash and QR code:
  `http://<your-domain>/lms/verify-certificate/<certificate-id>`
* Employers and institutions can independently verify authenticity without logging in.

### Interactive Quizzes
* Set passing percentage (e.g., 70%).
* Enable randomized question ordering to prevent cheating.
* Instant explanations displayed upon completion.

---

## 10. Day-2 Operations: Backups, Maintenance & Scaling

### Automated Backups
Run the automated multi-tenant backup utility:
```bash
bash saas/backup-tenants.sh
```
This exports full SQL dumps and uploaded media into timestamped tarballs under `saas/backups/`.

### Email (SMTP) Setup
For automated student invitations, password resets, and certificate delivery:
1. In Desk (`/app`), search for **Email Account**.
2. Set up your SMTP provider (SendGrid, Postmark, AWS SES, or Google Workspace).
3. Check **Default Outgoing** and verify connection.

---

*Engineered with precision for the next generation of online learning.*
