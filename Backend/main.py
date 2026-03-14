from flask import Flask, jsonify, request
from datetime import datetime
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SENSORS_FILE = os.path.join(BASE_DIR, "sensors.json")
LOTS_FILE = os.path.join(BASE_DIR, "lots.json")


def load_json_file(file_path):
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_json_file(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def load_sensors():
    return load_json_file(SENSORS_FILE)


def load_lots():
    return load_json_file(LOTS_FILE)


def save_lots(data):
    save_json_file(LOTS_FILE, data)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Parking lot backend is running",
        "status": "success"
    }), 200


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

    if not incoming:
        return jsonify({"error": "No JSON data received"}), 400

    device_id = incoming.get("deviceId")
    accuracy = incoming.get("accuracy")

    if device_id is None:
        return jsonify({"error": "deviceId is required"}), 400

    if accuracy is None:
        return jsonify({"error": "accuracy is required"}), 400

    try:
        accuracy = float(accuracy)
    except (TypeError, ValueError):
        return jsonify({"error": "accuracy must be a number"}), 400

    # Hardware sends accuracy like 0.75, 0.80, 1.0
    if accuracy <= 0.60:
        return jsonify({
            "message": "Detection ignored because accuracy is too low",
            "deviceId": device_id,
            "accuracy": accuracy
        }), 200

    sensors = load_sensors()
    matched_sensor = None

    for sensor in sensors:
        if sensor.get("device_id") == device_id:
            matched_sensor = sensor
            break

    if not matched_sensor:
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
    app.run(host="0.0.0.0", port=5000, debug=True)