# Weather API Wrapper Service

Project Reference: https://roadmap.sh/projects/weather-api-wrapper-service

A backend Weather API Wrapper Service built with **Python**, **Flask**, **Redis**, and **Visual Crossing Weather API**.

A backend Weather API Wrapper Service built with **Python**, **Flask**, **Redis**, and **Visual Crossing Weather API**.

This project accepts a city name, fetches current weather data from an external weather API, caches the response using Redis, and applies rate limiting to protect the API from excessive requests.

## Features

* Flask backend API
* Current weather lookup by city
* Visual Crossing Weather API integration
* API key stored securely using `.env`
* Redis caching with 2-hour expiry
* Rate limiting using Flask-Limiter
* Redis-backed rate limit storage
* Clean JSON responses
* JSON error response for rate-limit violations
* Git-based project versioning

## Tech Stack

* Python
* Flask
* Requests
* python-dotenv
* Redis
* Docker
* Flask-Limiter
* Git

## Project Structure

```text
weather-api-wrapper/
├── .venv/
├── .env
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
```

## API Endpoints

### Health/Home Endpoint

```http
GET /
```

Example response:

```json
{
  "defaultLimits": [
    "200 per day",
    "50 per hour"
  ],
  "message": "Weather API Wrapper is running",
  "rateLimiting": "enabled",
  "redisConnected": true,
  "try": "/api/weather?city=Amsterdam",
  "weatherApiKeyConfigured": true,
  "weatherEndpointLimit": "10 per minute"
}
```

### Weather Endpoint

```http
GET /api/weather?city=Amsterdam
```

Example response:

```json
{
  "cached": false,
  "city": "Amsterdam",
  "condition": "Partially cloudy",
  "humidity": 47.2,
  "source": "visual-crossing",
  "temperature": 19.3,
  "windSpeed": 2.8
}
```

When the same city is requested again before the cache expires, the response may show:

```json
{
  "cached": true,
  "city": "Amsterdam",
  "condition": "Partially cloudy",
  "humidity": 47.2,
  "source": "visual-crossing",
  "temperature": 19.3,
  "windSpeed": 2.8
}
```

## Rate Limiting

The API uses Flask-Limiter.

Default limits:

```text
200 requests per day
50 requests per hour
```

Weather endpoint limit:

```text
10 requests per minute
```

If the limit is exceeded, the API returns:

```json
{
  "error": "Rate limit exceeded",
  "message": "10 per 1 minute"
}
```

## Redis Caching

Weather responses are cached in Redis for 2 hours.

Cache key format:

```text
weather:<city>
```

Example:

```text
weather:amsterdam
```

Cache expiry:

```text
7200 seconds
```

## Setup Instructions

### 1. Clone the repository

```powershell
git clone <your-repository-url>
cd weather-api-wrapper
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

On Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Create a `.env` file

Create a file named `.env` in the project root.

Add your Visual Crossing API key:

```env
WEATHER_API_KEY=your_real_api_key_here
```

Do not commit `.env` to GitHub.

### 6. Start Redis using Docker

```powershell
docker run --name weather-redis -p 6379:6379 -d redis
```

Check if Redis is running:

```powershell
docker ps
```

Test Redis:

```powershell
docker exec -it weather-redis redis-cli ping
```

Expected response:

```text
PONG
```

### 7. Run the Flask app

```powershell
python app.py
```

The app should run at:

```text
http://127.0.0.1:5000
```

## Testing the API

Open this URL in a browser:

```text
http://127.0.0.1:5000/api/weather?city=Amsterdam
```

To test caching, refresh the same URL twice.

First request:

```json
"cached": false
```

Second request:

```json
"cached": true
```

To check Redis cache keys:

```powershell
docker exec -it weather-redis redis-cli keys "weather:*"
```

To check cache expiry:

```powershell
docker exec -it weather-redis redis-cli ttl weather:amsterdam
```

## Git Milestones

### Milestone 1

```text
Initial Flask weather API
```

Implemented:

* Flask app setup
* `/` endpoint
* `/api/weather` endpoint
* Visual Crossing API integration
* `.env` API key handling
* Basic error handling

### Milestone 2

```text
Add Redis caching for weather responses
```

Implemented:

* Redis Docker container
* Python Redis client
* Redis connection check
* Weather response caching
* 2-hour cache expiry
* Cached response indicator

### Milestone 3

```text
Add rate limiting for weather endpoint
```

Implemented:

* Flask-Limiter
* Redis-backed rate-limit storage
* Default limits
* Weather endpoint-specific limit
* JSON response for 429 Too Many Requests

## Security Notes

The `.env` file is ignored by Git and should never be uploaded to GitHub.

The `.gitignore` file should include:

```text
.venv/
.env
__pycache__/
*.pyc
```

## Current Status

Completed:

* Flask backend API
* External weather API integration
* Environment variable handling
* Redis caching
* Rate limiting
* Git commits for major milestones

Next possible improvements:

* Deploy the API
* Add Swagger/OpenAPI documentation
* Add Docker Compose
* Add frontend UI
* Add unit tests
