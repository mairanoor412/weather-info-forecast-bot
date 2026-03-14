import os
from datetime import datetime, timedelta

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

load_dotenv()

app = FastAPI()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def build_dialogflow_response(text: str) -> dict:
    return {"fulfillmentText": text}


async def get_current_weather(city: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            CURRENT_WEATHER_URL,
            params={"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"},
        )

    if response.status_code != 200:
        return f"Sorry, I couldn't find weather data for {city}."

    data = response.json()
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    description = data["weather"][0]["description"]

    return (
        f"The current weather for {city} is {description} "
        f"with a temperature of {temp}°C (feels like {feels_like}°C) "
        f"and humidity at {humidity}%."
    )


async def get_forecast_weather(city: str, date: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                FORECAST_URL,
                params={"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric", "cnt": 40},
            )

        print(f"OpenWeather API status: {response.status_code}")

        if response.status_code != 200:
            return f"Sorry, I couldn't find forecast data for {city}."

        data = response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return f"Sorry, there was an error fetching forecast data for {city}."

    try:
        start_date = datetime.strptime(date[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        start_date = datetime.now().date()

    print(f"Start date: {start_date}")

    end_date = start_date + timedelta(days=8)

    # Group forecasts by date and pick one per day (around noon)
    daily_forecasts = {}
    for item in data["list"]:
        forecast_dt = datetime.fromtimestamp(item["dt"]).date()
        if start_date <= forecast_dt <= end_date:
            forecast_hour = datetime.fromtimestamp(item["dt"]).hour
            # Pick the entry closest to noon (12:00) for each day
            if forecast_dt not in daily_forecasts or abs(forecast_hour - 12) < abs(daily_forecasts[forecast_dt]["hour"] - 12):
                daily_forecasts[forecast_dt] = {
                    "hour": forecast_hour,
                    "temp": item["main"]["temp"],
                    "description": item["weather"][0]["description"],
                }

    if not daily_forecasts:
        return f"No forecast data available for {city} from {start_date} to {end_date}."

    forecasts = []
    for dt in sorted(daily_forecasts.keys()):
        info = daily_forecasts[dt]
        forecasts.append(f"{dt}: {info['temp']}°C, {info['description']}")

    forecast_text = "\n".join(forecasts)
    return (
        f"The forecasted weather from {start_date} to {end_date} "
        f"for {city} is:\n{forecast_text}"
    )


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()

    intent_name = body.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = body.get("queryResult", {}).get("parameters", {})
    output_contexts = body.get("queryResult", {}).get("outputContexts", [])

    # Log for debugging
    print(f"Intent: {intent_name}")
    print(f"Parameters: {parameters}")

    # Check parameters from contexts as well (follow-up intents)
    city = parameters.get("geo-city", "") or parameters.get("city", "")
    date = parameters.get("date", "")

    # Handle date-period (Dialogflow sends startDate/endDate object)
    date_period = parameters.get("date-period", "")
    if not date and date_period:
        if isinstance(date_period, dict):
            date = date_period.get("startDate", "")
        elif isinstance(date_period, str):
            date = date_period

    if not city:
        for ctx in output_contexts:
            ctx_params = ctx.get("parameters", {})
            city = ctx_params.get("geo-city", "") or ctx_params.get("geo-city.original", "") or ctx_params.get("city", "")
            if city:
                break

    if not date:
        for ctx in output_contexts:
            ctx_params = ctx.get("parameters", {})
            date = ctx_params.get("date", "") or ctx_params.get("date.original", "")
            if not date:
                dp = ctx_params.get("date-period", "")
                if isinstance(dp, dict):
                    date = dp.get("startDate", "")
            if date:
                break

    if "current" in intent_name.lower() or "weather" in intent_name.lower() and "forecast" not in intent_name.lower():
        if not city:
            return JSONResponse(content=build_dialogflow_response("Please provide your city."))
        result = await get_current_weather(city)
        return JSONResponse(content=build_dialogflow_response(result))

    elif "forecast" in intent_name.lower():
        if not city:
            return JSONResponse(content=build_dialogflow_response("Please provide your city."))
        result = await get_forecast_weather(city, date)
        return JSONResponse(content=build_dialogflow_response(result))

    return JSONResponse(content=build_dialogflow_response("I'm not sure how to help with that."))


@app.get("/")
async def root():
    return {"message": "Weather Bot Webhook is running!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
