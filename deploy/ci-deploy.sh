#!/usr/bin/env bash
# Invoked by GitHub over SSH as root. Existing env, Nginx and database stay in place.
set -euo pipefail
release_sha=${1:?Expected commit SHA}
[[ "$release_sha" =~ ^[0-9a-f]{40}$ ]] || exit 1
[[ $(id -u) == 0 ]] || { echo 'Run as root'; exit 1; }
exec 9>/run/lock/vendorops-deploy.lock
flock -n 9 || { echo 'Another deployment is running'; exit 1; }
incoming="/opt/vendorops/incoming/$release_sha"
test -f "$incoming/backend/manage.py"
test -f "$incoming/frontend/vendorops/package-lock.json"
test -f "$incoming/deploy/install.sh"
test -d /opt/vendorops/app
test -f /etc/vendorops/backend.env
test -f /etc/vendorops/frontend.env
test -f /var/lib/vendorops/db.sqlite3
backup_dir="/var/backups/vendorops/$(date -u +%Y%m%dT%H%M%SZ)-$release_sha"
install -d -m 0700 "$backup_dir"
# Save source before stopping services, then take a consistent data backup.
tar -czf "$backup_dir/source.tar.gz" -C /opt/vendorops app
systemctl stop vendorops-frontend vendorops-backend
trap 'echo "Deployment failed. Services may be stopped. Inspect logs and backups at: $backup_dir. Do not restore old code without checking migrations." >&2' ERR
sqlite3 /var/lib/vendorops/db.sqlite3 ".backup '$backup_dir/db.sqlite3'"
# Preserve the previous tree rather than overwriting it. This removes stale source files.
mv /opt/vendorops/app "$backup_dir/previous-app"
mv "$incoming" /opt/vendorops/app
chmod -R a+rX /opt/vendorops/app
bash /opt/vendorops/app/deploy/install.sh
systemctl is-active --quiet vendorops-backend vendorops-frontend
curl --fail --silent --show-error --retry 6 --retry-delay 5 --retry-all-errors --max-time 15 http://127.0.0.1:3000/login --output /dev/null
# Authentication is expected to reject an anonymous request; verifies Django responds.
api_status=$(curl --silent --show-error --max-time 15 --output /dev/null --write-out '%{http_code}' http://127.0.0.1:8000/api/auth/me/)
[[ "$api_status" == 401 || "$api_status" == 403 ]]
trap - ERR
echo "Deployed $release_sha. Backup: $backup_dir"
