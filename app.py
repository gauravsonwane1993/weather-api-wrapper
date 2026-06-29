from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests
import redis
import json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

app = Flask(__name__)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379",
    headers_enabled=True
)

CACHE_EXPIRY_SECONDS = 60 * 60 * 2


def is_redis_connected():
    try:
        return redis_client.ping()
    except redis.RedisError:
        return False


@app.route("/")
def home():
    api_key_configured = bool(WEATHER_API_KEY and WEATHER_API_KEY != "your_api_key_here")

    return jsonify({
        "message": "Weather API Wrapper is running",
        "weatherApiKeyConfigured": api_key_configured,
        "redisConnected": is_redis_connected(),
        "rateLimiting": "enabled",
        "defaultLimits": ["200 per day", "50 per hour"],
        "weatherEndpointLimit": "10 per minute",
        "try": "/api/weather?city=Amsterdam"
    })

@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({
        "error": "Rate limit exceeded",
        "message": str(error.description)
    }), 429

@app.route("/api/weather")
@limiter.limit("10 per minute")
def get_weather():
    city = request.args.get("city")

    if not city:
        return jsonify({
            "error": "City is required. Example: /api/weather?city=Amsterdam"
        }), 400

    if not WEATHER_API_KEY:
        return jsonify({
            "error": "Weather API key is missing"
        }), 500

    cache_key = f"weather:{city.lower()}"

    try:
        cached_data = redis_client.get(cache_key)

        if cached_data:
            result = json.loads(cached_data)
            result["cached"] = True
            return jsonify(result)

    except redis.RedisError:
        pass

    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}"

    params = {
        "key": WEATHER_API_KEY,
        "unitGroup": "metric",
        "include": "current",
        "contentType": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 400:
            return jsonify({
                "error": "Invalid city or location not found"
            }), 400

        if response.status_code == 401:
            return jsonify({
                "error": "Invalid or unauthorized weather API key"
            }), 401

        response.raise_for_status()

        data = response.json()
        current = data.get("currentConditions", {})

        result = {
            "city": data.get("resolvedAddress", city),
            "temperature": current.get("temp"),
            "condition": current.get("conditions"),
            "humidity": current.get("humidity"),
            "windSpeed": current.get("windspeed"),
            "cached": False,
            "source": "visual-crossing"
        }

        try:
            redis_client.set(
                cache_key,
                json.dumps(result),
                ex=CACHE_EXPIRY_SECONDS
            )
        except redis.RedisError:
            pass

        return jsonify(result)

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Weather API request timed out"
        }), 504

    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Failed to fetch weather data from external weather API"
        }), 502


if __name__ == "__main__":
    app.run(debug=True)