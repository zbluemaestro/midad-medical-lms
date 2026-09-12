#!/usr/bin/env bash
set -e

# ==============================================================================
# Frappe LMS SaaS - Automated Ubuntu/Debian Cloud VPS Deployment Script
# Supports: Ubuntu 22.04 LTS, Ubuntu 24.04 LTS, Debian 12
# ==============================================================================

echo "=========================================================="
echo "    Deploying Frappe LMS SaaS on Cloud VPS                "
echo "=========================================================="

if [ "$EUID" -ne 0 ]; then
    echo "[-] Please run this deployment script as root or with sudo."
    exit 1
fi

PRIMARY_DOMAIN="${1}"
if [ -z "$PRIMARY_DOMAIN" ]; then
    read -p "Enter your Primary LMS SaaS Domain (e.g. lms.yourdomain.com): " PRIMARY_DOMAIN
fi

if [ -z "$PRIMARY_DOMAIN" ]; then
    echo "[-] Domain is required. Exiting."
    exit 1
fi

echo "[1/6] Updating system packages..."
apt-get update -y && apt-get upgrade -y
apt-get install -y curl wget git ufw apt-transport-https ca-certificates gnupg lsb-release

echo "[2/6] Configuring Security Firewall (UFW)..."
ufw allow 22/tcp || true
ufw allow 80/tcp || true
ufw allow 443/tcp || true
ufw --force enable || true

echo "[3/6] Installing Docker & Docker Compose Plugin..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | bash
    systemctl enable docker
    systemctl start docker
fi

echo "[4/6] Generating Strong SaaS Production Credentials..."
DB_PASSWORD=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9!@#%^&*')
ADMIN_PASSWORD=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9!@#%^&*')

cat <<EOF > /opt/frappe-lms-saas.env
DB_ROOT_PASSWORD=${DB_PASSWORD}
ADMIN_PASSWORD=${ADMIN_PASSWORD}
PRIMARY_DOMAIN=${PRIMARY_DOMAIN}
EOF
chmod 600 /opt/frappe-lms-saas.env

echo "[5/6] Launching Production Multi-Container Cluster..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

docker compose -f docker-compose.prod.yml --env-file /opt/frappe-lms-saas.env up -d

echo "[6/6] Registering Systemd Auto-Recovery Service..."
cat <<EOF > /etc/systemd/system/frappe-lms-saas.service
[Unit]
Description=Frappe LMS SaaS Engine
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml --env-file /opt/frappe-lms-saas.env up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml --env-file /opt/frappe-lms-saas.env down

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable frappe-lms-saas.service

echo "=========================================================="
echo "    FRAPPE LMS SAAS CLOUD DEPLOYMENT INITIALIZED!         "
echo "=========================================================="
echo "Domain:          http://${PRIMARY_DOMAIN}"
echo "LMS Portal:      http://${PRIMARY_DOMAIN}/lms"
echo "Desk Login:      http://${PRIMARY_DOMAIN}/app"
echo "Admin User:      Administrator"
echo "Admin Password:  ${ADMIN_PASSWORD}"
echo "Credentials are saved securely at: /opt/frappe-lms-saas.env"
echo "=========================================================="
