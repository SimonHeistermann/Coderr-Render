# 🧩 Coderr - Fullstack (Frontend + Backend)

**Coderr** is a fullstack service marketplace app with:

✅ a Django REST Framework backend API

✅ a plain HTML/CSS/JavaScript frontend (no framework)

The project is designed to run locally and to be deployed on **Render**.

---

## 🚀 Features

- 👤 **User Authentication**
  - Registration & Login (Token-based)
  - Customer & Business user roles
- 🏷️ **Offers & Packages**
  - Business users can create offers with multiple packages
  - Public browsing & search
- 🛒 **Orders**
  - Customers can place orders
  - Businesses can manage orders on their offers
  - Status tracking (in progress, completed, cancelled)
- ⭐ **Reviews**
  - Customers can review business users
  - One review per customer/business pair
- 📊 **Base Info / Stats**
  - Average rating
  - Review count
  - Offer count
- 🔐 **Permissions & Security**
  - Role-based access control
  - Token authentication
  - Throttling for sensitive endpoints (login, registration, order creation)
- 🌐 **CORS-ready** for local development and production

---

## 🧠 Tech Stack

| Layer | Technology |
|------|-----------|
| **Backend** | Django 6.0 |
| **API** | Django REST Framework |
| **Auth** | Token Authentication |
| **Database** | SQLite (dev) / PostgreSQL (prod optional) |
| **Filtering** | django-filter |
| **Env Management** | python-dotenv  | `.env` / `env-template` |
| **Frontend** | HTML + CSS * Vanilla JavaScript |
| **Deployment** | Gunicorn-compatible |

---

## 📦 Requirements

- **Python 3.13+**
- **pip** (Python package manager)
- **Git**
- **(Optional)** Virtual environment (`venv`)

---

## 🛠️ Setup (Development)

### 1️⃣ Clone Repository
```bash
git clone https://github.com/SimonHeistermann/Coderr-Render.git
cd Coderr-Render
```

### 2️⃣ Create and Activate a Virtual Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Environment Setup
```bash
cp env-template .env # macOS / Linux
# or
copy env-template .env # Windows (Command Prompt)
```
🔐 Tip: Never commit your .env file to Git.
You can safely use the default values for local development.
Optionally, replace SECRET_KEY or toggle DEBUG.

### 5️⃣ 🔑 Generate your own SECRET_KEY
Django requires a secret key for cryptographic signing.
You must generate one manually and add it to your .env file.

Option 1 (recommended):
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the generated key into your .env file:
```bash
SECRET_KEY='your-secret-key-here'
```

Option 2:
If Django isn’t installed yet, use an online generator such as
👉 https://djecrety.ir/

and paste the result into your .env.

### 6️⃣ Run Migrations
```bash
python manage.py migrate
```

### 7️⃣ Create a Superuser
```bash
python manage.py createsuperuser
```

### 8️⃣ Run the Development Server
```bash
python manage.py runserver
```

--> Open in browser:
➡️ http://127.0.0.1:8000/

### 9️⃣ Open Django Admin & create guest users for guest login

Open:
Admin Panel: http://127.0.0.1:8000/admin/

Log into the admin page of the project and create guest users with the following information:

--> After creating the Django User, also create the corresponding UserProfile with the correct type (customer/business):

#### Guest Customer User

| Field       | Value                      |
|-------------|----------------------------|
| **Username** | guest.customer            |
| **Email**    | guest_customer@guest.de   |
| **Password** | o6B6<c1x|`N2              |
| **First Name** | Guest                   |
| **Last Name**  | Customer                |
| **Type**  | customer                     |

#### Guest Business User

| Field       | Value                      |
|-------------|----------------------------|
| **Username** | guest.business            |
| **Email**    | guest_business@guest.de   |
| **Password** | o6B6<c1x|`N2              |
| **First Name** | Guest                   |
| **Last Name**  | Business                |
| **Type**  | business                     |

---

## 🎨 Frontend Setup (Vanilla JS)

### 1️⃣ Configure API Base URL

In frontend/config.js:
```bash
export const API_BASE_URL = "http://127.0.0.1:8000";
```

### 2️⃣ Run frontend locally

Option A (recommended): VS Code Live Server

- Open frontend/index.html

- Right-click → Open with Live Server

Option B: simple Python static server
```bash
cd frontend
python -m http.server 5500
```

Frontend runs on:
➡️ http://127.0.0.1:5500/

## 🔐 Authentication

All protected endpoints require the header:
```bash
Authorization: Token <YOUR_TOKEN>
```
### Tokens are returned on:

- POST /api/registration/
- POST /api/login/

---

## 🚦 Throttling

The API applies throttling to prevent abuse:

| Scope | Limit |
|------|-----------|
| **Anonymous users** | 100 / day |
| **Authenticated users** | 1000 / day |
| **Login** | 5 / minute |
| **Registration** | 3 / minute |
| **Order creation** | 20 / hour |

---

## 🌐 Hosting / Production Setup

If you plan to host your project (e.g. on Render, Railway, or your own VPS/server):

### 🔧 Update your .env file

DEBUG=False
SECRET_KEY=<your-production-secret>
ALLOWED_HOSTS=coderr.yourdomain.com
DATABASE_URL=postgres://user:pass@host:port/dbname
CORS_ALLOWED_ORIGINS=https://coderr.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://coderr.yourdomain.com

### 📦 Collect static files
```bash
python manage.py collectstatic
```

### ⚙️ Configure Gunicorn + Reverse Proxy (e.g. Nginx)

Set up Gunicorn as your WSGI server and use Nginx to serve static files and handle HTTPS requests.

Example (conceptually):

Gunicorn listens on 127.0.0.1:8000

Nginx listens on port 80/443 and proxies requests to Gunicorn

### 🔒 SSL Certificates

Use Let’s Encrypt (via Certbot) to enable HTTPS.

### 🧰 Debugging Tips

If you get 403 Forbidden errors:

Check your Browser DevTools → Network tab
→ Ensure the request includes the header:

Authorization: Token <YOUR_TOKEN>

--> Guest users don’t need admin rights, but they must be authenticated (valid token present).

Remember:
👉 Django only loads .env values when the server starts, so after editing your .env, restart it:
```bash
python manage.py runserver
```

### 📁 Project Structure
```bash
coderr/
│
├── backend/                  # Django project
│   ├── core/
│   ├── sales_app/
│   ├── user_auth_app/
│   ├── manage.py
│   ├── requirements.txt
│   ├── env-template
│   └── ...
│
├── frontend/                 # Vanilla frontend
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   ├── config.js             # API base URL (local/prod)
│   └── assets/
│
└── README.md
```

---

## 🧪 Testing

Run tests with coverage:
```bash
coverage run manage.py test
coverage report -m
```
Current coverage target: ≥ 95%

---

### 🧩 License

MIT License © 2025 Simon Heistermann