# Frappe LMS SaaS Engine 🚀

A complete, production-ready, multi-tenant Learning Management System (LMS) SaaS suite based on **Frappe Learning** ([frappe.io/learning](https://frappe.io/learning)) and Frappe Framework v15.

Designed for launching an independent LMS business, hosting multi-tenant academies, or offering private corporate learning portals.

---

## 📂 Repository Structure

```
frappe_lms_saas/
├── docker/                      # Multi-Container Development & Staging Stack
│   ├── docker-compose.yml       # MariaDB 10.8, Redis 7, Frappe Bench v15, LMS, Payments
│   ├── init-bench.sh            # Automated container initialization & app installer
│   └── .env.example             # Environment template for local deployment
│
├── saas/                        # Multi-Tenant SaaS Engine
│   ├── create-tenant.sh         # Linux 1-click tenant provisioning script
│   ├── create-tenant.ps1        # Windows Docker tenant provisioner
│   ├── list-tenants.sh          # List all active tenant databases and domains
│   └── backup-tenants.sh        # Automated backup for all tenant databases & media
│
├── cloud/                       # Production Linux Cloud VPS Deployment
│   ├── deploy-vps.sh            # 1-command automated deployment for Ubuntu 22.04/24.04
│   ├── docker-compose.prod.yml  # Production compose with Nginx, SSL, auto-restart
│   └── nginx.conf               # High-performance Nginx with Gzip & WebSockets
│
├── windows/                     # Windows 11 Tools
│   ├── setup-windows.ps1        # Docker environment verifier & stack launcher
│   └── share-tunnel.ps1         # Instant public HTTPS sharing via Cloudflare Tunnel
│
├── seeder/                      # Rich Showcase Demo Content
│   └── seed_saas_showcase.py    # Populates courses, video lessons, quizzes, certificates
│
├── tests/                       # Automated Verification Suite
│   └── test_saas_configs.py     # Unit tests verifying stack configs & script integrity
│
├── SAAS_FOUNDER_GUIDE.md        # Complete business, hosting, monetization & operations manual
└── README.md                    # This document
```

---

## ⚡ Quick Start: 2 Ways to Launch

### Option 1: Live Cloud VPS (Recommended for Production & Commercial SaaS)
On a fresh Ubuntu 22.04 or 24.04 LTS server (Hetzner, DigitalOcean, AWS, Linode):
```bash
git clone <this-repo> /opt/frappe_lms_saas
cd /opt/frappe_lms_saas
sudo bash cloud/deploy-vps.sh lms.yourdomain.com
```

### Option 2: Local Windows 11 + Instant Public Tunnel (Free Demo for Friends/Investors)
1. Launch the local container cluster:
   ```powershell
   powershell -File windows\setup-windows.ps1
   ```
2. Generate an instant secure public HTTPS link to share with your friend:
   ```powershell
   powershell -File windows\share-tunnel.ps1
   ```

---

## 📖 Comprehensive Founder Guide
For in-depth instructions on multi-tenancy, Stripe payment gateway configuration, white-labeling, certificate issuance, and business models, see [SAAS_FOUNDER_GUIDE.md](./SAAS_FOUNDER_GUIDE.md).
