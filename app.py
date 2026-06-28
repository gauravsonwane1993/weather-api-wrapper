from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


@app.route("/")
def home():
    api_key_configured = bool(WEATHER_API_KEY and WEATHER_API_KEY != "your_api_key_here")

    return jsonify({
        "message": "Weather API Wrapper is running",
        "weatherApiKeyConfigured": api_key_configured,
        "try": "/api/weather?city=Amsterdam"
    })


@app.route("/api/weather")
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