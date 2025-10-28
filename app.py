from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from cachetools import TTLCache
from time import time
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
CORS(app)

limiter = Limiter(app, key_func=get_remote_address, default_limits=["100 per hour"])
cache = TTLCache(maxsize=1000, ttl=300)

OCEANA_MW_KEY = os.getenv("OCEANA_MW_KEY", "test123")  # Render secret later

def fetch_noaa_sst(lat, lon):
    return {"sst": 28.9, "timestamp": int(time()), "source": "DEMO/NOAA"}

def ethical_masking(result):
    try:
        if 'lat' in result and 'lon' in result:
            result['lat'] = round(float(result['lat']), 3)
            result['lon'] = round(float(result['lon']), 3)
    except Exception:
        pass
    return result

@app.route("/v1/ocean/point", methods=["GET"])
@limiter.limit("60 per minute")
def ocean_point():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        abort(401, description="Missing Authorization header")
    token = auth.split(" ", 1)[1]
    if token != OCEANA_MW_KEY:
        abort(403, description="Invalid token")

    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"error": "lat and lon required"}), 400

    cache_key = f"{lat}:{lon}"
    if cache_key in cache:
        data = cache[cache_key]
        data['cached'] = True
        return jsonify(data)

    sst_data = fetch_noaa_sst(lat, lon)
    result = {
        "lat": lat,
        "lon": lon,
        "sst": sst_data['sst'],
        "timestamp": sst_data['timestamp'],
        "source": sst_data['source'],
        "note": "For official alerts, consult IMD/INCOIS/NOAA."
    }
    result = ethical_masking(result)
    cache[cache_key] = result
    result['cached'] = False
    return jsonify(result)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": int(time())})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
