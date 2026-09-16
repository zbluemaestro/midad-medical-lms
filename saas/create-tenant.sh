#!/usr/bin/env bash
set -e

# ==============================================================================
# Frappe LMS SaaS - Multi-Tenant Provisioning Engine
# Usage: ./create-tenant.sh <tenant_name> [custom_domain]
# Example: ./create-tenant.sh academy-pro learn.academypro.com
# ==============================================================================

if [ -z "$1" ]; then
    echo "Usage: $0 <tenant_name> [custom_domain]"
    echo "Example: $0 techacademy learn.techacademy.org"
    exit 1
fi

TENANT_SLUG="$1"
CUSTOM_DOMAIN="$2"
ROOT_DOMAIN="${ROOT_DOMAIN:-lmssaas.com}"
TENANT_SITE="${TENANT_SLUG}.${ROOT_DOMAIN}"
DB_ROOT_PASS="${DB_ROOT_PASSWORD:-admin}"
TENANT_ADMIN_PASS=$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9!@#' | head -c 16)

echo "=========================================================="
echo "    Provisioning New LMS Tenant: $TENANT_SLUG             "
echo "    Site: $TENANT_SITE                                    "
echo "=========================================================="

cd /home/frappe/frappe-bench || cd ./frappe-bench

# 1. Create isolated tenant site
echo "[1/4] Generating isolated database & site schema..."
bench new-site "$TENANT_SITE" \
    --mariadb-root-password "$DB_ROOT_PASS" \
    --admin-password "$TENANT_ADMIN_PASS" \
    --no-mariadb-socket \
    --force

# 2. Install LMS & Payments apps
echo "[2/4] Installing LMS & Payment modules..."
bench --site "$TENANT_SITE" install-app payments
bench --site "$TENANT_SITE" install-app lms

# 3. Apply custom domain if specified
if [ -n "$CUSTOM_DOMAIN" ]; then
    echo "[3/4] Binding custom domain: $CUSTOM_DOMAIN..."
    bench --site "$TENANT_SITE" add-to-hosts
    # Store custom domain mapping
    bench --site "$TENANT_SITE" set-config custom_domain "$CUSTOM_DOMAIN"
fi

# 4. Seed initial setup & configure large video upload limit (10 GB)
echo "[4/4] Finalizing tenant optimization & upload thresholds..."
bench --site "$TENANT_SITE" set-config max_file_size 10737418240
bench --site "$TENANT_SITE" set-config http_timeout 1800
bench --site "$TENANT_SITE" clear-cache

# Summary output
CREDENTIALS_FILE="/workspace/saas/tenants/${TENANT_SLUG}_credentials.txt"
mkdir -p /workspace/saas/tenants 2>/dev/null || true

cat <<EOF | tee "$CREDENTIALS_FILE" 2>/dev/null || true
===================================================================
                NEW LMS TENANT PROVISIONED
===================================================================
Tenant ID:           $TENANT_SLUG
Site Domain:         http://$TENANT_SITE:8000
Custom Domain:       ${CUSTOM_DOMAIN:-None}
Admin Username:      Administrator
Admin Password:      $TENANT_ADMIN_PASS
LMS Portal URL:      http://$TENANT_SITE:8000/lms
Desk Admin URL:      http://$TENANT_SITE:8000/app
===================================================================
EOF

echo "[+] Tenant successfully created!"
