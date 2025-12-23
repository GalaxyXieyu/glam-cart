# Repository Guidelines

## Project Structure & Module Organization
- `frontend/`: Vite + React + TypeScript app. Source in `frontend/src/` (components, pages, hooks, lib, types) and static assets in `frontend/public/`.
- `backend/`: FastAPI service. Core modules include `backend/main.py`, `backend/models.py`, `backend/schemas.py`, and `backend/auth.py`. Static uploads live in `backend/static/` (product images, carousels, QR codes).
- Deployment/support scripts: `manage-services.sh`, `start-services.sh`, `stop-services.sh`, and `nginx-glam-cart.conf`.

## Build, Test, and Development Commands
Frontend (run from `frontend/`):
- `npm install`: install dependencies.
- `npm run dev`: start local dev server.
- `npm run build`: production build to `frontend/dist/`.
- `npm run preview`: serve the built bundle locally.
- `npm run lint`: run ESLint.

Backend (run from `backend/`):
- `python -m venv .venv && source .venv/bin/activate`: create/activate venv.
- `pip install -r requirements.txt`: install dependencies.
- `python run.py`: start API server (reads `.env`).
- `python -m pytest tests/ -v`: run tests.
- `python tests/run_tests.py`: start server and run tests.

Ops helpers (root): `./manage-services.sh status|start|stop` to control backend + nginx (requires local nginx setup).

## Coding Style & Naming Conventions
- Python: 4-space indentation, PEP8 style, snake_case for modules/functions, PascalCase for classes.
- TypeScript/React: 2-space indentation in JSX, PascalCase component names in `frontend/src/components/`, `useX` naming for hooks, Tailwind utility classes for styling.
- Linting: use `npm run lint` before PRs; keep new ESLint warnings to zero.

## Testing Guidelines
- Backend uses `pytest` with tests in `backend/tests/` named `test_*.py`.
- No dedicated frontend test runner is configured; validate UI changes via `npm run dev` and manual checks.
- No coverage threshold is defined; add tests for new API endpoints or data model changes.

## Commit & Pull Request Guidelines
- This deployment snapshot does not include a `.git` history, so no established commit convention is visible. Use concise, imperative commit subjects (e.g., "Add carousel sort order").
- PRs should include: a short summary, test commands run, and screenshots/GIFs for UI changes. Link related issues when applicable.

## Configuration & Security Notes
- Backend config lives in `backend/.env` (database URL, JWT secret, admin credentials). Avoid committing real secrets.
- Frontend env lives in `frontend/.env` (API base URL). Keep values aligned with backend host/port.
