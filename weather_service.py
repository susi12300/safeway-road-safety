import requests


# =====================================================
# GET WEATHER FOR ONE LOCATION
# =====================================================

def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    parameters = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code",
        "timezone": "auto"
    }

    try:

        response = requests.get(
            url,
            params=parameters,
            timeout=10
        )

        # If Open-Meteo temporarily rate-limits us
        if response.status_code == 429:

            print("Open-Meteo rate limit reached. Using fallback weather.")

            return {
                "temperature": 25,
                "weather": "clear"
            }

        response.raise_for_status()

        data = response.json()

        if isinstance(data, list):
            data = data[0]

        temperature = data["current"]["temperature_2m"]
        weather_code = data["current"]["weather_code"]

        if weather_code in [0, 1, 2, 3]:
            weather = "clear"

        elif weather_code in [45, 48]:
            weather = "fog"

        elif weather_code in [
            51, 53, 55,
            56, 57,
            61, 63, 65,
            66, 67,
            80, 81, 82
        ]:
            weather = "rain"

        elif weather_code in [
            71, 73, 75,
            77,
            85, 86
        ]:
            weather = "snow"

        elif weather_code in [95, 96, 99]:
            weather = "storm"

        else:
            weather = "clear"

        return {
            "temperature": temperature,
            "weather": weather
        }

    except Exception as e:

        print("Weather API error:", e)

        # Keep route prediction working even if
        # the weather service is temporarily unavailable
        return {
            "temperature": 25,
            "weather": "clear"
        }
# =====================================================
# GET WEATHER FOR ROUTE POINTS
# =====================================================

def get_route_weather(route_points):

    weather_results = []

    # -------------------------------------------------
    # SAMPLE ONLY 5 POINTS FROM THE ROUTE
    # -------------------------------------------------

    if not route_points:
        return weather_results

    number_of_points = len(route_points)

    sample_indexes = [
        0,
        number_of_points // 4,
        number_of_points // 2,
        (3 * number_of_points) // 4,
        number_of_points - 1
    ]

    # Remove duplicates
    sample_indexes = list(dict.fromkeys(sample_indexes))

    # -------------------------------------------------
    # GET WEATHER FOR SELECTED POINTS
    # -------------------------------------------------

    for index in sample_indexes:

        point = route_points[index]

        # ORS coordinates:
        # [longitude, latitude]

        longitude = point[0]
        latitude = point[1]

        print(
            "Checking weather:",
            latitude,
            longitude
        )

        weather_data = get_weather(
            latitude,
            longitude
        )

        weather_results.append({

            "latitude":
                latitude,

            "longitude":
                longitude,

            "temperature":
                weather_data["temperature"],

            "weather":
                weather_data["weather"]

        })

    return weather_results
# =====================================================
# GET OVERALL ROUTE WEATHER
# =====================================================

def get_overall_route_weather(route_points):

    weather_results = get_route_weather(

        route_points

    )


    if not weather_results:

        return {

            "overall_weather":
                "clear",

            "average_temperature":
                0

        }


    # -----------------------------------------
    # TEMPERATURE
    # -----------------------------------------

    temperatures = [

        item["temperature"]

        for item in weather_results

    ]


    average_temperature = round(

        sum(temperatures)
        /
        len(temperatures),

        2

    )


    # -----------------------------------------
    # WEATHER
    # -----------------------------------------

    weather_list = [

        item["weather"]

        for item in weather_results

    ]


    # Give priority to dangerous weather

    if "storm" in weather_list:

        overall_weather = "storm"

    elif "snow" in weather_list:

        overall_weather = "snow"

    elif "rain" in weather_list:

        overall_weather = "rain"

    elif "fog" in weather_list:

        overall_weather = "fog"

    else:

        overall_weather = "clear"


    return {

        "overall_weather":
            overall_weather,

        "average_temperature":
            average_temperature

    }