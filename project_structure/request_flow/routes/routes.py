from flask import Blueprint, jsonify
from ..config import database
from google.cloud import firestore

test_bp = Blueprint('test_bp', __name__)

@test_bp.route('/test-firestore', methods=['GET'])
def test_firestore():
    try:
        test_doc = {
            "message": "Hello from Firestore!",
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        database.collection("test_collection").add(test_doc)
        return jsonify({"success": True, "message": "Firestore write successful!"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
