# Weather Info & Forecast Bot

A weather chatbot webhook built with **FastAPI**, **Dialogflow ES**, and **OpenWeather API** that provides current weather and forecast information for any city.

## Architecture Diagram

```
Dialogflow ES  <------>  Webhook (FastAPI)  <------>  OpenWeather API
```

## Features

- **Current Weather:** Get real-time weather information (temperature, humidity, description) for any city.
- **Weather Forecast:** Get forecasted weather for up to 8 days from a specific date for any city.
- **Conversational Flow:** Natural language interaction through Dialogflow ES.

## Conversational Flow

```
User: "Hi"
Bot:  "This is weather BOT. How may I help you?"

User: "What is the current weather?"
Bot:  "Please provide your city."

User: "Karachi"
Bot:  "The current weather for Karachi is clear sky with a temperature of 29°C..."

User: "Please tell me the weather forecast from tomorrow for Lahore"
Bot:  "The forecasted weather from 2026-03-15 to 2026-03-23 for Lahore is:..."

User: "Thanks"
Bot:  "Is there anything else I can help you with?"

User: "No thanks"
Bot:  "Thank you for contacting. Goodbye!"
```

## Tech Stack

- **Chatbot Engine:** Google Dialogflow ES
- **Backend:** Python (FastAPI)
- **Weather Data:** OpenWeather API
- **Tunnel:** ngrok (for exposing local server)

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/weather-info-forecast-bot.git
cd weather-info-forecast-bot
```

### 2. Create virtual environment and install dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root directory:

```
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

Get your free API key from [openweathermap.org](https://openweathermap.org/api).

### 4. Start the server

```bash
python main.py
```

Server will start at `http://localhost:8000`.

### 5. Expose with ngrok

```bash
ngrok http 8000
```

Copy the public URL and set it as the webhook URL in Dialogflow ES:

```
https://your-ngrok-url.ngrok-free.dev/webhook
```

## API Endpoints

| Method | Endpoint   | Description                          |
|--------|------------|--------------------------------------|
| GET    | `/`        | Health check                         |
| POST   | `/webhook` | Dialogflow webhook fulfillment endpoint |

## Dialogflow ES Setup

### Intents

1. **Default Welcome Intent** - Greeting responses
2. **get.current.weather** - Asks user for city
3. **get.current.weather - city** - Fetches current weather (webhook enabled)
4. **get.forecast.weather** - Fetches weather forecast (webhook enabled)
5. **thanks** - Thank you response
6. **goodbye** - Goodbye response

### Fulfillment

- Enable **Webhook** in Fulfillment section
- Set URL to your ngrok public URL + `/webhook`

## Project Structure

```
weather-info-forecast-bot/
├── main.py              # FastAPI webhook endpoint
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore file
└── README.md            # Project documentation
```
