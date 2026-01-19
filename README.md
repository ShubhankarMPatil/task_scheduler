# Task Time Tracker (Full Stack)
Backend: Django + Django REST Framework
Frontend: Next.js (App Router) + TypeScript + Axios

## Features (assignment requirements)
- Full CRUD for tasks (create, list/view, update, delete)
- Reporting/chart derived from DB data: completed vs pending counts
- Third-party API integration (World Time API) proxied via backend and displayed in UI
- Production-ready configuration via environment variables

## Project structure
- `backend/` — Django project (API)
- `frontend/` — Next.js project (UI)

## Prerequisites
- Python 3.10+ (3.11+ recommended)
- Node.js 18+ (or newer)

## Backend setup (Django)
From repo root:
```bash
cd backend
python -m venv venv
# activate venv (Windows)
venv\Scripts\activate
pip install -r requirements.txt

# env
copy .env.example .env

python manage.py migrate
python manage.py runserver
```
Backend will run at `http://127.0.0.1:8000/`.

### Backend environment variables
Set these in `backend/.env`:
- `DEBUG` (True/False)
- `SECRET_KEY`
- `ALLOWED_HOSTS` (comma-separated)
- `DATABASE_URL` (optional; if omitted defaults to SQLite)
- `CORS_ALLOW_ALL_ORIGINS` and optionally `CORS_ALLOWED_ORIGINS`

## Frontend setup (Next.js)
From repo root:
```bash
cd frontend
npm install

# env
copy .env.example .env.local

npm run dev
```
Frontend will run at `http://localhost:3000/`.

### Frontend environment variables
Set these in `frontend/.env.local`:
- `NEXT_PUBLIC_API_BASE_URL` (example: `http://127.0.0.1:8000/api`)

## API endpoints (backend)
- CRUD Tasks: `GET/POST /api/tasks/`, `GET/PATCH/PUT/DELETE /api/tasks/{id}/`
- Reporting: `GET /api/tasks/stats/?date=YYYY-MM-DD` (date optional)
- Third-party: `GET /api/tasks/world-time/`
- (Optional existing endpoint) `GET /api/dashboard/?date=YYYY-MM-DD`

## How to test CRUD end-to-end (step-by-step)
1. Start the backend (`python manage.py runserver`).
2. Start the frontend (`npm run dev`).
3. Open `http://localhost:3000/tasks`.
4. Create a task using the “Add task” form.
5. Verify the task appears in the list (View).
6. Update the task:
   - Toggle the completed checkbox
   - Use “Rename” or “Set target”
7. Delete the task with “Delete”.
8. Confirm all actions update the DB and UI immediately.

## Dashboard / report path
- UI: `http://localhost:3000/tasks`
- Chart: “Status” pie chart (Completed vs Pending) fed by `GET /api/tasks/stats/`

## Third-party API integration path
- Backend: `GET /api/tasks/world-time/`
- UI: World Time panel on `http://localhost:3000/tasks`

## Deployment notes (high level)
- Set `DEBUG=False` and a strong `SECRET_KEY`.
- Set `ALLOWED_HOSTS` to your domain(s).
- Provide `DATABASE_URL` (Postgres recommended in production).
- For Django static files:
  - run `python manage.py collectstatic`
  - serve `backend/staticfiles/` via your web server / platform
- Run Django with Gunicorn (example):
  - `gunicorn core.wsgi:application`
- Frontend can be deployed with Vercel (or run as Node server via `next build` + `next start`).
