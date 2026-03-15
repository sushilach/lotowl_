# 🦉 LotOwl — Real-Time Parking Availability

LotOwl is a smart parking availability web application that helps users quickly find open parking lots using a live map and real-time occupancy updates.

> ⚠️ This is a personal fork of [bananaPeppers/lotowl](https://github.com/bananaPeppers/lotowl), originally built for YSU Hackathon 2026.

---

## 🏆 Hackathon Context

This was a group project for **YSU Hackathon 2026**. The idea was generated, designed, and fully implemented within **36 hours** by a team of 4.

**Original repository:** [bananaPeppers/lotowl](https://github.com/bananaPeppers/lotowl)  
**This fork:** [sushilach/lotowl](https://github.com/sushilach/lotowl)

---

## 🚀 Features

- Interactive parking map (Leaflet)
- Lot summary panel (total, taken, available)
- Search parking lots by lot name or ID
- Navigation routing to selected lot
- Sensor-based occupancy updates via API
- Reset endpoint for quick demo/testing
- Database status page for deployment diagnostics

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, Flask, Gunicorn |
| Database | MySQL via PyMySQL |
| Frontend | HTML, CSS, JavaScript |
| Maps | Leaflet + Leaflet Routing Machine |
| Deployment | Railway |

---

## 📁 Project Structure

```
lotowl/
├── main.py                  # Flask app and API routes
├── templates/
│   ├── index.html           # Main UI
│   └── db_status.html       # DB status page
├── static/
│   ├── css/style.css        # Styling
│   └── js/                  # Frontend scripts
├── config/
│   └── db_config.py         # Database URL/config helpers
└── requirements.txt         # Python dependencies
```

---

## 🗺️ API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Main app UI |
| GET | `/db-status` | Database connectivity status |
| GET | `/sensors` | All sensors |
| GET | `/lots` | All lots |
| GET | `/lots/<lot_id>` | One lot by ID |
| GET | `/summary` | Aggregated lot summary |
| POST | `/update` | Update lot occupancy from sensor input |
| POST | `/reset` | Reset all lot occupancy values |

---

## ⚙️ Local Setup

1. Clone this fork:
```bash
git clone https://github.com/sushilach/lotowl.git
cd lotowl
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
python main.py
```

4. Open in browser: `http://127.0.0.1:8000`

---

## 🚂 Railway Deployment

Use this start command in Railway:
```bash
gunicorn -w 2 -k gthread -b 0.0.0.0:$PORT main:app
```

Recommended environment variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Main DB connection string (or `MYSQL_URL` / `MYSQL_PUBLIC_URL`) |
| `MYSQL_USE_SSL` | Set to `true` |
| `MIN_DETECTION_ACCURACY` | Set to `0.50` |
| `FLASK_DEBUG` | Set to `false` in production |

---

## 📤 Git Push

After making changes:
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

If your remote is not set yet:
```bash
git remote add origin https://github.com/sushilach/lotowl
git branch -M main
git push -u origin main
```

---

## 👥 Original Team (YSU Hackathon 2026)

- [@prah-lad](https://github.com/prah-lad)
- [@sushilach](https://github.com/sushilach)
- https://github.com/bananaPeppers
- https://github.com/JonFactor

---

## 📄 License

Open source. Built in 36 hours at YSU Hackathon 2026.  
Original project posted in [bananaPeppers](https://github.com/bananaPeppers/lotowl).
