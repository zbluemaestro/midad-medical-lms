#!/usr/bin/env bash
set -e

# Backs up all sites with files and databases
cd /home/frappe/frappe-bench 2>/dev/null || cd ./frappe-bench 2>/dev/null

BACKUP_DIR="/workspace/saas/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "=========================================================="
echo "    Backing up all LMS Tenants to $BACKUP_DIR...          "
echo "=========================================================="

for site in $(find sites -maxdepth 1 -mindepth 1 -type d ! -name "assets" ! -name ".*" -exec basename {} \;); do
    echo "[*] Backing up tenant site: $site..."
    bench --site "$site" backup --with-files
    cp -r "sites/$site/private/backups/"* "$BACKUP_DIR/" 2>/dev/null || true
done

echo "[+] All tenant backups archived successfully at $BACKUP_DIR"
