# LotOwl

LotOwl is a smart parking availability web application that helps users quickly find open parking lots using a live map and occupancy updates.

## Hackathon Context

This was a **group project for YSU Hackathon 2026**.
The idea was **generated, created, and fully implemented within 36 hours**.

Project repository:
https://github.com/sushilach/lotowl

## Features

- Interactive parking map (Leaflet)
- Lot summary panel (total, taken, available)
- Search parking lots by lot name or ID
- Navigation routing to selected lot
- Sensor-based occupancy updates via API
- Reset endpoint for quick demo/testing
- Database status page for deployment diagnostics

## Tech Stack

- Python 3.11+
- Flask
- Gunicorn
- PyMySQL
- HTML/CSS/JavaScript
- Leaflet + Leaflet Routing Machine

## Project Structure

- `main.py` - Flask app and API routes
- `templates/index.html` - Main UI
- `templates/db_status.html` - DB status page
- `static/css/style.css` - Styling
- `static/js/` - Frontend scripts
- `config/db_config.py` - Database URL/config helpers
- `requirements.txt` - Python dependencies

## API Endpoints

- `GET /` - Main app UI
- `GET /db-status` - Database connectivity status
- `GET /sensors` - All sensors
- `GET /lots` - All lots
- `GET /lots/<lot_id>` - One lot by ID
- `GET /summary` - Aggregated lot summary
- `POST /update` - Update lot occupancy from sensor input
- `POST /reset` - Reset all lot occupancy values

## Local Setup

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python main.py
   ```
4. Open in browser:
   http://127.0.0.1:8000

## Railway Deployment

Use this start command in Railway:

```bash
gunicorn -w 2 -k gthread -b 0.0.0.0:$PORT main:app
```

Recommended environment variables:

- `DATABASE_URL` (or `MYSQL_URL` / `MYSQL_PUBLIC_URL`)
- `MYSQL_USE_SSL=true`
- `MIN_DETECTION_ACCURACY=0.50`
- `FLASK_DEBUG=false`

## Git Push

After changes, push everything with:

```bash
git add .
git commit -m "Update project documentation and app changes"
git push origin main
```

If your remote is not set yet:

```bash
git remote add origin https://github.com/sushilach/lotowl
git branch -M main
git push -u origin main
```
