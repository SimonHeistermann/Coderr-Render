# Coderr — Fullstack Service Marketplace

> A Fiverr-style freelance service marketplace with Django REST backend and vanilla JavaScript frontend — training project from Developer Akademie.

## Disclaimer

This is a **training project** built as part of my education at [Developer Akademie](https://developerakademie.com/). It is **not** a commercial product and is not intended for real-world use.

- No real services are offered or transactions processed
- No real orders, payments, or deliveries take place
- Any resemblance to real businesses is for educational demonstration only
- **Do not enter real personal data** — demo accounts are available for testing

For questions, contact: [simon@heistermann-solutions.de](mailto:simon@heistermann-solutions.de)

---

## About

Coderr simulates a freelance service marketplace where business users can create and manage service offers with tiered packages, and customers can browse, order, and review those services. The project demonstrates fullstack development with a REST API backend, token-based authentication, role-based permissions, and a responsive vanilla JavaScript frontend.

**Related repository:** The backend-only version (submitted for Developer Akademie evaluation) is available at [SimonHeistermann/Coderr](https://github.com/SimonHeistermann/Coderr).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6.0 |
| **API** | Django REST Framework |
| **Auth** | Token Authentication |
| **Database** | SQLite (dev) / PostgreSQL (prod optional) |
| **Filtering** | django-filter |
| **Env Management** | python-dotenv / `.env` / `env-template` |
| **Frontend** | HTML + CSS + Vanilla JavaScript |
| **Deployment** | Gunicorn + Render |

---

## Features

- **User Authentication** — Registration & Login (Token-based), Customer & Business user roles
- **Offers & Packages** — Business users can create offers with multiple packages (basic/standard/premium), public browsing & search
- **Orders** — Customers can place orders, businesses manage orders, status tracking (in progress, completed, cancelled)
- **Reviews** — Customers can review business users, one review per customer/business pair
- **Base Info / Stats** — Average rating, review count, offer count
- **Permissions & Security** — Role-based access control, token authentication, throttling for sensitive endpoints
- **CORS-ready** for local development and production

---

## Getting Started

### Prerequisites

- **Python 3.13+**
- **pip** (Python package manager)
- **Git**
- **(Optional)** Virtual environment (`venv`)

### 1. Clone Repository
```bash
git clone https://github.com/SimonHeistermann/Coderr-Render.git
cd Coderr-Render
```

### 2. Create and Activate a Virtual Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
```bash
cp env-template .env # macOS / Linux
# or
copy env-template .env # Windows (Command Prompt)
```
> **Tip:** Never commit your `.env` file to Git.
> You can safely use the default values for local development.
> Optionally, replace `SECRET_KEY` or toggle `DEBUG`.

### 5. Generate your own SECRET_KEY
Django requires a secret key for cryptographic signing.
You must generate one manually and add it to your `.env` file.

**Option 1 (recommended):**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the generated key into your `.env` file:
```bash
SECRET_KEY='your-secret-key-here'
```

**Option 2:**
If Django isn't installed yet, use an online generator such as [djecrety.ir](https://djecrety.ir/) and paste the result into your `.env`.

### 6. Run Migrations
```bash
python manage.py migrate
```

### 7. Create a Superuser
```bash
python manage.py createsuperuser
```

### 8. Run the Development Server
```bash
python manage.py runserver
```
Open in browser: http://127.0.0.1:8000/

### 9. Open Django Admin & create guest users for guest login

Open the Admin Panel: http://127.0.0.1:8000/admin/

Log into the admin page and create guest users with the following information.
After creating each Django User, also create the corresponding UserProfile with the correct type (customer/business):

#### Guest Customer User

| Field | Value |
|-------|-------|
| **Username** | guest.customer |
| **Email** | guest_customer@guest.de |
| **Password** | o6B6<c1x\|`N2 |
| **First Name** | Guest |
| **Last Name** | Customer |
| **Type** | customer |

#### Guest Business User

| Field | Value |
|-------|-------|
| **Username** | guest.business |
| **Email** | guest_business@guest.de |
| **Password** | o6B6<c1x\|`N2 |
| **First Name** | Guest |
| **Last Name** | Business |
| **Type** | business |

---

## Frontend Setup (Vanilla JS)

### 1. Configure API Base URL

In `frontend/shared/scripts/config.js`:
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api/';
```

### 2. Run frontend locally

**Option A (recommended):** VS Code Live Server
- Open `frontend/index.html`
- Right-click → Open with Live Server

**Option B:** Simple Python static server
```bash
cd frontend
python -m http.server 5500
```

Frontend runs on: http://127.0.0.1:5500/

---

## Authentication

All protected endpoints require the header:
```
Authorization: Token <YOUR_TOKEN>
```

Tokens are returned on:
- `POST /api/registration/`
- `POST /api/login/`

---

## Throttling

The API applies throttling to prevent abuse:

| Scope | Limit |
|-------|-------|
| **Anonymous users** | 100 / day |
| **Authenticated users** | 1000 / day |
| **Login** | 5 / minute |
| **Registration** | 3 / minute |
| **Order creation** | 20 / hour |

---

## Hosting / Production Setup

If you plan to host your project (e.g. on Render, Railway, or your own VPS/server):

### Update your .env file
```
DEBUG=False
SECRET_KEY=<your-production-secret>
ALLOWED_HOSTS=coderr.yourdomain.com
DATABASE_URL=postgres://user:pass@host:port/dbname
CORS_ALLOWED_ORIGINS=https://coderr.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://coderr.yourdomain.com
```

### Collect static files
```bash
python manage.py collectstatic
```

### Configure Gunicorn + Reverse Proxy (e.g. Nginx)

Set up Gunicorn as your WSGI server and use Nginx to serve static files and handle HTTPS requests.

Example (conceptually):
- Gunicorn listens on `127.0.0.1:8000`
- Nginx listens on port 80/443 and proxies requests to Gunicorn

### SSL Certificates

Use Let's Encrypt (via Certbot) to enable HTTPS.

### Debugging Tips

If you get 403 Forbidden errors:
- Check your Browser DevTools → Network tab
- Ensure the request includes the header: `Authorization: Token <YOUR_TOKEN>`
- Guest users don't need admin rights, but they must be authenticated (valid token present)

Remember: Django only loads `.env` values when the server starts, so after editing your `.env`, restart it:
```bash
python manage.py runserver
```

---

## Project Structure
```
Coderr-Render/
├── backend/                  # Django project
│   ├── core/                 # Project configuration (settings, URLs)
│   ├── sales_app/            # Offers, orders, reviews
│   ├── user_auth_app/        # Registration, login, profiles
│   ├── manage.py
│   ├── requirements.txt
│   ├── env-template
│   └── Dockerfile
│
├── frontend/                 # Vanilla JS frontend
│   ├── index.html            # Landing page
│   ├── login.html            # Login page
│   ├── registration.html     # Registration page
│   ├── offer_list.html       # Offer marketplace
│   ├── offer.html            # Single offer detail
│   ├── own_profile.html      # User's own profile
│   ├── business_profile.html # Public business profile
│   ├── customer_profile.html # Public customer profile
│   ├── imprint.html          # Impressum (Legal Notice)
│   ├── privacy_policy.html   # Datenschutzerklärung (Privacy Policy)
│   ├── shared/               # Shared scripts, styles, assets
│   └── assets/               # Images, icons, fonts
│
└── README.md
```

---

## Testing

Run tests with coverage from the `backend/` directory:
```bash
coverage run manage.py test
coverage report -m
```
Current coverage target: ≥ 95%

---

## Legal

- [Impressum (Legal Notice)](frontend/imprint.html)
- [Datenschutzerklärung (Privacy Policy)](frontend/privacy_policy.html)

---

## Author

**Simon Maximilian Heistermann**
- Website: [simon-heistermann.de](https://simon-heistermann.de)
- Email: [simon@heistermann-solutions.de](mailto:simon@heistermann-solutions.de)
- LinkedIn: [Simon Heistermann](https://www.linkedin.com/in/simon-heistermann/)

---

## License

This project is part of a training curriculum and is not licensed for commercial use.
