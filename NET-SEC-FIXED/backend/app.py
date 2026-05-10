"""
NET-SEC Flask Backend
─────────────────────
Fixes applied vs original:
  • CORS restricted to allowed origins (not wildcard in production)
  • OTP is no longer returned in the API response
  • Input validation and length caps on all fields
  • Security headers added (X-Content-Type-Options, X-Frame-Options, etc.)
  • debug=False enforced in production path
  • Proper HTTP status codes on all paths
"""

import os
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from otp_service import generate_otp, verify_otp

# ─── App setup ────────────────────────────────────────────────────────────────

app = Flask(__name__)

# Restrict CORS to your actual frontend origin in production.
# Change this list when deploying; "*" is fine only for local dev.
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", "http://localhost:5000,http://127.0.0.1:5000"
).split(",")

CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=False)

FRONTEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# ─── Security headers (applied to every response) ─────────────────────────────

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"]        = "DENY"
    response.headers["Referrer-Policy"]         = "no-referrer"
    response.headers["Cache-Control"]           = "no-store"
    return response

# ─── Validation helpers ───────────────────────────────────────────────────────

# Only alphanumeric + underscore/hyphen, 1–64 chars
_USER_ID_RE = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")

def _valid_user_id(uid: str) -> bool:
    return bool(uid and _USER_ID_RE.match(uid))

def _valid_otp(otp: str) -> bool:
    return bool(otp and otp.isdigit() and 4 <= len(otp) <= 8)

# ─── Static frontend ──────────────────────────────────────────────────────────

@app.route("/")
def serve_ui():
    return send_from_directory(FRONTEND_PATH, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_PATH, path)

# ─── API: Generate OTP ────────────────────────────────────────────────────────

@app.route("/generate-otp", methods=["POST"])
def generate_otp_api():
    data = request.get_json(silent=True)

    if not data or "user_id" not in data:
        return jsonify({"error": "user_id is required"}), 400

    user_id = str(data["user_id"]).strip()

    if not _valid_user_id(user_id):
        return jsonify({"error": "Invalid user_id format"}), 400

    result = generate_otp(user_id)

    if not result["ok"]:
        # Rate-limit → 429, anything else → 400
        status = 429 if "Rate limit" in result.get("message", "") else 400
        return jsonify({"error": result["message"]}), status

    # ⚠ IMPORTANT: OTP is intentionally NOT returned here.
    # In a real system, deliver it via SMS / email / push notification.
    # For demo purposes the OTP is printed to the *server* console only.
    return jsonify({"message": "OTP generated. Check your registered channel."}), 200

# ─── API: Verify OTP ─────────────────────────────────────────────────────────

@app.route("/verify-otp", methods=["POST"])
def verify_otp_api():
    data = request.get_json(silent=True)

    if not data or "user_id" not in data or "otp" not in data:
        return jsonify({"error": "user_id and otp are required"}), 400

    user_id  = str(data["user_id"]).strip()
    user_otp = str(data["otp"]).strip()

    if not _valid_user_id(user_id):
        return jsonify({"error": "Invalid user_id format"}), 400

    if not _valid_otp(user_otp):
        return jsonify({"error": "OTP must be 4–8 digits"}), 400

    result = verify_otp(user_id, user_otp)

    if result["status"]:
        return jsonify({"message": result["message"]}), 200

    # Map specific failures to appropriate HTTP codes
    msg = result["message"]
    if "expired" in msg.lower():
        return jsonify({"error": msg}), 410   # Gone
    if "attempts" in msg.lower():
        return jsonify({"error": msg}), 429   # Too Many Requests
    return jsonify({"error": msg}), 401       # Unauthorized

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="127.0.0.1", port=5000, debug=debug_mode)
