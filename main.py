from flask import Flask, jsonify, request,render_template
from datetime import datetime
import json
import os
import logging
import threading
import pymysql

from config.db_config import get_database_url, get_mysql_settings

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)
SENSORS_FILE = os.path.join(DATA_DIR, "sensors.json")
LOTS_FILE = os.path.join(DATA_DIR, "lots.json")
DEFAULT_SENSORS_FILE = os.path.join(BASE_DIR, "sensors.json")
DEFAULT_LOTS_FILE = os.path.join(BASE_DIR, "lots.json")

# Lock to prevent concurrent read/write races when saving/loading JSON files
_FILE_LOCK = threading.Lock()


def load_json_file(file_path):
    if not os.path.exists(file_path):
        return []

    try:
        with _FILE_LOCK:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_json_file(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # Write atomically: write to temp file, then replace original
    tmp_path = f"{file_path}.tmp"
    with _FILE_LOCK:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, file_path)


def env_flag(name, default=False):
    value = os.environ.get(name, str(default))
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_float(name, default):
    value = os.environ.get(name, str(default))
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def check_db_connection_status():
    database_url = get_database_url()
    mysql_settings = get_mysql_settings()

    if mysql_settings.get("scheme") not in {"mysql", "mysql+pymysql"}:
        return {
            "ok": False,
            "message": "DATABASE_URL is not configured for MySQL.",
            "database_url": database_url,
            "details": "Expected a mysql:// URL from Railway (MYSQL_URL or MYSQL_PUBLIC_URL).",
        }

    host = mysql_settings.get("host")
    port = mysql_settings.get("port") or 3306
    user = mysql_settings.get("user")
    password = mysql_settings.get("password")
    database = mysql_settings.get("database")

    if not host or not user or not database:
        return {
            "ok": False,
            "message": "DATABASE_URL is missing required values.",
            "database_url": database_url,
            "details": "Host, user, and database are required.",
        }

    try:
        conn = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
            connect_timeout=8,
            read_timeout=8,
            write_timeout=8,
            cursorclass=pymysql.cursors.DictCursor,
            ssl={"ssl": {}} if os.environ.get("MYSQL_USE_SSL", "true").lower() == "true" else None,
        )
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS ok")
            result = cur.fetchone()
            cur.execute("SHOW TABLES")
            tables = cur.fetchall()
        conn.close()

        return {
            "ok": True,
            "message": "Database connection successful.",
            "database_url": database_url,
            "details": f"Ping returned {result}. Tables found: {len(tables)}",
            "host": host,
            "port": port,
            "database": database,
            "user": user,
        }
    except Exception as exc:
        return {
            "ok": False,
            "message": "Database connection failed.",
            "database_url": database_url,
            "details": str(exc),
            "host": host,
            "port": port,
            "database": database,
            "user": user,
        }


def load_sensors():
    sensors = load_json_file(SENSORS_FILE)
    if sensors:
        return sensors

    # Seed runtime data directory from repository defaults when mounted volumes are empty.
    fallback = load_json_file(DEFAULT_SENSORS_FILE)
    if fallback and SENSORS_FILE != DEFAULT_SENSORS_FILE:
        save_json_file(SENSORS_FILE, fallback)
        app.logger.info("Seeded sensors file from defaults: %s", SENSORS_FILE)
    return fallback


def load_lots():
    lots = load_json_file(LOTS_FILE)
    if lots:
        return lots

    # Seed runtime data directory from repository defaults when mounted volumes are empty.
    fallback = load_json_file(DEFAULT_LOTS_FILE)
    if fallback and LOTS_FILE != DEFAULT_LOTS_FILE:
        save_json_file(LOTS_FILE, fallback)
        app.logger.info("Seeded lots file from defaults: %s", LOTS_FILE)
    return fallback


def save_lots(data):
    save_json_file(LOTS_FILE, data)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/db-status", methods=["GET"])
def db_status_page():
    status = check_db_connection_status()
    return render_template("db_status.html", status=status), (200 if status.get("ok") else 500)


@app.route("/sensors", methods=["GET"])
def get_sensors():
    sensors = load_sensors()
    return jsonify({
        "count": len(sensors),
        "sensors": sensors
    }), 200


@app.route("/lots", methods=["GET"])
def get_lots():
    lots = load_lots()
    return jsonify({
        "count": len(lots),
        "lots": lots
    }), 200


@app.route("/lots/<lot_id>", methods=["GET"])
def get_lot(lot_id):
    lots = load_lots()

    for lot in lots:
        if lot.get("lot_id") == lot_id:
            total = lot.get("max_capacity", 0)
            taken = lot.get("occupied_count", 0)
            available = total - taken

            return jsonify({
                "lot_id": lot.get("lot_id"),
                "name": lot.get("name", ""),
                "max_capacity": total,
                "occupied_count": taken,
                "available": available,
                "last_updated": lot.get("last_updated", "")
            }), 200

    return jsonify({"error": "Lot not found"}), 404


@app.route("/summary", methods=["GET"])
def get_summary():
    lots = load_lots()
    summary = []

    for lot in lots:
        total = lot.get("max_capacity", 0)
        taken = lot.get("occupied_count", 0)
        available = total - taken

        summary.append({
            "lot_id": lot.get("lot_id"),
            "name": lot.get("name", ""),
            "total": total,
            "taken": taken,
            "available": available,
            "last_updated": lot.get("last_updated", "")
        })

    return jsonify({
        "count": len(summary),
        "lots": summary
    }), 200


@app.route("/update", methods=["POST"])
def update_from_sensor():
    incoming = request.get_json()

    app.logger.info("Received /update POST: %s", incoming)

    if not incoming:
        return jsonify({"error": "No JSON data received"}), 400

    device_id = incoming.get("deviceId", incoming.get("device_id"))
    accuracy = incoming.get("accuracy", incoming.get("confidence"))

    if device_id is None:
        return jsonify({"error": "deviceId (or device_id) is required"}), 400

    if accuracy is None:
        return jsonify({"error": "accuracy is required"}), 400

    try:
        accuracy = float(accuracy)
    except (TypeError, ValueError):
        return jsonify({"error": "accuracy must be a number"}), 400


    min_accuracy = env_float("MIN_DETECTION_ACCURACY", 0.50)
    if accuracy < min_accuracy:
        app.logger.info(
            "Ignored detection from device %s due to low accuracy %s (min=%s)",
            device_id,
            accuracy,
            min_accuracy,
        )
        return jsonify({
            "message": "Detection ignored because accuracy is too low",
            "deviceId": device_id,
            "accuracy": accuracy,
            "min_required_accuracy": min_accuracy,
        }), 200

    try:
        device_id = str(int(device_id))
    except (TypeError, ValueError):
        device_id = str(device_id)

    sensors = load_sensors()
    matched_sensor = None

    for sensor in sensors:
        sensor_device_id = sensor.get("device_id")
        try:
            sensor_device_id = str(int(sensor_device_id))
        except (TypeError, ValueError):
            sensor_device_id = str(sensor_device_id)

        if sensor_device_id == device_id:
            matched_sensor = sensor
            break

    if not matched_sensor:
        app.logger.info("Unknown deviceId: %s", device_id)
        return jsonify({"error": "Unknown deviceId"}), 404

    sensor_type = matched_sensor.get("type")
    lot_id = matched_sensor.get("lot_id")

    if sensor_type not in ["entry", "exit"]:
        return jsonify({"error": "Sensor type must be 'entry' or 'exit'"}), 400

    lots = load_lots()

    for lot in lots:
        if lot.get("lot_id") == lot_id:
            current_count = lot.get("occupied_count", 0)
            max_capacity = lot.get("max_capacity", 0)

            if sensor_type == "entry":
                if current_count >= max_capacity:
                    return jsonify({
                        "message": "Lot is already full",
                        "lot_id": lot_id,
                        "occupied_count": current_count,
                        "max_capacity": max_capacity
                    }), 200

                lot["occupied_count"] = current_count + 1

            elif sensor_type == "exit":
                if current_count <= 0:
                    return jsonify({
                        "message": "Lot is already empty",
                        "lot_id": lot_id,
                        "occupied_count": current_count
                    }), 200

                lot["occupied_count"] = current_count - 1

            lot["last_updated"] = datetime.now().isoformat()

            # Log the update and file path being written
            app.logger.info(
                "Updating lot %s: %s -> %s (sensor=%s device=%s file=%s)",
                lot_id,
                current_count,
                lot.get("occupied_count"),
                sensor_type,
                device_id,
                LOTS_FILE,
            )

            save_lots(lots)

            total = lot.get("max_capacity", 0)
            taken = lot.get("occupied_count", 0)
            available = total - taken

            return jsonify({
                "message": "Lot updated successfully",
                "deviceId": device_id,
                "sensor_type": sensor_type,
                "accuracy": accuracy,
                "lot": {
                    "lot_id": lot.get("lot_id"),
                    "name": lot.get("name", ""),
                    "max_capacity": total,
                    "occupied_count": taken,
                    "available": available,
                    "last_updated": lot.get("last_updated", "")
                }
            }), 200

    return jsonify({"error": "Matching lot not found for this sensor"}), 404


@app.route("/reset", methods=["POST"])
def reset_lots():
    lots = load_lots()

    for lot in lots:
        lot["occupied_count"] = 0
        lot["last_updated"] = ""

    save_lots(lots)

    return jsonify({
        "message": "All parking lots have been reset"
    }), 200


if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
        debug=env_flag("FLASK_DEBUG", True),
    )
