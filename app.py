from flask import Flask, render_template, request, jsonify
import json
import os
import urllib.request
import urllib.parse

app = Flask(__name__)

# Use Environment Variables or a defaults file if env var is missing
# In Vercel, file system is read-only (except /tmp), so we cannot persist config changes to a file.
# Configuration must be done via Environment Variables or hardcoded.

DEFAULT_CONFIG = {
    "title": "Location Check-in",
    "gas_url": os.environ.get("GAS_URL", ""),
    "fields": [
        {"id": "name", "type": "text", "label": "Name", "required": True},
        {"id": "phone", "type": "tel", "label": "Phone Number", "required": True},
        {"id": "notes", "type": "textarea", "label": "Additional Notes", "required": False}
    ]
}

def load_config():
    # Attempt to load from JSON string in env var, fallback to default
    env_config = os.environ.get("APP_CONFIG")
    if env_config:
        try:
            return json.loads(env_config)
        except:
            pass
    return DEFAULT_CONFIG

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    # Admin page is now read-only or instructions to use Env Vars
    return render_template('admin.html', read_only=True)

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    if request.method == 'GET':
        return jsonify(load_config())
    else:
        # On Vercel, we can't save to file. 
        return jsonify({"status": "error", "message": "Configuration updates on Vercel must be done via Environment Variables."}), 403

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.json
    config = load_config()
    gas_url = config.get('gas_url')
    
    if not gas_url:
        return jsonify({"status": "error", "message": "Google Script URL not configured"}), 400

    try:
        # Prepare data for GAS
        payload = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(gas_url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            return jsonify({"status": "success", "gas_response": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Vercel requires the app object to be available as 'app'
# No 'if __name__ == "__main__":' block needed for Vercel, but useful for local testing
if __name__ == '__main__':
    app.run(debug=True, port=3000)
