# Vendor Ops

The SvelteKit server calls the Django API, so browser requests stay same-origin and Django does not need CORS enabled. The API base URL is configured with the private `DJANGO_API_URL` environment variable; it defaults to `http://127.0.0.1:8000` for local development.

## Run locally

Start Django in one terminal:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

Start SvelteKit in a second terminal:

```powershell
cd frontend/vendorops
pnpm install
$env:DJANGO_API_URL = "http://127.0.0.1:8000"
pnpm dev
```

Open the URL printed by Vite and sign in with the Django superuser. Set `DJANGO_API_URL` on the SvelteKit server in other environments; do not expose it as a `PUBLIC_` variable.

## Validate

```sh
pnpm check
pnpm build
```
