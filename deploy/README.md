# Deploy Vendor Ops with PostgreSQL on Ubuntu 24.04

The droplet runs Nginx, Django/Gunicorn and SvelteKit as native services. PostgreSQL runs natively on **127.0.0.1:5432**. GitHub Actions uses a disposable PostgreSQL service container for tests; the droplet does not require Docker.

For automated deployment, see [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md).

**Windows PowerShell** means your local terminal. **Droplet** means an SSH terminal logged in as root (or run sudo -i first). Replace app.example.com with your actual hostname and confirm 162.243.224.95 is your droplet.

## 1. Connect and install prerequisites

Windows PowerShell:

```powershell
ssh -i "$env:USERPROFILE\.ssh\vendorops_ed25519" root@162.243.224.95
```

If SSH reports Permission denied (publickey), add the corresponding .pub public key to /root/.ssh/authorized_keys through DigitalOcean's console. Preserve existing keys; use directory mode 700 and file mode 600. Never share the private key.

Droplet:

```sh
apt update
apt install -y nginx python3-venv python3-pip postgresql postgresql-client libpq5 certbot python3-certbot-nginx curl ca-certificates gnupg nano
systemctl enable --now postgresql
pg_isready -h 127.0.0.1 -p 5432
pg_dump --version
```

Ubuntu 24.04 supplies PostgreSQL 16, matching CI. Use a pg_dump version at least as new as your server. If you installed another PostgreSQL version already, confirm versions before changing packages.

Install Node.js 24 if it is not already available:

```sh
curl -fsSL https://deb.nodesource.com/setup_24.x -o /tmp/vendorops-nodesource.sh
bash /tmp/vendorops-nodesource.sh
apt install -y nodejs
node --version
command -v node
```

The frontend service expects /usr/bin/node. Check other apps' requirements before changing an existing Node installation.

## 2. Create the production database and role

Droplet:

```sh
sudo -u postgres psql
```

In the PostgreSQL prompt, run these individually:

```sql
CREATE ROLE vendorops LOGIN;
\password vendorops
CREATE DATABASE tgf_vendor_ops OWNER vendorops;
\q
```

The password command prompts twice. Choose a strong password and record it privately for the environment file. The production role owns this database so Django can apply migrations; it does not need superuser or CREATEDB privileges. Skip CREATE commands for an existing role/database and verify ownership instead. Do not recreate or overwrite a database containing production data.

Verify a real TCP login:

```sh
psql -h 127.0.0.1 -p 5432 -U vendorops -d tgf_vendor_ops -W -c 'SELECT current_database(), current_user;'
```

Success prints tgf_vendor_ops and vendorops. PostgreSQL's default loopback listener is sufficient. Keep port 5432 private; do not add a public firewall rule. If local password authentication is customized, configure pg_hba.conf for the vendorops role/database on 127.0.0.1/32 using scram-sha-256.

## 3. Upload source

Droplet:

```sh
mkdir -p /opt/vendorops/app
```

Windows PowerShell:

```powershell
Set-Location "C:\Users\thoma\OneDrive\Desktop\projects\vendor-ops"
tar -czf "$env:TEMP\vendorops-source.tar.gz" --exclude=.env --exclude='.env.*' --exclude=.venv --exclude=venv --exclude=node_modules --exclude=build --exclude=.svelte-kit --exclude=__pycache__ --exclude='*.sqlite3*' --exclude=staticfiles --exclude=media backend frontend/vendorops deploy
scp -i "$env:USERPROFILE\.ssh\vendorops_ed25519" "$env:TEMP\vendorops-source.tar.gz" root@162.243.224.95:/tmp/vendorops-source.tar.gz
```

Droplet:

```sh
tar -xzf /tmp/vendorops-source.tar.gz -C /opt/vendorops/app
sed -i 's/\r$//' /opt/vendorops/app/deploy/install.sh /opt/vendorops/app/deploy/ci-deploy.sh
```

## 4. Configure environment files

For initial setup only, on the droplet:

```sh
install -d -m 0750 /etc/vendorops
cp /opt/vendorops/app/deploy/backend.env.example /etc/vendorops/backend.env
cp /opt/vendorops/app/deploy/frontend.env.example /etc/vendorops/frontend.env
chmod 600 /etc/vendorops/*.env
python3 -c 'import secrets; print(secrets.token_urlsafe(64))'
nano /etc/vendorops/backend.env
```

For an existing deployment, edit the existing files instead of copying templates over them. Keep your existing SECRET_KEY and SMTP settings. Remove obsolete DATABASE_PATH and add:

```dotenv
DB_NAME=tgf_vendor_ops
DB_USER=vendorops
DB_PASSWORD="YOUR_POSTGRESQL_PASSWORD"
DB_HOST=127.0.0.1
DB_PORT=5432
```

Use your actual database/role names if different. These are systemd environment files: quote special values appropriately; do not use shell variable substitutions. Do not commit the files. Keep DEBUG=false, a random SECRET_KEY of at least 50 characters, your public hostname in ALLOWED_HOSTS, and its HTTPS URL in CSRF_TRUSTED_ORIGINS.

Edit frontend.env:

```dotenv
NODE_ENV=production
HOST=127.0.0.1
PORT=3000
ORIGIN=https://app.example.com
DJANGO_API_URL=http://127.0.0.1:8000
```

In nano, Ctrl+O then Enter saves; Ctrl+X exits.

## 5. Migrate, build and start

Droplet:

```sh
bash /opt/vendorops/app/deploy/install.sh
```

The installer installs dependencies, checks/builds the frontend, backs up PostgreSQL, runs Django migrate --noinput with production credentials, collects static files, and starts systemd services. Backup/migration/build failures stop deployment. Even on first deployment, create the empty database first so the backup and migrations can connect.

Unit/integration tests run against GitHub's disposable PostgreSQL service before deployment. They do not run against the production database. The CI role can create Django's test database; the production role need not.

Verify:

```sh
systemctl is-active vendorops-backend vendorops-frontend
curl -I http://127.0.0.1:3000/login
```

## 6. Nginx, DNS and HTTPS

Point your domain's A record to the droplet. Correct any AAAA record. If using Cloudflare, start with DNS only. On Windows, Resolve-DnsName app.example.com -Type A should return the droplet IP.

For initial Nginx setup, on the droplet:

```sh
cp /opt/vendorops/app/deploy/nginx.conf /etc/nginx/sites-available/vendorops
nano /etc/nginx/sites-available/vendorops
```

Replace server_name app.example.com with your domain. Preserve other sites and resolve duplicate hostnames. Then:

```sh
ln -s /etc/nginx/sites-available/vendorops /etc/nginx/sites-enabled/vendorops
nginx -t
systemctl reload nginx
certbot --nginx -d app.example.com --redirect
certbot renew --dry-run
```

Skip the link command if it exists. Do not reload invalid Nginx configuration. For an existing HTTPS deployment, preserve the active Certbot-managed config instead of copying the template again.

Allow inbound 80/443 and preserve SSH access in UFW/DigitalOcean firewalls. Leave 3000, 8000 and 5432 private. Production login cookies require HTTPS.

## 7. Create an administrator

Droplet:

```sh
systemd-run --pty --wait --collect --uid=vendorops --gid=vendorops \
  --property=WorkingDirectory=/opt/vendorops/app/backend \
  --property=EnvironmentFile=/etc/vendorops/backend.env \
  /opt/vendorops/venv/bin/python manage.py createsuperuser
```

Sign in at https://app.example.com/login and test a vendor page and form submission.

## Existing SQLite data

Changing DB settings does not transfer SQLite records into PostgreSQL. Preserve a copy of the old database. Plan a controlled export/import with matching code versions, paused writes, and verified record counts/relationships. Do not copy a .sqlite3 file into PostgreSQL or assume migrate imports existing data. Resolve the data migration before switching a live app with SQLite data.

## Backups and recovery

The installer and CI deployment now produce custom-format .dump files from the database in Django's settings. Passwords are passed to pg_dump through its environment, not command arguments. A failed backup stops deployment; existing backup files are never overwritten.

For a manual backup, on the droplet:

```sh
install -d -m 0700 /var/backups/vendorops
systemd-run --quiet --wait --pipe --collect \
  --property=WorkingDirectory=/opt/vendorops/app/backend \
  --property=EnvironmentFile=/etc/vendorops/backend.env \
  /opt/vendorops/venv/bin/python manage.py backup_database "/var/backups/vendorops/manual-$(date -u +%Y%m%dT%H%M%SZ).dump"
```

For daily backups, place the following in /etc/cron.daily/vendorops-backup and chmod 700 that file:

```sh
#!/bin/sh
set -eu
umask 077
systemd-run --quiet --wait --pipe --collect --property=WorkingDirectory=/opt/vendorops/app/backend --property=EnvironmentFile=/etc/vendorops/backend.env /opt/vendorops/venv/bin/python manage.py backup_database "/var/backups/vendorops/daily-$(date -u +%Y%m%dT%H%M%SZ).dump"
```

Run it once manually to verify. Copy backups off the droplet using scp, monitor disk space, and periodically test recovery into a separate database. pg_dump stores database contents/schema, not cluster roles; provision the destination role separately.

To test restoration into a new, empty recovery database owned by vendorops:

```sh
sudo -u postgres createdb --owner=vendorops vendorops_recovery
pg_restore -h 127.0.0.1 -p 5432 -U vendorops -W --no-owner --no-acl --exit-on-error -d vendorops_recovery /var/backups/vendorops/YOUR_BACKUP.dump
```

Replace the filename. This does not modify the live database. For a real rollback, stop application writes and restore a matching database/source version; do not automatically restore old data after failed migrations.

## Updates and troubleshooting

Use GitHub Actions as described in GITHUB_ACTIONS.md. Manual updates require backing up source/data, stopping services, uploading updated source and rerunning install.sh. Preserve production environment files and Nginx configuration.

```sh
journalctl -u vendorops-backend -u vendorops-frontend -n 100 --no-pager
pg_isready -h 127.0.0.1 -p 5432
systemctl status postgresql --no-pager
```

Connection refused: check PostgreSQL and its loopback listener. Authentication failed: check role/password and pg_hba.conf. Migration permission denied: verify database/schema ownership. pg_dump missing: install postgresql-client matching the server. Deployment stops before restart if an existing application check/test fails; inspect that failure separately.

References: [GitHub PostgreSQL services](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers), [PostgreSQL pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html).
