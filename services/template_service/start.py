# services/user_service/start.py
import os, time, subprocess, sys

def run(cmd):
    print(">>", " ".join(cmd))
    return subprocess.call(cmd)

def ensure_migrations():
    if not os.path.exists("migrations"):
        print("📦 migrations/ not found, initializing…")
        # If app import fails, this will show the traceback
        if run(["flask", "db", "init"]) != 0:
            print("❌ flask db init failed"); sys.exit(1)
        # generate first migration from models
        run(["flask", "db", "migrate", "-m", "init"])

def wait_and_upgrade():
    for _ in range(40):  # ~2 minutes of retries
        code = run(["flask", "db", "upgrade"])
        if code == 0:
            print("✅ migrations applied")
            return
        print("⏳ DB not ready or migration failed, retrying in 3s…")
        time.sleep(3)
    print("❌ failed to run migrations after retries")
    sys.exit(1)

if __name__ == "__main__":
    os.environ.setdefault("FLASK_APP", "wsgi.py")
    ensure_migrations()
    wait_and_upgrade()
    os.execvp("gunicorn", ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "wsgi:app"])
