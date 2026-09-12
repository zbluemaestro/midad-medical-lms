#!/usr/bin/env bash
# Lists all active sites/tenants on the Frappe Bench
cd /home/frappe/frappe-bench 2>/dev/null || cd ./frappe-bench 2>/dev/null

echo "=========================================================="
echo "          ACTIVE FRAPPE LMS SAAS TENANTS                  "
echo "=========================================================="
find sites -maxdepth 1 -mindepth 1 -type d ! -name "assets" ! -name ".*" -exec basename {} \;
