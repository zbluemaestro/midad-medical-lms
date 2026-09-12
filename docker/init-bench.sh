#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "    Frappe LMS SaaS Engine - Automated Container Setup   "
echo "=========================================================="

SITE="${SITE_NAME:-lms.localhost}"
DB_PASS="${DB_ROOT_PASSWORD:-admin}"
ADMIN_PASS="${ADMIN_PASSWORD:-admin}"
BRANCH="${FRAPPE_BRANCH:-version-15}"

if [ -d "/home/frappe/frappe-bench/apps/frappe" ]; then
    echo "[+] Existing Frappe Bench detected. Skipping initial build..."
    cd /home/frappe/frappe-bench
    bench --site "$SITE" migrate || true
    bench --site "$SITE" clear-cache || true
    bench use "$SITE"
    echo "[+] Starting Frappe LMS services..."
    exec bench start
fi

echo "[1/6] Initializing Frappe Bench (branch: $BRANCH)..."
export PATH="${NVM_DIR}/versions/node/v${NODE_VERSION_DEVELOP:-18}/bin/:${PATH}"

cd /home/frappe
bench init --skip-redis-config-generation --frappe-branch "$BRANCH" frappe-bench

cd /home/frappe/frappe-bench

echo "[2/6] Configuring DB and Redis container endpoints..."
bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

# Remove redis & watch from local Procfile as they are containerized
sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile

echo "[3/6] Fetching required Frappe apps (payments & lms)..."
bench get-app payments || echo "Payments already fetched or using fallback"
bench get-app lms --branch develop

echo "[4/6] Creating primary site: $SITE..."
bench new-site "$SITE" \
    --force \
    --mariadb-root-password "$DB_PASS" \
    --admin-password "$ADMIN_PASS" \
    --no-mariadb-socket

echo "[5/6] Installing apps onto $SITE..."
bench --site "$SITE" install-app payments
bench --site "$SITE" install-app lms
bench --site "$SITE" set-config developer_mode 1
# Configure 10 GB Upload Limit for Medical Video Lectures
bench --site "$SITE" set-config max_file_size 10737418240
bench --site "$SITE" clear-cache
bench use "$SITE"

echo "[6/6] Seeding Midad Medical Curriculum & Content Security..."
if [ -f "/workspace/seeder/seed_midad_medical.py" ]; then
    cp /workspace/seeder/seed_midad_medical.py ./
    bench --site "$SITE" execute seed_midad_medical.seed_midad_curriculum || {
        echo "[!] Primary medical seeder encountered exception, running fallback showcase seeder."
        bench --site "$SITE" execute seed_saas_showcase.seed_showcase || true
    }
elif [ -f "/workspace/seeder/seed_saas_showcase.py" ]; then
    cp /workspace/seeder/seed_saas_showcase.py ./
    bench --site "$SITE" execute seed_saas_showcase.seed_showcase || true
fi

echo "=========================================================="
echo " Frappe LMS is ready! Serving at http://localhost:8000/lms"
echo " Administrator Login: Administrator / $ADMIN_PASS"
echo "=========================================================="

exec bench start
