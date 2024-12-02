from flask import Flask, request, jsonify
from db import get_db
import os

app = Flask(__name__)
db = get_db()

# Endpoint for initializing the room
@app.route('/initialize', methods=['POST'])
def initialize_room():
    """Initialize the room with immutable data"""
    data = request.json
    required_fields = ["id", "type", "profile", "metadata"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Check if a room with the same ID already exists
    if db.rooms.find_one({"id": data["id"]}):  # Now checks by ID
        return jsonify({"error": f"Room with ID {data['id']} already initialized"}), 409

    db.rooms.insert_one(data)
    return jsonify({"message": f"Room with ID {data['id']} initialized successfully"}), 201

# Endpoint for updating mutable data
@app.route('/update', methods=['POST'])
def update_room():
    """Update mutable fields for the room"""
    data = request.json
    mutable_fields = ["status", "temperature", "humidity", "devices", "bottles", "measurements"]

    updates = {key: data[key] for key in data if key in mutable_fields}
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    result = db.rooms.update_one({}, {"$set": updates})  # Update the first (and only) room
    if result.matched_count == 0:
        return jsonify({"error": "Room not found"}), 404

    return jsonify({"message": "Room updated successfully"}), 200

# Endpoint for retrieving room data
@app.route('/room', methods=['GET'])
def get_room():
    """Retrieve the room data"""
    room = db.rooms.find_one()
    if not room:
        return jsonify({"error": "Room not initialized"}), 404

    room["_id"] = str(room["_id"])  # Convert MongoDB ObjectId to string
    return jsonify(room)

if __name__ == '__main__':
    port = int(os.getenv("FLASK_RUN_PORT", 5000))  # Default to 5000
    app.run(host='0.0.0.0', port=port)
