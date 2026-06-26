"""SMB Automation Health Dashboard — Flask web app."""

import os
import yaml
from datetime import datetime
from flask import Flask, render_template, jsonify

from checks.runner import run_checks_sync

app = Flask(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "clients.yaml")


def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


@app.route("/")
def dashboard():
    config = load_config()
    return render_template("dashboard.html", clients=config.get("clients", []))


@app.route("/api/health")
def api_health():
    config = load_config()
    results = run_checks_sync(config)
    return jsonify(results)


@app.route("/api/health/<client_slug>")
def api_health_client(client_slug):
    config = load_config()
    all_results = run_checks_sync(config)
    filtered = [r for r in all_results if r["client"].lower().replace(" ", "-") == client_slug]
    return jsonify(filtered)


@app.route("/status")
def status_page():
    config = load_config()
    results = run_checks_sync(config)
    clients_data = {}
    for r in results:
        clients_data.setdefault(r["client"], []).append(r)
    return render_template("status.html", clients_data=clients_data, now=datetime.now)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"  SMB Automation Health Dashboard")
    print(f"  Config: {CONFIG_PATH}")
    print(f"  Server: http://localhost:{port}")
    print(f"  Dashboard: http://localhost:{port}/status")
    app.run(debug=True, host="0.0.0.0", port=port)
