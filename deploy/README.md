# Deploy Vendor Ops to Ubuntu 24.04

Already deployed? Follow [the GitHub CI/CD setup guide](GITHUB_ACTIONS.md) to automate checks and deployments.

Follow these steps in order. If a command fails, stop and save the error before continuing. This uses Nginx and systemd without Docker.

## Before you start

**Windows PowerShell** means a terminal on your computer. **Droplet** means the Ubuntu terminal after connecting with SSH. Droplet commands assume you are root; if using another administrator account, run sudo -i first.

Replace **ops.yourdomain.com** everywhere with your actual domain. Confirm **162.243.224.95** is the intended droplet in DigitalOcean. Keep the SSH terminal open and use a second Windows terminal for uploads.

The main steps create a fresh database. The optional import section copies existing data.

Nginx receives HTTPS requests and forwards app traffic to SvelteKit on localhost port 3000. SvelteKit calls Django on localhost port 8000. Systemd starts both services after reboot and restarts them after crashes. The database lives outside the source folder.

## 1. Connect to the droplet

**Windows PowerShell:**

~~~powershell
ssh root@162.243.224.95
~~~

Verify the server fingerprint through a trusted source, such as the droplet console, before accepting a first connection. Success means you see an Ubuntu prompt like root@your-droplet:~#.

Our earlier attempt returned Permission denied (publickey). If that happens, specify your existing private key:

~~~powershell
ssh -i "$env:USERPROFILE\.ssh\id_ed25519" root@162.243.224.95
~~~

Use your actual key path. If you have no key, create one at a new filename. Do not overwrite an existing key:

~~~powershell
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\vendorops_ed25519"
Get-Content "$env:USERPROFILE\.ssh\vendorops_ed25519.pub"
~~~

Copy the entire public-key line. Open the droplet's browser console in DigitalOcean, log in as root, and run:

~~~sh
mkdir -p /root/.ssh
chmod 700 /root/.ssh
nano /root/.ssh/authorized_keys
~~~

Paste the public key on a new line, preserving existing keys. In nano, save with **Ctrl+O**, **Enter**, then exit with **Ctrl+X**.

~~~sh
chmod 600 /root/.ssh/authorized_keys
~~~

Retry on Windows:

~~~powershell
ssh -i "$env:USERPROFILE\.ssh\vendorops_ed25519" root@162.243.224.95
~~~

Adding a key to your DigitalOcean account alone does not install it on an existing droplet. Never share the private key. If SSH needs the -i option, add the same option to each scp command below.

## 2. Point your domain to the droplet

At your domain's DNS provider, create:

| Field | Value |
| --- | --- |
| Type | A |
| Name / Host | ops for ops.yourdomain.com |
| Value / Target | 162.243.224.95 |
| TTL | Default |

For a root domain, the name is usually @. Remove an incorrect AAAA record for this hostname, or configure the droplet's actual IPv6 address. For Cloudflare, use **DNS only** during initial setup.

**Windows PowerShell:**

~~~powershell
Resolve-DnsName ops.yourdomain.com -Type A
~~~

Success: the answer contains your droplet IP. DNS changes may take time. Public DNS must be correct before HTTPS setup.

## 3. Install server software

**Droplet:**

~~~sh
apt update
apt install -y nginx python3-venv python3-pip sqlite3 certbot python3-certbot-nginx curl ca-certificates gnupg nano
~~~

Install Node.js 24 from NodeSource. If other apps already run on this server, check their Node requirements before changing the installed version.

~~~sh
curl -fsSL https://deb.nodesource.com/setup_24.x -o /tmp/vendorops-nodesource.sh
bash /tmp/vendorops-nodesource.sh
apt install -y nodejs
node --version
npm --version
python3 --version
command -v node
~~~

Success: Node prints v24..., standard Ubuntu 24.04 Python prints 3.12..., and Node is at /usr/bin/node. The service expects that path. Ubuntu's older default Node package is insufficient for this frontend.

## 4. Upload your app

**Droplet:**

~~~sh
mkdir -p /opt/vendorops/app
~~~

**Windows PowerShell, in a second terminal:**

~~~powershell
Set-Location "C:\Users\thoma\OneDrive\Desktop\projects\vendor-ops"
tar -czf "$env:TEMP\vendorops-source.tar.gz" --exclude=.env --exclude='.env.*' --exclude=.venv --exclude=venv --exclude=node_modules --exclude=build --exclude=.svelte-kit --exclude=__pycache__ --exclude='*.sqlite3*' --exclude=staticfiles --exclude=media backend frontend/vendorops deploy
scp "$env:TEMP\vendorops-source.tar.gz" root@162.243.224.95:/tmp/vendorops-source.tar.gz
~~~

This uploads your current source, including uncommitted changes, excluding secrets, databases, and generated files.

**Droplet:**

~~~sh
tar -xzf /tmp/vendorops-source.tar.gz -C /opt/vendorops/app
ls /opt/vendorops/app
sed -i 's/\r$//' /opt/vendorops/app/deploy/install.sh
~~~

Success: you see backend, frontend, and deploy. The last command removes Windows line endings from the script.

## 5. Create production settings

**Droplet:**

~~~sh
install -d -m 0750 /etc/vendorops
cp /opt/vendorops/app/deploy/backend.env.example /etc/vendorops/backend.env
cp /opt/vendorops/app/deploy/frontend.env.example /etc/vendorops/frontend.env
chmod 600 /etc/vendorops/backend.env /etc/vendorops/frontend.env
python3 -c 'import secrets; print(secrets.token_urlsafe(64))'
~~~

Copy the random text Python prints. This is your secret key. Keep it private and retain it for future deployments.

~~~sh
nano /etc/vendorops/backend.env
~~~

Edit these lines using your generated key and actual domain:

~~~dotenv
SECRET_KEY=PASTE_YOUR_GENERATED_SECRET_HERE
DEBUG=false
ALLOWED_HOSTS=127.0.0.1,localhost,ops.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://ops.yourdomain.com
DATABASE_PATH=/var/lib/vendorops/db.sqlite3
TRUST_PROXY=true
SECURE_SSL_REDIRECT=false
~~~

Keep the SMTP lines. For email delivery, fill in your email provider's host, username, password, sender, port and TLS settings. With an empty SMTP host, email sending is unavailable. Quote values containing spaces. Do not commit these files or share passwords in chat.

Save with **Ctrl+O**, **Enter**, then **Ctrl+X**.

~~~sh
nano /etc/vendorops/frontend.env
~~~

Use:

~~~dotenv
NODE_ENV=production
HOST=127.0.0.1
PORT=3000
ORIGIN=https://ops.yourdomain.com
DJANGO_API_URL=http://127.0.0.1:8000
~~~

Use your real HTTPS hostname for ORIGIN, without a trailing slash. Keep the internal API URL as shown. Save and exit.

## 6. Build and start the app

**Droplet:**

~~~sh
bash /opt/vendorops/app/deploy/install.sh
~~~

This may take several minutes. It installs dependencies, checks and builds the frontend, creates database tables, collects static files, and starts services. Later runs back up the existing production database before migrations.

Success: both services show active (running). Check:

~~~sh
systemctl is-active vendorops-backend vendorops-frontend
curl -I http://127.0.0.1:3000/login
~~~

Expect two active lines and an HTTP response from the login page. If pip cannot find a pinned package version, stop and have the requirements checked against available releases. Resolve any frontend check/build errors before proceeding.

## 7. Configure Nginx

**Droplet:**

~~~sh
ls -l /etc/nginx/sites-enabled
cp /opt/vendorops/app/deploy/nginx.conf /etc/nginx/sites-available/vendorops
nano /etc/nginx/sites-available/vendorops
~~~

Change the server_name line to your real domain:

~~~nginx
server_name ops.yourdomain.com;
~~~

Save and exit, then:

~~~sh
ln -s /etc/nginx/sites-available/vendorops /etc/nginx/sites-enabled/vendorops
nginx -t
systemctl reload nginx
~~~

Skip ln if the link already exists. Resolve another enabled site using the same hostname first. The default Ubuntu site can coexist with this named site.

Success: Nginx says syntax OK and configuration test successful. Do not reload a failing configuration.

## 8. Check firewalls

**Droplet:**

~~~sh
ufw status
~~~

If UFW is active:

~~~sh
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw status
~~~

If inactive, these commands can prepare rules, but this guide does not enable it automatically. Preserve rules needed by other services. Always allow SSH before enabling a firewall.

If a DigitalOcean Cloud Firewall is attached, allow inbound TCP **80** and **443** from the internet, and **22** from your own IP for SSH. Keep ports **3000** and **8000** private.

Open http://ops.yourdomain.com/login. You should see the page. Wait for HTTPS before signing in: production cookies require HTTPS.

## 9. Enable HTTPS

**Droplet:**

~~~sh
certbot --nginx -d ops.yourdomain.com --redirect
~~~

Enter an email for certificate notices and accept the terms when prompted. Certbot installs the certificate and configures HTTP to redirect to HTTPS.

~~~sh
nginx -t
curl -I https://ops.yourdomain.com/login
certbot renew --dry-run
~~~

Success: HTTPS works, your browser shows a secure connection, and renewal testing succeeds. If issuance fails, check public DNS, any AAAA record, and inbound ports 80/443.

## 10. Create your login account

**Droplet:**

~~~sh
systemd-run --pty --wait --collect --uid=vendorops --gid=vendorops \
  --property=WorkingDirectory=/opt/vendorops/app/backend \
  --property=EnvironmentFile=/etc/vendorops/backend.env \
  /opt/vendorops/venv/bin/python manage.py createsuperuser
~~~

Enter your username, email, and password. Password characters do not appear while typing; this is normal.

Sign in at https://ops.yourdomain.com/login. Django admin is at https://ops.yourdomain.com/admin/. Check a vendor page, create a test record, and submit a form. If SMTP is configured, test an email action with an address you control.

## Optional: import your local data

Skip this for an empty database. Importing replaces server data and includes existing accounts. Do it before people start using the deployed app.

Stop local Django. **Windows PowerShell, from the project root:**

~~~powershell
@'
import sqlite3
source = sqlite3.connect('backend/db.sqlite3')
destination = sqlite3.connect('backend/db-upload.sqlite3')
source.backup(destination)
destination.close()
source.close()
'@ | .\backend\.venv\Scripts\python.exe -
scp .\backend\db-upload.sqlite3 root@162.243.224.95:/root/vendorops-db-upload.sqlite3
~~~

Adjust the Python path if your virtual environment is elsewhere. This file contains private data.

**Droplet, after initial deployment:**

~~~sh
systemctl stop vendorops-frontend vendorops-backend
install -d -m 0700 /var/backups/vendorops
sqlite3 /var/lib/vendorops/db.sqlite3 ".backup '/var/backups/vendorops/before-import-$(date -u +%Y%m%dT%H%M%SZ).sqlite3'"
sqlite3 /var/lib/vendorops/db.sqlite3 'PRAGMA wal_checkpoint(TRUNCATE);'
install -o vendorops -g vendorops -m 0640 /root/vendorops-db-upload.sqlite3 /var/lib/vendorops/db.sqlite3
bash /opt/vendorops/app/deploy/install.sh
~~~

Stop if any command fails, before replacing data. Keep services stopped during import. The installer applies missing migrations and starts services again. Sign in using an existing local account.

## Deploy future changes

This causes brief downtime. Take a DigitalOcean snapshot before updating if you need a full recovery point.

**Droplet:**

~~~sh
systemctl stop vendorops-frontend vendorops-backend
install -d -m 0700 /var/backups/vendorops
sqlite3 /var/lib/vendorops/db.sqlite3 ".backup '/var/backups/vendorops/before-update-$(date -u +%Y%m%dT%H%M%SZ).sqlite3'"
tar -czf "/var/backups/vendorops/source-$(date -u +%Y%m%dT%H%M%SZ).tar.gz" -C /opt/vendorops app
~~~

Repeat **step 4** to upload and extract updated source, then:

~~~sh
bash /opt/vendorops/app/deploy/install.sh
curl -I https://ops.yourdomain.com/login
~~~

Do not repeat step 5: it overwrites settings. Do not overwrite the active Nginx config with the template after Certbot adds HTTPS. Extraction overwrites matching files but does not remove deleted files; review and remove specific obsolete files when an update requires it.

If an update fails, services may remain stopped. Inspect the error. Restoring old code alone may not undo migrations; rollback can require the matching database backup.

## Daily database backups

The installer backs up only before migrations. To add daily backups, **on the droplet**:

~~~sh
install -d -m 0700 /var/backups/vendorops
nano /etc/cron.daily/vendorops-backup
~~~

Paste:

~~~sh
#!/bin/sh
set -eu
umask 077
sqlite3 /var/lib/vendorops/db.sqlite3 ".backup '/var/backups/vendorops/daily-$(date -u +%Y%m%dT%H%M%SZ).sqlite3'"
~~~

Save, exit, and test:

~~~sh
chmod 700 /etc/cron.daily/vendorops-backup
/etc/cron.daily/vendorops-backup
ls -lh /var/backups/vendorops
~~~

Copy backups off the droplet regularly. **Windows PowerShell:**

~~~powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\Documents\vendorops-backups"
scp root@162.243.224.95:/var/backups/vendorops/EXACT_BACKUP_FILENAME.sqlite3 "$env:USERPROFILE\Documents\vendorops-backups\"
~~~

Use an exact filename from ls. Backups contain private data. This example keeps backups until you remove old ones: monitor space with df -h. Periodically restore a backup into a separate test environment to verify it.

## Troubleshooting

**Droplet — service status and logs:**

~~~sh
systemctl status vendorops-backend vendorops-frontend --no-pager
journalctl -u vendorops-backend -u vendorops-frontend -n 100 --no-pager
tail -n 50 /var/log/nginx/error.log
~~~

| Problem | Check |
| --- | --- |
| SSH publickey error | Correct user, key path, and public key in authorized_keys |
| 502 Bad Gateway | Service status/logs; try curl -I http://127.0.0.1:3000/login |
| Nginx welcome page | DNS, server_name and enabled-site link; visit domain rather than IP |
| Login or form origin error | HTTPS; frontend ORIGIN matches browser URL; backend hosts and trusted origins match |
| Certificate failure | Public DNS, incorrect AAAA record, inbound ports 80/443 |
| Email failure | SMTP credentials, verified sender, logs, DigitalOcean outbound SMTP restrictions |

After editing environment settings:

~~~sh
systemctl restart vendorops-backend vendorops-frontend
~~~

| Path | Purpose |
| --- | --- |
| /opt/vendorops/app | Source and build |
| /opt/vendorops/venv | Python dependencies |
| /etc/vendorops/backend.env | Backend settings and SMTP secrets |
| /etc/vendorops/frontend.env | Site URL and internal API URL |
| /var/lib/vendorops/db.sqlite3 | Production database |
| /var/backups/vendorops | Backups |
| /etc/nginx/sites-available/vendorops | Active Nginx configuration |

## References

- [NodeSource installation documentation](https://github.com/nodesource/distributions/blob/master/DEV_README.md)
- [SvelteKit Node adapter settings](https://svelte.dev/docs/kit/adapter-node)
- [Certbot documentation](https://eff-certbot.readthedocs.io/en/stable/using.html)
