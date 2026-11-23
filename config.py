import os

SECRET_KEY = "campushub-super-secret-key-1234567890"

API_KEY = "CH-API-KEY-do-not-hardcode-me-abcdef123456"

DB_PATH = os.environ.get("CAMPUSHUB_DB", os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "campushub.db"))

UPLOAD_DIR = os.environ.get("CAMPUSHUB_UPLOADS", os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "uploads"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

HOST = os.environ.get("CAMPUSHUB_HOST", "127.0.0.1")
PORT = int(os.environ.get("CAMPUSHUB_PORT", "5000"))

DEBUG = os.environ.get("CAMPUSHUB_DEBUG", "1") == "1"
