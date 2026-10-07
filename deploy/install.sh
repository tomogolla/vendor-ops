#!/usr/bin/env bash
# Run as root after copying the source to /opt/vendorops/app and preparing env files.
set -euo pipefail
cd /opt/vendorops/app
test -f /etc/vendorops/backend.env
test -f /etc/vendorops/frontend.env
command -v node
command -v npm
python3 --version
command -v pg_dump
id vendorops >/dev/null 2>&1 || useradd --system --home /var/lib/vendorops --shell /usr/sbin/nologin vendorops
install -d -o vendorops -g vendorops -m 0750 /var/lib/vendorops
chown root:vendorops /etc/vendorops/*.env
chmod 0640 /etc/vendorops/*.env
python3 -m venv /opt/vendorops/venv
/opt/vendorops/venv/bin/pip install -r backend/requirements.txt
cd frontend/vendorops
npm ci
npm run check
npm run build
cd /opt/vendorops/app
# Back up the actual PostgreSQL database using Django's production connection settings.
install -d -m 0700 /var/backups/vendorops
systemd-run --quiet --wait --pipe --collect --property=WorkingDirectory=/opt/vendorops/app/backend --property=EnvironmentFile=/etc/vendorops/backend.env /opt/vendorops/venv/bin/python manage.py backup_database "/var/backups/vendorops/db-$(date -u +%Y%m%dT%H%M%SZ)-$$.dump"
systemd-run --quiet --wait --pipe --collect --uid=vendorops --gid=vendorops --property=WorkingDirectory=/opt/vendorops/app/backend --property=EnvironmentFile=/etc/vendorops/backend.env /opt/vendorops/venv/bin/python manage.py migrate --noinput
systemd-run --quiet --wait --pipe --collect --property=WorkingDirectory=/opt/vendorops/app/backend --property=EnvironmentFile=/etc/vendorops/backend.env /opt/vendorops/venv/bin/python manage.py collectstatic --noinput
install -m 0644 deploy/vendorops-backend.service deploy/vendorops-frontend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable vendorops-backend vendorops-frontend
systemctl restart vendorops-backend vendorops-frontend
systemctl --no-pager status vendorops-backend vendorops-frontend
