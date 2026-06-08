# Public Release Checklist

Use this checklist before pushing **EcoBridge Ghana** to a public GitHub repository.

## Do Not Upload

- `.env` or any `.env.*` file except `.env.example`
- `.venv/`, `.idea/`, `.pytest_cache/`, `__pycache__/`, and other local tooling folders
- `instance/`, `*.db`, `*.sqlite`, or `*.sqlite3`
- `app/static/uploads/*` except `.gitkeep`
- `app/static/team/*` unless the client has approved those portraits for public GitHub
- `app/static/campaign/*` unless the client has approved those videos/audio/images for public GitHub
- `ecobridge-deploy*.zip` or any generated deployment archive
- `tmp/`, generated CVs, presentations, videos, and exported documents
- Remotion/video workspaces, `node_modules/`, and generated media
- Real user data, private client documents, passwords, API keys, SMTP credentials, or hosting/database usernames

## Safe To Upload

- `app/` source code and templates
- `tests/`
- `requirements.txt`
- `run.py`
- `wsgi.py`
- `.gitignore`
- `.env.example`
- `README.md`
- Public branding assets approved for display
- Sanitized screenshots in `docs/screenshots/`

## Before Publishing

1. Confirm any real team, client, or campaign media has explicit public GitHub approval.
2. Use demo data in screenshots and avoid showing private email inboxes, admin passwords, or real user records.
3. Run a sensitive-data scan for passwords, API keys, production database URLs, and private documents.
4. Run the test suite with `pytest`.
5. After `git init`, check what Git will include with `git status --ignored`.
