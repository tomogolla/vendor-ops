# Set up GitHub CI/CD for your existing droplet

The workflow is in `.github/workflows/ci-cd.yml`. It starts a PostgreSQL 16 service container for CI, waits for its health check, connects Django to 127.0.0.1:5432, checks migration consistency, applies migrations, runs unit/integration tests, and checks/builds SvelteKit. The CI database and credentials are disposable; they do not connect to your droplet. Pull requests only run checks. Successful pushes to **master** deploy once you enable deployment. You can also run it manually from GitHub's Actions tab on master.

This matches the existing Nginx/systemd setup in [README.md](README.md). It assumes the app, database and environment files are at the paths in that guide, and SSH uses port 22. Confirm these paths on your running droplet before enabling it. Nginx, certificates and environment settings are preserved. Updates have downtime while dependencies install and the frontend builds.

## 1. Create a separate GitHub deployment key

**Windows PowerShell:**

```powershell
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\vendorops_github" -C "vendorops-github-actions"
```

Use an empty passphrase for this automation key: press Enter at both passphrase prompts. Do not overwrite an existing file. Keep your normal login key separate.

```powershell
Get-Content "$env:USERPROFILE\.ssh\vendorops_github.pub"
```

Copy the entire public-key line. Connect to your droplet using your normal working SSH login.

**Droplet, as root:**

```sh
nano /root/.ssh/authorized_keys
```

Append the new public key on its own line, preserving your existing keys. Prefix this new line with `restrict `, so it looks like:

```text
restrict ssh-ed25519 AAAA... vendorops-github-actions
```

The actual key must contain the full text, not `AAAA...`. Save with Ctrl+O, Enter, Ctrl+X.

```sh
chmod 700 /root/.ssh
chmod 600 /root/.ssh/authorized_keys
```

This key allows production deployment as root, including running application installation code. The restrict option disables forwarding and interactive terminal allocation; it still allows commands and file transfers. Anyone who controls this key or the deployment workflow can change the server. Protect repository write access and the production environment accordingly.

**Windows PowerShell — verify the new key:**

```powershell
ssh -o IdentitiesOnly=yes -i "$env:USERPROFILE\.ssh\vendorops_github" root@162.243.224.95 "whoami"
```

Success: `root` is printed without a password prompt.

## 2. Record the droplet's SSH identity

This lets GitHub verify it is connecting to your server.

**Droplet, through your trusted existing SSH session or DigitalOcean console:**

```sh
cat /etc/ssh/ssh_host_ed25519_key.pub
```

This is a public host key, not your login key. Copy the first two fields and put the droplet IP before them. The resulting single line should look like:

```text
162.243.224.95 ssh-ed25519 AAAAC3...FULL_HOST_KEY_HERE
```

Use the full key. Save this line for the DEPLOY_KNOWN_HOSTS secret below. Do not use an unverified ssh-keyscan result as the source of trust.

## 3. Add the GitHub secrets and variables

Open [your repository](https://github.com/tomogolla/vendor-ops), then **Settings → Environments → New environment**. Name it **production**.

Under that environment's **Environment secrets**, add:

| Name | Value |
| --- | --- |
| DEPLOY_HOST | 162.243.224.95 |
| DEPLOY_SSH_KEY | Full contents of your new private-key file, including BEGIN and END lines |
| DEPLOY_KNOWN_HOSTS | The host-key line from step 2 |

To display the automation private key locally:

```powershell
Get-Content "$env:USERPROFILE\.ssh\vendorops_github"
```

Paste it only into GitHub's secret field. Do not commit it or post it in chat. Do not use the `.pub` file for DEPLOY_SSH_KEY.

Add an **environment variable** in production:

| Name | Value |
| --- | --- |
| APP_URL | Your actual HTTPS URL, for example https://ops.yourdomain.com |

Create a **repository variable** at **Settings → Secrets and variables → Actions → Variables**:

| Name | Initial value |
| --- | --- |
| ENABLE_DEPLOY | false |

ENABLE_DEPLOY must be a repository variable because the job condition is evaluated before environment variables are available. APP_URL belongs to the production environment. Django and SMTP secrets remain on the droplet under /etc/vendorops; do not add them to GitHub.

If your plan supports environment deployment restrictions, restrict production to master. You can add a required reviewer if you want to approve deployments manually. Otherwise successful master pushes deploy automatically after you enable them. See [GitHub's environment and deployment controls](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments) and [secret setup instructions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).

## 4. Check the droplet firewall

GitHub-hosted runners need to reach SSH port 22. If you previously allowed SSH only from your own IP, that rule will block GitHub runners. Their IPs vary between runs.

Choose a deliberate firewall solution before enabling deployment: GitHub larger runners with a static IP, a private-network connection, or broader SSH access with key authentication. Do not install a general-purpose self-hosted runner on the production droplet to run pull-request code. Preserve your own SSH access when changing rules.

## 5. Commit and push the workflow

**Windows PowerShell, in the project folder:**

```powershell
git status
git add .github/workflows/ci-cd.yml .gitattributes deploy
git diff --cached --stat
git commit -m "Add GitHub Actions CI and droplet deployment"
git push origin master
```

Review what is staged before committing. The deploy directory was previously untracked; it must be committed for the workflow to work. Never stage private keys, production environment files or databases.

Open **GitHub → Actions → Test and deploy**. On this first push the test job runs and the deploy job is skipped because ENABLE_DEPLOY is false.

If any test fails, open the failed step and fix the error. The exact pinned requirements must install on Python 3.12; if you changed those on the droplet, reconcile the committed requirements before enabling deployment.

## 6. Enable the first deployment

Take a DigitalOcean snapshot or verify a recent PostgreSQL backup first. Follow the PostgreSQL setup in README.md: install PostgreSQL and pg_dump on the droplet, create the database/role, and set DB_NAME, DB_USER, DB_PASSWORD, DB_HOST=127.0.0.1 and DB_PORT=5432 in /etc/vendorops/backend.env. The app role owns the database and can run migrations; production does not need CREATEDB. Django tests use a separate database created by the disposable CI role. Local uploads/media inside the source folder are not carried into the new deployment; persistent files must live outside /opt/vendorops/app.

Change the repository variable **ENABLE_DEPLOY** to **true**.

Open **Actions → Test and deploy → Run workflow**, select **master**, and run it. Tests run first, then deployment.

The deployment:

1. Uploads committed source over SSH with host-key checking.
2. Saves the current source and stops both services.
3. Backs up PostgreSQL using Django's configured credentials and preserves the old application directory.
4. Replaces source with a clean tree, installs dependencies, migrates, builds, and restarts services.
5. Checks the frontend and Django locally, then checks the public HTTPS login page.

Check the app in your browser and sign in. A successful HTTP check does not replace checking a real login and form submission.

## 7. Your normal workflow afterward

For direct updates, commit and push to master. For a safer review process, create a branch, open a pull request, wait for checks, then merge it into master. GitHub deploys the merged commit.

Protect master in repository settings: require pull requests and the `test` status check if you want changes reviewed before deployment. Do not rename the branch without updating the workflow's push filter and deployment condition.

Deployments are serialized, and a running deployment is not cancelled by a newer push. A server lock also prevents overlapping deployment scripts. Multiple queued pushes may be coalesced by GitHub; the latest queued revision is the important deployment.

## Failures and recovery

If tests fail, deployment does not run. If deployment fails after services stop, they may stay stopped and GitHub reports failure. Inspect:

```sh
systemctl status vendorops-backend vendorops-frontend --no-pager
journalctl -u vendorops-backend -u vendorops-frontend -n 100 --no-pager
ls -lt /var/backups/vendorops
```

Each deployment backup directory contains source.tar.gz, db.dump (PostgreSQL custom format), and the previous-app directory once the source switch occurs. Use pg_restore for a database recovery, as described in README.md. The shared Python virtual environment is not backed up; a rollback must reinstall the old requirements too.

There is no automatic rollback: migrations may have changed the database. A failed HTTPS check can also mean the app started but DNS/TLS or the external network check failed. Diagnose before restoring data. Set ENABLE_DEPLOY to false to pause future deployments while investigating. Keep backups off the droplet and monitor storage: old source trees and uploaded archives are retained, so disk use grows.

The workflow and scripts are prepared locally. CI/CD becomes active only after you configure GitHub and push these files.
