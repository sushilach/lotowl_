from flask import Flask, jsonify, request
from datetime import datetime
import json
import os

app = Flask(__name__)

# To makes sure data.json is found correctly no matter where you run the file from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")


def load_data():
    """Load parking data from data.json. If file does not exist or is invalid, return empty list."""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_data(data):
    """Save parking data to data.json."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Parking lot backend is running",
        "status": "success"
    }), 200


@app.route("/spots", methods=["GET"])
def get_spots():
    data = load_data()
    return jsonify({
        "count": len(data),
        "spots": data
    }), 200


@app.route("/spots/<spot_id>", methods=["GET"])
def get_spot(spot_id):
    data = load_data()

    for spot in data:
        if spot.get("spot_id") == spot_id:
            return jsonify(spot), 200

    return jsonify({
        "error": "Spot not found"
    }), 404


@app.route("/update", methods=["POST"])
def update_spot():
    incoming = request.get_json()

    if not incoming:
        return jsonify({
            "error": "No JSON data received"
        }), 400

    if "spot_id" not in incoming:
        return jsonify({
            "error": "spot_id is required"
        }), 400

    data = load_data()
    spot_id = incoming["spot_id"]

    # Update existing spot
    for spot in data:
        if spot.get("spot_id") == spot_id:
            spot["is_occupied"] = incoming.get("is_occupied", spot.get("is_occupied", False))
            spot["device_id"] = incoming.get("device_id", spot.get("device_id", ""))
            spot["accuracy_score"] = incoming.get("accuracy_score", spot.get("accuracy_score", 0))
            spot["time_duration"] = incoming.get("time_duration", spot.get("time_duration", 0))
            spot["last_updated"] = datetime.now().isoformat()

            save_data(data)

            return jsonify({
                "message": "Spot updated successfully",
                "spot": spot
            }), 200

    # Add new spot if it does not exist
    new_spot = {
        "spot_id": spot_id,
        "is_occupied": incoming.get("is_occupied", False),
        "device_id": incoming.get("device_id", ""),
        "accuracy_score": incoming.get("accuracy_score", 0),
        "time_duration": incoming.get("time_duration", 0),
        "last_updated": datetime.now().isoformat()
    }

    data.append(new_spot)
    save_data(data)

    return jsonify({
        "message": "New spot added successfully",
        "spot": new_spot
    }), 201


@app.route("/delete/<spot_id>", methods=["DELETE"])
def delete_spot(spot_id):
    data = load_data()

    for i, spot in enumerate(data):
        if spot.get("spot_id") == spot_id:
            deleted_spot = data.pop(i)
            save_data(data)

            return jsonify({
                "message": "Spot deleted successfully",
                "spot": deleted_spot
            }), 200

    return jsonify({
        "error": "Spot not found"
    }), 404


@app.route("/reset", methods=["POST"])
def reset_data():
    save_data([])
    return jsonify({
        "message": "All parking data has been reset"
    }), 200


if __name__ == "__main__":
    app.run(debug=True)