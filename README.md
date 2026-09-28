# Groundwork

Lean garden planner PWA: name a plot, manage beds & plant placements, browse a cited plant bible, and one-tap suggest companion-aware layouts.

**Stack:** Django (session auth) · Tailwind CSS 3 · vanilla JS (esbuild) · SQLite

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
npm run build
python manage.py migrate
python manage.py seed_plants
python manage.py runserver
```

Open http://127.0.0.1:8000/ — sign up, complete plot onboarding, then edit layouts or browse **Plants**.

### Dev watch (CSS + JS)

```bash
npm run watch
```

Runs Tailwind watch and chokidar/esbuild minify of `src/js/*.js` → `static/js/` via `concurrently`.

## Features (Phase 1)

1. **Plot onboarding** — name, width/length (ft); first-run redirect when you have no layouts
2. **Named layouts CRUD** — beds + plant placements for logged-in users
3. **PWA** — `manifest.webmanifest`, `sw.js`, icons, meta tags in base template
4. **Plant bible** — ~22 common veggies with spacing, growth copy, companions, and citations; `seed_plants` management command
5. **One-tap suggest** — fills beds using spacing + companion scoring
6. **Hub** header link → https://frank-dixon.github.io/
7. **Stripe Pro stub** — `/pro/` placeholder only (no billing)

## Notes

- `TIME_ZONE = America/New_York`
- Do **not** enable GitHub Pages for this repo (app is meant to run as Django, not static Pages)
- Soil/leaf palette via Tailwind theme tokens (`soil-*`, `leaf-*`, `sand-*`)

## License

Personal project — Frank Dixon.
